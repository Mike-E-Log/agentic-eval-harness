"""The orchestration loop: drive a project through the phases, gating each boundary.

This is the glue that connects the individually-tested components
(`next_phase` -> `create_worktree` -> `run_phase` -> `run_gate` -> render ->
persist -> manual-approve) into a working run. The gate is **decision-support,
not an automated verdict**: it never blocks on its own. The only thing that
advances or halts a run is the human `approve` callback at each boundary.

    next_phase ──> run_phase (claude --print, in the worktree)
                      │ gated (artifact written)
                      ▼
                   run_gate (cross-vendor panel scores artifact vs exemplar)
                      │
                      ▼
                   render + persist last_gate ──> approve(phase, gate)?
                      │ True                         │ False
                      ▼                              ▼
                   next_phase                      stop (state kept)
"""
from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from aeh.eval_gate.gate import run_gate
from aeh.orchestrator import next_phase
from aeh.phase_runner import run_phase
from aeh.renderer import render_gate
from aeh.state_store import StateStore
from aeh.worktree_manager import create_worktree

# Each phase produces exactly one gateable artifact (path relative to the
# worktree root). The phase prompts in prompts/<phase>.md instruct `claude` to
# write these files; run_phase verifies the file exists and is non-empty.
ARTIFACTS = {
    "ideate": "docs/IDEATE.md",
    "spec": "docs/SPEC.md",
    "plan": "docs/PLAN.md",
    "implement": "docs/IMPLEMENT.md",
    "review": "docs/REVIEW.md",
}

DEFAULT_TIMEOUT = 600


def _prompts_dir() -> Path:
    # packaged under aeh/_data/prompts; fall back to the repo prompts/ for
    # editable installs (mirrors demo.fixture_path's packaged-or-repo pattern).
    try:
        p = files("aeh").joinpath("_data/prompts")
        if p.is_dir():
            return Path(str(p))
    except (ModuleNotFoundError, FileNotFoundError):
        pass
    return Path(__file__).resolve().parents[2] / "prompts"


def load_phase(phase: str) -> tuple[str, str, str, str]:
    """Return (prompt_text, exemplar_text, criterion, artifact_relpath)."""
    d = _prompts_dir()
    prompt = (d / f"{phase}.md").read_text(encoding="utf-8")
    exemplar = (d / f"{phase}.exemplar.md").read_text(encoding="utf-8")
    criterion = json.loads((d / "criteria.json").read_text(encoding="utf-8"))[phase]
    return prompt, exemplar, criterion, ARTIFACTS[phase]


def drive(project, run_id, *, judges, approve, timeout=DEFAULT_TIMEOUT, emit=print) -> dict:
    """Drive a project through the phases, gating each boundary.

    judges:  list of judge names to run at each gate (e.g. ["claude", "gpt"]).
             Empty list -> the gate runs but reports no scores (keyless).
    approve: callable(phase: str, gate: GateResult) -> bool. Called after each
             gate; return False to halt (state is preserved for `aeh resume`).
    emit:    sink for human-facing output (gate scorecards, phase notices).

    Returns the final persisted state dict. Never raises on a failed phase —
    it records status="failed" and returns so the caller can report cleanly.
    """
    project = Path(project)
    store = StateStore(project, run_id)
    worktree = create_worktree(project, run_id)
    log_dir = project / ".aeh" / "runs" / run_id / "logs"

    state = {"project": str(project), "phase": None, "status": "running",
             "worktree": str(worktree)}
    store.write(state)

    phase = next_phase(None)
    while phase is not None:
        prompt, exemplar, criterion, artifact_rel = load_phase(phase)
        artifact = worktree / artifact_rel
        result = run_phase(cwd=worktree, prompt=prompt, expected_artifact=artifact,
                           log_dir=log_dir, timeout=timeout, json_mode=False)
        if result.status == "failed":
            state = {**state, "phase": phase, "status": "failed", "reason": result.reason}
            store.write(state)
            emit(f"phase '{phase}' failed: {result.reason}")
            return state

        candidate = artifact.read_text(encoding="utf-8")
        gate = run_gate(phase=phase, candidate=candidate, exemplar=exemplar,
                        exemplar_ref=f"prompts/{phase}.exemplar.md",
                        criterion=criterion, judges=judges)
        emit(render_gate(gate))
        state = {**state, "phase": phase, "status": "gated", "last_gate": gate.to_dict()}
        store.write(state)

        if not approve(phase, gate):
            return state
        phase = next_phase(phase)

    state = {**state, "status": "completed"}
    store.write(state)
    return state

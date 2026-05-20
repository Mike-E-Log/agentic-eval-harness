from __future__ import annotations

from aeh.models import PHASES


def next_phase(current: str | None) -> str | None:
    if current is None:
        return PHASES[0]
    i = PHASES.index(current)
    return PHASES[i + 1] if i + 1 < len(PHASES) else None


def resume_action(state: dict) -> str:
    status = state.get("status")
    return {"gated": "reprompt", "running": "rerun",
            "failed": "rerun", "completed": "noop"}.get(status, "rerun")


def extract_result(envelope: dict) -> str:
    # tolerant across `claude --output-format json` envelope shapes
    for k in ("result", "text", "content"):
        if isinstance(envelope.get(k), str):
            return envelope[k]
    raise ValueError("unrecognized claude --output-format json envelope shape")

# SPEC — agentic-eval-harness

> Part of an AI-evaluation engineering portfolio — overview at https://mikeilog.com

## Purpose

A CLI that drives Claude Code through a fixed phase sequence (ideate → spec → plan → implement → review) with a **cross-vendor decision-support eval gate** at each phase boundary. v0.1 = Phase 1 (single-agent runner + manual approval) + Phase 2 (the eval gate). The gate surfaces multi-vendor scores, disagreement, and critiques to inform the operator's manual approve/reject — it does not auto-decide. Doubles as an R&D platform for long-horizon autonomous-agent work.

## Positioning (one paragraph)

agentic-eval-harness drives a coding agent through phases and, at each boundary, runs an independent cross-vendor panel that scores the phase output against a known-good exemplar and surfaces per-judge scores, disagreement, and critiques to the operator. The gate is honest **decision-support, not an automated verdict**: it does not pretend an uncalibrated multi-LLM vote is a trustworthy classifier. The disciplined path to automation is explicit — log the operator's approve/reject decisions, then calibrate the gate against them (the v0.2 re-entry point for `ai-eval-toolkit`'s judge-human calibration). The signal: this applies real eval methodology to the coding-agent ecosystem and is honest about what its gate does and doesn't know.

## Orchestration architecture

```
┌──────────────────────────────────────────────────────────┐
│                  agentic-eval-harness CLI                  │
│   aeh run <project> · resume <id> · status <id>            │
│   show <id> · cleanup <id> · demo                          │
└───────────────────────────┬────────────────────────────────┘
                            ▼
              ┌──────────────────────────┐
              │     Run Orchestrator      │
              │  - session lifecycle      │
              │  - reads/writes state     │
              │  - dispatches to phase    │
              └───────┬──────────┬────────┘
                      │          │
         ┌────────────┘          └──────────────┐
         ▼                                       ▼
┌──────────────────┐                  ┌────────────────────┐
│   Phase Runner   │                  │  Eval Gate          │
│  drives `claude  │                  │  (decision-support) │
│  --print` through│ ──phase output──▶│  imports VENDORED   │
│  the 5 phases    │                  │  eval_gate/judging  │
│  (hardened       │                  │  → scores artifact  │
│   subprocess)    │                  │  vs exemplar;       │
└──────────────────┘                  │  surfaces scores +  │
         │                            │  dispersion +       │
         ▼                            │  critiques to user  │
┌──────────────────┐                  └────────────────────┘
│ Worktree Manager │
│ (1 isolated      │   No toolkit/MCP dependency at v0.1.
│  worktree/run)   │   Scoring logic is vendored in-repo.
└──────────────────┘
```

## Scoring mechanism (vendored, decoupled)

The eval gate's multi-vendor scoring lives **inside the harness repo** at `eval_gate/judging.py` — a clean, importable adaptation of a `cross-vendor-judges` `judge.py` core (parallel Claude/GPT/Gemini calls, per-judge scoring, agreement/dispersion), written without import-time side effects so the gate imports it directly. An attribution header names `cross-vendor-judges` as the origin and notes it is a snapshot, not a live dependency.

- **Self-contained + distributable:** anyone cloning the repo can run the gate with their own API keys; nothing points at a private skills directory.
- **Reference-exemplar comparison:** the gate scores `[phase_output, known-good_exemplar]` against a per-phase criterion (the judge's native comparative mode). Surfaces the phase output's per-judge scores, the per-judge critiques, and cross-vendor dispersion. **Never surfaces a winner/verdict token.**
- **N=2 caveat (documented):** with two candidates, Kendall-τ is undefined; the gate reports the directional agreement fraction instead. Stated plainly in the README — an eval reviewer will check.
- **Parity test** against known `judge.py` output guards the snapshot from silent drift.
- **Dogfooding narrative:** "the gate shares its scoring logic with my cross-vendor-judges daily-driver, which I used to make real decisions."

## Eval gate = decision-support (not a verdict)

At each `running → gated` boundary, the gate produces:
`{phase, scores: {judge: number}, dispersion: number, critiques: {judge: string}[], exemplar_ref}` — and **no** `recommendation`/`ceiling_fired`/`halt` token. The operator reads the evidence and decides. The README states: "the gate is decision-support; the scores are heuristics shown to the operator, not a validated classifier."

## `claude --print` driver (the #1 real risk — harden it)

The Phase Runner drives Claude Code via `claude --print` subprocess. Required v0.1 robustness:
1. `subprocess.run(..., timeout=N)` (default 30 min/phase) → `TimeoutExpired` → `failed` state with captured partial stdout/stderr.
2. Check `returncode`; capture both streams to `.aeh/runs/<id>/<phase>.log`.
3. **Validate the phase produced its expected artifact** (e.g., spec phase must write `docs/SPEC.md`); missing → `failed`, never silently advance to the gate.
4. Log `claude --version` into state at run start for diagnosability.
5. Use `--output-format json` if the installed CLI supports it (verify, don't assume); else parse defensively.

## State machine (minimal — cut the rest)

```
running → gated → (approved) → next phase | paused | failed | completed
```
State persisted to `<project>/.aeh/runs/<run-id>/state.json` (OUTSIDE the worktree) on every transition; `state_schema_version: 1`. **CUT from v0.1:** `regression`/`replanning` states, the 3-replan halt loop, `force-state` recovery, 30-day retention timer, `--prompt-override`.

## Phase prompts + exemplars

Five phase prompts in `prompts/<phase>.md`; each paired with `prompts/<phase>.exemplar.md` (a reference-quality artifact the gate scores against) and a per-phase `criterion` string.

## Manual approval prompt (scannable)

```
PHASE: spec (gated) — exemplar match 7.4/10 · dispersion σ=1.8  ⚠ judges disagree
  judge    score  critique
  claude     8    "covers the error model; thin on edge cases"
  gpt        7    "spec is clear; success criteria vague"
  gemini     7    "good structure; missing rollback story"

[a]pprove  [r]eject  [d]iff  [v]erbose-critiques
```
Lead with the headline number; per-judge as a compact table; **dispersion is the visual centerpiece** (it's the methodology differentiator); spell out the keys every time.

## `aeh demo` — the hero asset (60-second scan)

`aeh demo` (alias `aeh run --replay`) replays a committed recorded run from `examples/recorded-run/` to the terminal in <2s — **no `claude` CLI, no API keys**. It feeds fixture JSON to the *same renderer* a real run uses (honest, not a mock). The README's first screen is: one-line pitch → an asciinema/GIF of this gate output (above the fold) → the 2-line `aeh demo` quickstart. This is what converts a 60-second scan into "this person understands eval methodology" — build it first.

## CLI commands

`aeh run <project>` · `aeh resume <id>` · `aeh status <id>` · `aeh show <id>` (re-print a past run's gate output) · `aeh cleanup <id>` (dry-run by default; `--force` to delete) · `aeh demo`. **CUT `aeh pause`** — Ctrl-C between phases + persisted state covers it.

## Preflight checks (before phase 1)

- `claude` not on PATH → `error: 'claude' not found. Install Claude Code CLI (…). Try 'aeh demo' for a no-CLI walkthrough.`
- Missing API keys → validate (canonical-variant + scope aware) **before** phase 1; name the missing var and which judges it disables; offer to run with the available subset. Never drive 3 minutes of Claude then die at the gate.

## Worktree coordination

One git worktree per run at `<project>/.aeh/worktrees/<run-id>/`; state file lives outside it (survives cleanup). Created at `run`; cleaned on explicit `cleanup --force`. (Cut: "warn if main HEAD changed" detection — worktree isolation already covers it.)

## Dependencies

- **Vendored, in-repo:** `eval_gate/judging.py` (multi-vendor scoring, adapted from cross-vendor-judges with attribution). No runtime dependency on any private skills directory.
- **HARD:** `claude` CLI + Claude Code subscription (for `aeh run`; NOT needed for `aeh demo`).
- API keys for the gate's judges (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`), keyed by canonical-variant + scope-aware lookup.
- Python 3.11+, `git` 2.5+.
- **NO hard dependency on `ai-eval-toolkit` at v0.1** (decoupled). Toolkit `calibrate` re-enters at v0.2 (below).

## v0.2 path (the calibration re-entry)

Log the operator's approve/reject decisions per gated phase. At v0.2, use `ai-eval-toolkit`'s `calibrate` to measure agreement (Cohen's κ) between the gate's scores and the operator's actual decisions. Only once the gate is calibrated against the human does it earn configurable auto-approval. This is the disciplined human-in-the-loop → calibrated-automation arc, and the coherent cross-repo link to the toolkit.

## Tests

- **End-to-end with a mocked `claude` binary** (fake script writes a canned artifact, exits 0): drive ideate→review on a throwaway git repo in a tmpdir; assert state transitions persist, worktree created, `resume` round-trips.
- **Gate test with `eval_gate/judging` stubbed:** assert the gate renders scores+dispersion+critiques and emits NO approve/reject token.
- **Parity test:** vendored judging vs known `judge.py` output on a fixed fixture.
- **One real (or VCR-recorded) judge call**, gated behind a keys/marker so keyless CI still passes.
- **Failure modes:** timeout → `failed`; missing-artifact → `failed`; judge error → gate degrades with warning, run doesn't crash.

## Success criteria (verifiable)

- [ ] `aeh demo` replays recorded gate output in <2s with no `claude` CLI and no API keys
- [ ] `aeh run <project>` drives a Phase 1 run; ideate produces output; CLI shows the gate then prompts for manual approval
- [ ] State persists at `.aeh/runs/<id>/state.json` after every transition; `resume` round-trips
- [ ] Worktree creates at `.aeh/worktrees/<id>/`; `cleanup --force` removes it
- [ ] Gate surfaces per-judge scores + dispersion + critiques and emits NO automated verdict token
- [ ] Vendored judging matches `judge.py` on the parity fixture
- [ ] Preflight: missing `claude` CLI or keys produces an actionable error that points to `aeh demo`
- [ ] `claude --print` timeout → `failed` state with captured logs; missing artifact → `failed`, never silent-advance
- [ ] README first screen: one-liner + gate-output GIF above the fold + `aeh demo` quickstart; states the gate is decision-support

## Risks + mitigations

1. **`claude --print` reliability** (the #1 risk now that MCP coupling is gone): timeout + returncode + artifact-validation + version pin (above).
2. **Vendored-snapshot drift** vs cross-vendor-judges: parity test + attribution comment noting it's a snapshot.
3. **Scope creep** (perfectionism vector): hard cut list — no replanning, no cost-guard, no multi-agent, no pause, no toolkit coupling at v0.1.
4. **Gate read as circular/naive:** mitigated by the decision-support framing + the explicit v0.2 calibration path stated in the README.

## What's NOT in v0.1 (deferred)

- Replanning trigger + `regression` state — v0.2.
- Automated approve/regenerate/halt verdict — abandoned; the gate is decision-support.
- `ai-eval-toolkit` coupling — decoupled; re-enters at v0.2 for gate calibration only.
- Cost guard / `--budget-tokens` — v0.3 (`claude --print` gives no reliable token accounting anyway).
- Multi-agent parallelism, autonomous mode, infinite-loop detection — v0.3+.
- `aeh pause`, `force-state`, retention timer, `--prompt-override` — cut.
- Adapters (Aider/OpenHands/codex) — v0.3+ (deferred indefinitely).
- Static HTML results dashboard, web UI — v0.2+.

## Implementation task list

- [ ] this `docs/SPEC.md` — reconciled ✅ (written)
- [ ] **build FIRST** — `aeh demo` recorded-run replay + `examples/recorded-run/` fixture + README gate-output GIF
- [ ] `eval_gate/judging.py`: vendored multi-vendor scoring (attribution header) + parity test vs judge.py
- [ ] Phase Runner: hardened `claude --print` driver (timeout, returncode, artifact validation, version pin, log capture)
- [ ] Orchestrator + state machine (minimal) + `.aeh/runs/<id>/state.json` persistence; `run`/`resume`/`status`/`show`/`cleanup`
- [ ] Worktree Manager (1/run; state outside worktree; `cleanup --force`)
- [ ] Preflight checks (claude CLI + keys) with demo redirect
- [ ] Eval Gate: reference-exemplar scoring via vendored judging; surface scores+dispersion+critiques; NO verdict token
- [ ] Scannable approval prompt renderer (shared with `aeh demo`)
- [ ] Phase prompts + exemplars (`prompts/<phase>.md` + `.exemplar.md` + criteria)
- [ ] Tests — mocked-claude e2e, stubbed-gate, parity, VCR judge call, failure modes

> Design rationale, the cross-vendor review record, and the decision audit for this SPEC are in [`DECISIONS.md`](./DECISIONS.md).

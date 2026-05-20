# DEPLOY READY — agentic-eval-harness v0.1

All 14 plan tasks are DONE and verification is green. The loop has halted at the
**binding deploy gate**. Deploy does not proceed until you authorize it with
`/idea-to-ship deploy`.

## What shipped (branch `build/v0.1`, 14 commits)

- `aeh` CLI: `run / resume / status / show / cleanup / list / demo / --version`
- `aeh demo` hero replay (no claude CLI, no keys, no SDKs, <2s) feeding the same renderer a live run uses
- Vendored cross-vendor judging (`eval_gate/judging.py`) + parity test (prompt-snapshot + upstream-SHA pin) + injection delimiter
- Eval gate: parallel reference-exemplar scoring, degrade-on-judge-error, **no verdict token**
- Hardened `claude --print` driver: shutil.which resolution, timeout + process-tree kill, UTF-8, rc/artifact decision table
- Atomic versioned state store + per-run lock; worktree manager with enumerated failures; preflight (claude + canonical-variant keys)
- Scannable renderer: σ legend + disagreement threshold, NO_COLOR / non-TTY / ASCII / narrow-term + auto unicode detection
- 5 phase prompts + illustrative exemplars + per-phase criteria
- Tests: 51 passing (models, renderer, demo, judging parity, gate, state, worktree, phase-runner, preflight, orchestrator, prompts, e2e mocked-claude, security secret-scrub, envelope-version fixtures)

## Verification

- `pytest -q` -> **51 passed**
- `aeh demo` renders the three-phase recorded run; `python -m build --wheel` packages prompts + fixture.
- No remote CI configured (local-only repo); local pytest is the verification gate.

## Deploy = what, exactly

This is a portfolio repo with remote `Mike-E-Log/agentic-eval-harness`. "Deploy" means: merge `build/v0.1` -> `main` and push to GitHub. That is a visible, hard-to-reverse action — hence the gate.

## Open item before/after deploy (your call)

- **`docs/recorded-run.gif` is not recorded.** It needs a real terminal capture (asciinema/GIF) that this session can't produce. The README references it (broken image until recorded) but includes the gate output as a fenced text block, so the first screen is still legible. Options: record it before deploy, or deploy now and add the GIF in a follow-up.

To proceed: `/idea-to-ship deploy` (merge + push). To hold: `/idea-to-ship hold`.

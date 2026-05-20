# Changelog

All notable changes to agentic-eval-harness are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); this project adheres to semantic versioning.

## [0.1.0] — 2026-05-20

First release. An eval-gated runner that drives Claude Code through five phases and, at each boundary, runs an independent cross-vendor panel that scores the phase output against a known-good exemplar — surfacing per-judge scores, dispersion, and critiques as **decision-support, not an automated verdict**.

### Added
- `aeh` CLI: `run`, `resume`, `status`, `show`, `cleanup` (dry-run by default; `--force`), `list`, `demo`, `--version`.
- `aeh demo` — replays a recorded run through the same renderer a live run uses, in under 2 seconds, with no `claude` CLI, no API keys, and no vendor SDKs installed.
- Cross-vendor eval gate: vendored multi-vendor judging (`eval_gate/judging.py`, attribution + upstream-SHA pin) with a parity test that snapshots the constructed prompt; reference-exemplar scoring that degrades on judge error and **emits no verdict token**.
- Hardened `claude --print` driver: `shutil.which` resolution (Windows `.cmd` shim), timeout + process-tree kill, UTF-8 decode, and an explicit returncode/artifact decision table.
- Atomic, schema-versioned state store with a per-run lock; one git worktree per run with state preserved outside it; preflight checks (claude on PATH + canonical-variant API keys).
- Scannable approval renderer: dispersion (σ) legend + disagreement threshold, `NO_COLOR`/non-TTY/ASCII fallbacks, narrow-terminal truncation, and terminal-unicode auto-detection.
- Five phase prompts + illustrative exemplars + per-phase criteria.

### Fixed
- `aeh run` now drives the full phase loop end-to-end (`next_phase` → `create_worktree` → `run_phase` → `run_gate` → render → persist → manual approval). The orchestration components existed and were unit-tested, but nothing connected them into `run`; this wires them via a new `aeh/driver.py`. `aeh run` accepts `--yes` (auto-approve) and `--timeout`. Added a real end-to-end test (`tests/test_e2e.py`) that drives all five phases through a fake `claude` and asserts the gate fires and state advances, plus a keyless GitHub Actions CI workflow.
- The `implement` phase prompt now also writes `docs/IMPLEMENT.md`, giving every phase a uniform gateable artifact.

### Security
- Untrusted agent output is wrapped in an unspoofable delimiter before it enters a judge prompt (prompt-injection defense); a test scrubs the committed `examples/recorded-run/` fixture for secret-like tokens.

### Known limitations
- Single-reference exemplar comparison (reference-bias is documented, not yet mitigated).
- Gate scores are uncalibrated heuristics shown to the operator. Calibrating them against operator decisions (Cohen's κ) is the v0.2 roadmap — see [`docs/DECISIONS.md`](docs/DECISIONS.md).
- README hero is the gate text block; the animated GIF (`docs/recorded-run.tape`) is optional and not yet rendered.

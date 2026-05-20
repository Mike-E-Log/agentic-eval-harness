# Design Decisions — agentic-eval-harness

This repo's v0.1 SPEC was produced through a review (CEO + Eng + DX) with a cross-vendor LLM judge panel (Claude + GPT + Gemini) as the adversarial second voice. This file records how the design was reached so the reasoning behind [`SPEC.md`](./SPEC.md) is auditable.

## What the review changed

The original design had the eval gate (a) produce an automated `approve|regenerate|halt` verdict from a mean of LLM scores, and (b) depend on `ai-eval-toolkit`'s `bias.analyze` ceiling verdict + `calibrate.agreement`. Both broke under review:

1. **Automated-verdict framing** repeated the unverifiable-heuristic mistake (gating on a mean of uncalibrated LLM scores with no validation against human judgment). The cross-vendor panel scored the verdict framing **2.33/10** vs decision-support framing **9.67/10**.
2. **Toolkit dependency** was stale (those toolkit primitives were repositioned away) and created a hard chokepoint. The panel scored decoupling **9.33/10** vs keeping the dependency **2.67/10**.

The harness was reshaped: the eval gate is **decision-support** (surfaces evidence, the human approves); scoring is **self-contained** (vendored multi-vendor judging logic, decoupled from the toolkit for v0.1).

## Decision Audit Trail

| # | Phase | Decision | Class | Evidence |
|---|-------|----------|-------|----------|
| 1 | CEO | Gate = decision-support, not automated verdict | Premise | judges 9.67 vs 2.33 |
| 2 | CEO | Decouple from toolkit for v0.1 (toolkit calibrate → v0.2) | Premise | judges 9.33 vs 2.67 |
| 3 | CEO | Defer replanning entirely to v0.2 | Mechanical | subagent; scope discipline |
| 4 | Eng | Reference-exemplar comparison (reuse comparative judging), not single-artifact rubric mode | Taste→auto | judges 9.33 vs 4.00 |
| 5 | Eng | Vendor judging logic into repo with attribution (not call external judge.py, not extract package, not fresh impl) | Taste | judges 9.33 (B 5.67, C 2.67); flag=noise (6.66pt spread) |
| 6 | Eng | Harden `claude --print` driver (timeout/returncode/artifact-validation/version-pin) | Mechanical | subagent CRITICAL |
| 7 | Eng | Minimal state machine; cut regression/force-state/retention/prompt-override | Mechanical | subagent; scope |
| 8 | DX | `aeh demo` recorded-run replay (hero asset); README gate-output GIF above fold | Mechanical | subagent CRITICAL |
| 9 | DX | Scannable approval prompt; dispersion as centerpiece; spelled-out keys | Mechanical | subagent |
| 10 | DX | Preflight checks for claude CLI + keys before phase 1 | Mechanical | subagent HIGH |
| 11 | DX | Cut `aeh pause`; add `aeh show` | Mechanical | subagent |

> Provenance note: decision #5 was initially mis-locked as "call the external judge.py directly" due to a misread; on review that mechanism was non-distributable (judge.py lives in a private skills dir). Re-judged → vendor-with-attribution. The SPEC reflects validated decisions, not assumed ones.

## Review Report

| Review | Runs | Status | Findings |
|--------|------|--------|----------|
| CEO Review | 1 | reshaped | Gate→decision-support; decouple from toolkit; 6 subagent findings (2 critical) |
| Cross-vendor Judges (Claude+GPT+Gemini) | 3 | 2 PASS, 1 FLAGGED(noise) | gate-framing 9.67 vs 2.33; decouple 9.33 vs 2.67; mechanism 9.33 (flag=noise, 6.66pt spread) |
| Design Review | 0 | skipped | No UI scope (CLI tool) |
| Eng Review | 1 | clean after fixes | Vendor judging; reference-exemplar; harden driver; minimal state machine; 6 findings |
| DX Review | 1 | clean after fixes | `aeh demo` hero asset; scannable prompt; preflight; cut pause; 6 findings |

- **Cross-model:** the mechanism round FLAGGED at τ=1.00 but the 6.66-point score spread marks it genuine consensus, not collusion (a live application of the toolkit's own methodology).
- **Cross-phase theme:** honesty over flash + scope discipline — the gate must not overclaim (decision-support, not verdict); the repo must self-contain and ship in budget.
- **Verdict:** APPROVED. Decoupled from toolkit, so the 4 repos can run in parallel.

## Second pass — /autoplan before the build loop (2026-05-19)

Re-ran CEO + Eng + DX review on the SPEC via `/idea-to-ship` → `/autoplan` (Claude-subagent voices only; Codex was unavailable). The implementation plan landed at [`../plan/EXECUTION_PLAN.md`](../plan/EXECUTION_PLAN.md). Full review artifact: `~/.gstack/projects/agentic-eval-harness/main-autoplan-review-20260519.md`.

**Premise re-opened and held:** all three voices flagged that v0.1 ships zero *measured* eval methodology (calibration deferred to v0.2), so "decision-support honesty" risks reading as a hedge to an eval-savvy reviewer. Offered: (A) pull a calibration slice into v0.1, (B) keep scope + harden, (C) reframe to gate-only. **Operator chose B** — respect the documented v0.2 deferral; ship runner+gate + 18 hardening fixes. Calibration stays v0.2; single-reference exemplar bias is now documented as a known limitation rather than fixed.

**18 hardening fixes folded into the plan (all auto-decided, mechanical/completeness):**

| Area | Fix |
|------|-----|
| Security | prompt-injection (agent-output→judge-prompt) added to threat model + unspoofable untrusted-content delimiter; secret-scrub test on the committed `examples/recorded-run/` fixture |
| Driver | replace "parse defensively" with a concrete `--output-format json` probe + pinned min CLI version; recorded-envelope version fixtures (the mock can't see CLI-version drift) |
| Driver (Win) | process-tree kill on timeout, UTF-8 decode (`errors="replace"`), MAX_PATH, CRLF — author is on Windows |
| State | atomic write (tmp+fsync+`os.replace`) + per-run lockfile; resume semantics per source state; `state_schema_version` mismatch + corrupt-state actionable errors |
| Parity | snapshot the *constructed prompt string* (highest-drift surface) + record upstream `judge.py` SHA, not just scored output |
| Stats | precise σ definition (sample stdev over present judges); N=1 suppresses σ; failed judge → excluded row, σ recomputed over survivors; fixed the showcase mean (8,7,7 → 7.33, not 7.4) |
| DX | pinned install/entry-point (`[project.scripts]`, pipx/uvx, fixture-in-wheel); added `aeh list` + print-id-and-resume-cmd on run; σ legend + disagreement threshold; `aeh demo` runs with vendor SDKs uninstalled (lazy-import); NO_COLOR/non-TTY/ASCII/narrow-term fallbacks; `aeh --version` + LICENSE; error copy for corrupt-state/worktree-collision/missing-fixture/unknown-id; README needs/cost(~15 judge calls/full run)/safety block |
| Structure | named State Store + Renderer as first-class modules; promoted exemplar + criterion authoring to first-class tasks |

Already correct (not a finding): `.aeh/` is gitignored. **Verdict:** plan APPROVED; ready for the build loop (deploy gate remains binding).

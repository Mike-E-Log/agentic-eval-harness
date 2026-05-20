# agentic-eval-harness

An eval-gated runner that drives a coding agent (Claude Code) through phases — ideate → spec → plan → implement → review — and, at each boundary, runs an independent cross-vendor panel that scores the phase output and surfaces per-judge scores, disagreement, and critiques to you.

The gate is **decision-support, not an automated verdict**: it doesn't pretend an uncalibrated multi-LLM vote is a trustworthy classifier. You approve each phase; the gate informs the call. The disciplined path to automation (calibrating the gate against your own approve/reject decisions) is the v0.2 roadmap.

**Status:** v0.1 in progress. See [`docs/SPEC.md`](./docs/SPEC.md) for the design and [`docs/DECISIONS.md`](./docs/DECISIONS.md) for how it was reached.

_A `aeh demo` (recorded-run replay, no CLI or keys needed) + a gate-output GIF land at the top of this README as v0.1 ships._

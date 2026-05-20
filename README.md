# agentic-eval-harness

Eval-gated runner for coding agents. Drives Claude Code through ideate -> spec -> plan -> implement -> review and, at each boundary, runs an independent cross-vendor panel that scores the phase output against a known-good exemplar, surfacing per-judge scores, disagreement (sigma), and critiques to you. **Decision-support, not an automated verdict.**

It doesn't pretend an uncalibrated multi-LLM vote is a trustworthy classifier. You approve each phase; the gate informs the call. The disciplined path to automation — calibrating the gate against your own approve/reject decisions — is the [v0.2 roadmap](docs/DECISIONS.md).

![gate output](docs/recorded-run.gif)

```
PHASE: plan (gated) - exemplar match 6.67/10 · dispersion σ=2.1
  [σ = stdev of judge scores, 0-10; ⚠ judges disagree]
  judge   score critique
  claude  9     tasks are bite-sized and tested
  gpt     5     dependency order unclear in places
  gemini  6     some steps lack concrete code

[a]pprove  [r]eject  [d]iff  [v]erbose-critiques
```

## Quickstart (no keys, no CLI)

```bash
pipx install agentic-eval-harness   # or: uvx agentic-eval-harness demo
aeh demo
```

`aeh demo` replays a recorded run through the same renderer a live run uses — in under 2 seconds, with no `claude` CLI and no API keys.

## For a real run

- **Needs:** Python 3.11+, git 2.5+, the `claude` CLI + a Claude Code subscription, and API keys for the judges (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`). Missing a key just disables that judge.
- **Cost:** a full 5-phase run fires up to ~15 judge API calls (3 judges x 5 boundaries) plus the `claude --print` drive. The demo costs nothing.
- **Safe on your repo:** each run works in an isolated git worktree; your working tree is never mutated; run state lives outside the worktree and survives cleanup.

```bash
aeh run <project>     # drive a project; the gate prompts you at each phase
aeh list              # see run ids
aeh resume <id>       # pick up an interrupted run
aeh show <id>         # re-print a run's last gate scorecard
aeh cleanup <id>      # remove a run's worktree (dry-run; --force to delete)
```

**Status:** v0.1 in progress. See [`docs/SPEC.md`](./docs/SPEC.md) for the design and [`docs/DECISIONS.md`](./docs/DECISIONS.md) for how it was reached (including the reviews that shaped it).

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.11%2B-7c3aed?style=flat-square&labelColor=0f172a"/>
  <img alt="judges" src="https://img.shields.io/badge/judges-claude%20%2B%20gpt%20%2B%20gemini-f59e0b?style=flat-square&labelColor=0f172a"/>
  <img alt="mode" src="https://img.shields.io/badge/mode-decision--support-22c55e?style=flat-square&labelColor=0f172a"/>
  <img alt="status" src="https://img.shields.io/badge/status-v0.1%20in%20progress-0ea5e9?style=flat-square&labelColor=0f172a"/>
</p>

<h2 align="center">agentic-eval-harness · eval-gated runner for coding agents</h2>

<p align="center">
  <em>Drives Claude Code through ideate → spec → plan → implement → review; at each<br/>boundary, a cross-vendor judge panel scores against a known-good exemplar.<br/>Decision-support, not an automated verdict.</em>
</p>

---

It doesn't pretend an uncalibrated multi-LLM vote is a trustworthy classifier. You approve each phase; the gate informs the call. The disciplined path to automation — calibrating the gate against your own approve/reject decisions — is the [v0.2 roadmap](docs/DECISIONS.md).

What the gate shows you at a phase boundary (`aeh demo` prints exactly this):

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

---

**AI-evaluation engineering portfolio** — five repos, one discipline:

- [**ai-eval-toolkit**](https://github.com/Mike-E-Log/ai-eval-toolkit) — judge-vs-human calibration (Cohen's κ / Kendall-τ vs Landis–Koch bands)
- **agentic-eval-harness** *(you are here)* — eval-gated Claude Code phase boundaries with cross-vendor scorecards
- [**ai-eval-atlas**](https://github.com/Mike-E-Log/ai-eval-atlas) — practitioner + technique map, source-linked
- [**ai-engineer-best-practices**](https://github.com/Mike-E-Log/ai-engineer-best-practices) — handbook + `score` MCP tool (3-vendor judge ensemble)
- [**learn-ai-eval**](https://github.com/Mike-E-Log/learn-ai-eval) — Claude-tutored learning engine for the eval canon

Profile: [github.com/Mike-E-Log](https://github.com/Mike-E-Log) · website: [mikeilog.com](https://mikeilog.com)

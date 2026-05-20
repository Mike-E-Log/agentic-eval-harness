from aeh.models import GateResult, JudgeScore
from aeh.renderer import render_gate


def _g(scores):
    return GateResult(phase="spec", exemplar_ref="prompts/spec.exemplar.md", scores=scores)


def test_leads_with_headline_and_no_verdict_token():
    out = render_gate(_g([JudgeScore("claude", 8, "covers error model"),
                          JudgeScore("gpt", 7, "clear"),
                          JudgeScore("gemini", 7, "good structure")]), color=False, width=80)
    assert "exemplar match 7.33/10" in out
    assert "[a]pprove" in out and "[r]eject" in out
    for forbidden in ("APPROVE", "REGENERATE", "HALT", "recommendation"):
        assert forbidden not in out


def test_sigma_has_legend_and_threshold_warning():
    out = render_gate(_g([JudgeScore("claude", 9, "x"), JudgeScore("gpt", 6, "y"),
                          JudgeScore("gemini", 5, "z")]), color=False, width=80)
    assert "dispersion" in out and "judges disagree" in out
    assert "stdev of judge scores, 0-10" in out


def test_single_judge_suppresses_dispersion():
    out = render_gate(_g([JudgeScore("claude", 8, "x")]), color=False, width=80)
    assert "single judge" in out and "dispersion" not in out


def test_failed_judge_rendered_as_excluded_row():
    out = render_gate(_g([JudgeScore("claude", 8, "ok"),
                          JudgeScore("gpt", 0, "", error="timeout"),
                          JudgeScore("gemini", 7, "ok")]), color=False, width=80)
    assert "gpt" in out and "excluded" in out
    assert "7.5/10" in out


def test_no_color_and_ascii_fallback():
    out = render_gate(_g([JudgeScore("claude", 9, "x"), JudgeScore("gpt", 5, "y")]),
                      color=False, width=80, unicode=False)
    assert "\x1b[" not in out
    assert "⚠" not in out and "(!)" in out


def test_long_critique_truncated_to_width():
    long = "edge cases " * 30
    out = render_gate(_g([JudgeScore("claude", 8, long), JudgeScore("gpt", 7, "ok")]),
                      color=False, width=80)
    assert "…" in out or "..." in out
    assert all(len(line) <= 80 for line in out.splitlines())

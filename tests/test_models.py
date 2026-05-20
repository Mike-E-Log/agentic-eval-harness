import dataclasses
import statistics

from aeh.models import GateResult, JudgeScore, PHASES, GATE_SCHEMA_VERSION


def test_phases_are_the_five():
    assert PHASES == ("ideate", "spec", "plan", "implement", "review")


def test_gate_result_has_no_verdict_field():
    fields = {f.name for f in dataclasses.fields(GateResult)}
    for forbidden in ("recommendation", "verdict", "ceiling_fired", "halt"):
        assert forbidden not in fields


def test_gate_result_roundtrips_json_with_schema_version():
    g = GateResult(
        phase="spec", exemplar_ref="prompts/spec.exemplar.md",
        scores=[JudgeScore("claude", 8, "covers error model; thin on edges"),
                JudgeScore("gpt", 7, "clear; success criteria vague"),
                JudgeScore("gemini", 7, "good structure; missing rollback")],
    )
    d = g.to_dict()
    assert d["schema_version"] == GATE_SCHEMA_VERSION
    back = GateResult.from_dict(d)
    assert back == g


def test_headline_is_mean_and_internally_consistent():
    g = GateResult(phase="spec", exemplar_ref="x",
                   scores=[JudgeScore("a", 8, ""), JudgeScore("b", 7, ""), JudgeScore("c", 7, "")])
    assert round(g.headline, 2) == 7.33   # mean of 8,7,7 — NOT 7.4


def test_dispersion_is_sample_stdev_over_present_judges():
    g = GateResult(phase="spec", exemplar_ref="x",
                   scores=[JudgeScore("a", 8, ""), JudgeScore("b", 7, ""), JudgeScore("c", 7, "")])
    assert round(g.dispersion, 4) == round(statistics.stdev([8, 7, 7]), 4)


def test_single_judge_has_no_dispersion():
    g = GateResult(phase="spec", exemplar_ref="x", scores=[JudgeScore("a", 8, "")])
    assert g.dispersion is None

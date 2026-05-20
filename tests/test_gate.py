from aeh.eval_gate import gate
from aeh.eval_gate.judging import JudgeOutput
from aeh.models import GateResult


def test_gate_scores_against_exemplar_and_emits_no_verdict(monkeypatch):
    monkeypatch.setattr(
        gate.judging, "score_candidate",
        lambda judge, **kw: JudgeOutput(judge, {"claude": 8, "gpt": 7, "gemini": 7}[judge], f"{judge} note"))
    g = gate.run_gate(phase="spec", candidate="body", exemplar="ref",
                      exemplar_ref="prompts/spec.exemplar.md", criterion="c",
                      judges=["claude", "gpt", "gemini"])
    assert isinstance(g, GateResult)
    assert "recommendation" not in g.to_dict()
    assert round(g.headline, 2) == 7.33


def test_gate_degrades_on_judge_error(monkeypatch):
    def flaky(judge, **kw):
        if judge == "gemini":
            raise TimeoutError("timeout")
        return JudgeOutput(judge, 8 if judge == "claude" else 7, "ok")

    monkeypatch.setattr(gate.judging, "score_candidate", flaky)
    g = gate.run_gate(phase="spec", candidate="b", exemplar="r",
                      exemplar_ref="x", criterion="c", judges=["claude", "gpt", "gemini"])
    errored = [s for s in g.scores if s.error]
    assert len(errored) == 1 and errored[0].judge == "gemini"
    assert round(g.headline, 2) == 7.5


def test_single_judge_subset(monkeypatch):
    monkeypatch.setattr(gate.judging, "score_candidate", lambda judge, **kw: JudgeOutput(judge, 8, "x"))
    g = gate.run_gate(phase="spec", candidate="b", exemplar="r", exemplar_ref="x",
                      criterion="c", judges=["claude"])
    assert g.dispersion is None and len(g.present) == 1

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from aeh.eval_gate import judging
from aeh.models import GateResult, JudgeScore


def run_gate(*, phase: str, candidate: str, exemplar: str, exemplar_ref: str,
             criterion: str, judges: list[str]) -> GateResult:
    def one(judge: str) -> JudgeScore:
        try:
            o = judging.score_candidate(
                judge, candidate=candidate, exemplar=exemplar, criterion=criterion)
            return JudgeScore(judge=o.judge, score=o.score, critique=o.critique)
        except Exception as e:   # degrade, never crash the run
            return JudgeScore(judge=judge, score=0.0, critique="",
                              error=f"{type(e).__name__}: {e}")

    with ThreadPoolExecutor(max_workers=len(judges) or 1) as ex:
        scores = list(ex.map(one, judges))
    return GateResult(phase=phase, exemplar_ref=exemplar_ref, scores=scores)

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass, field

PHASES = ("ideate", "spec", "plan", "implement", "review")
GATE_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1

# Disagreement threshold for the "judges disagree" warning (sample stdev of 0-10 scores).
DISPERSION_WARN_THRESHOLD = 1.5


@dataclass(frozen=True)
class JudgeScore:
    judge: str          # "claude" | "gpt" | "gemini"
    score: float        # 0-10
    critique: str
    error: str | None = None   # set when the judge call failed; excluded from stats


@dataclass(frozen=True)
class GateResult:
    phase: str
    exemplar_ref: str
    scores: list[JudgeScore] = field(default_factory=list)
    schema_version: int = GATE_SCHEMA_VERSION

    @property
    def present(self) -> list[JudgeScore]:
        return [s for s in self.scores if s.error is None]

    @property
    def headline(self) -> float | None:
        vals = [s.score for s in self.present]
        return statistics.fmean(vals) if vals else None

    @property
    def dispersion(self) -> float | None:
        vals = [s.score for s in self.present]
        return statistics.stdev(vals) if len(vals) >= 2 else None

    @property
    def disagree(self) -> bool:
        d = self.dispersion
        return d is not None and d >= DISPERSION_WARN_THRESHOLD

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "GateResult":
        if d.get("schema_version") != GATE_SCHEMA_VERSION:
            raise ValueError(
                f"gate fixture schema_version {d.get('schema_version')} "
                f"!= supported {GATE_SCHEMA_VERSION}; reinstall or update aeh")
        return cls(
            phase=d["phase"], exemplar_ref=d["exemplar_ref"],
            scores=[JudgeScore(**s) for s in d["scores"]],
            schema_version=d["schema_version"])

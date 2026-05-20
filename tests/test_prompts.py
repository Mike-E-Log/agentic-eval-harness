import json
from pathlib import Path

from aeh.models import PHASES

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def test_every_phase_has_prompt_exemplar_and_criterion():
    crit = json.loads((PROMPTS / "criteria.json").read_text(encoding="utf-8"))
    for p in PHASES:
        assert (PROMPTS / f"{p}.md").is_file()
        assert (PROMPTS / f"{p}.exemplar.md").is_file()
        assert p in crit and len(crit[p]) > 20


def test_criteria_are_comparative_and_specific():
    crit = json.loads((PROMPTS / "criteria.json").read_text(encoding="utf-8"))
    assert "error model" in crit["spec"].lower() or "edge" in crit["spec"].lower()

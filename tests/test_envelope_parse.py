import json
from pathlib import Path

from aeh.orchestrator import extract_result

ENV = Path(__file__).parent / "fixtures" / "claude_envelopes"


def test_extracts_body_from_each_recorded_version():
    files = list(ENV.glob("*.json"))
    assert files, "no envelope fixtures recorded"
    for f in files:
        env = json.loads(f.read_text(encoding="utf-8"))
        assert isinstance(extract_result(env), str) and extract_result(env)

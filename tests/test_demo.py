import json
import time

import pytest

from aeh.demo import fixture_path, run_demo


def test_fixture_exists_and_valid_schema():
    data = json.loads(fixture_path().read_text(encoding="utf-8"))
    assert data["phases"]
    for p in data["phases"]:
        assert p["schema_version"] == 1
        assert "recommendation" not in p


def test_demo_renders_each_phase_under_2s(capsys):
    t0 = time.perf_counter()
    run_demo(color=False, width=80)
    elapsed = time.perf_counter() - t0
    out = capsys.readouterr().out
    assert "[a]pprove" in out
    assert elapsed < 2.0


def test_demo_runs_with_sdks_unimportable(monkeypatch):
    import builtins
    real_import = builtins.__import__

    def guard(name, *a, **k):
        if name in ("anthropic", "openai", "google", "google.genai"):
            raise ImportError(f"{name} not installed")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", guard)
    run_demo(color=False, width=80)   # must not raise


def test_missing_fixture_actionable_error(monkeypatch, tmp_path):
    monkeypatch.setattr("aeh.demo.fixture_path", lambda: tmp_path / "missing.json")
    with pytest.raises(SystemExit) as e:
        run_demo()
    assert "recorded-run fixture not found" in str(e.value)

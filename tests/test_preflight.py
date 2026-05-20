from aeh.preflight import KEY_VARIANTS, available_judges, check_claude


def test_missing_claude_points_to_demo(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    ok, msg = check_claude()
    assert not ok and "aeh demo" in msg


def test_available_judges_from_env(monkeypatch):
    for vs in KEY_VARIANTS.values():
        for v in vs:
            monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    present, missing = available_judges()
    assert "claude" in present and "gemini" in present and "gpt" in missing

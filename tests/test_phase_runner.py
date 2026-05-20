import os

from aeh.phase_runner import run_phase


def _prepend_path(monkeypatch, bindir):
    monkeypatch.setenv("PATH", bindir + os.pathsep + os.environ["PATH"])


def test_success_writes_artifact_and_captures_log(tmp_path, fake_claude, monkeypatch):
    art = tmp_path / "docs" / "SPEC.md"
    _prepend_path(monkeypatch, fake_claude(rc=0, artifact_rel=str(art), artifact_body="# Spec\nbody\n"))
    res = run_phase(cwd=tmp_path, prompt="write spec", expected_artifact=art,
                    log_dir=tmp_path / "logs", timeout=30, json_mode=False)
    assert res.status == "gated" and art.is_file()
    assert (tmp_path / "logs" / "spec.log").is_file()


def test_rc_zero_but_missing_artifact_is_failed(tmp_path, fake_claude, monkeypatch):
    _prepend_path(monkeypatch, fake_claude(rc=0, artifact_rel=None))
    res = run_phase(cwd=tmp_path, prompt="x", expected_artifact=tmp_path / "docs" / "SPEC.md",
                    log_dir=tmp_path / "logs", timeout=30, json_mode=False)
    assert res.status == "failed" and "artifact" in res.reason


def test_timeout_is_failed_with_partial_log(tmp_path, fake_claude, monkeypatch):
    _prepend_path(monkeypatch, fake_claude(rc=0, sleep=5, stdout="partial"))
    res = run_phase(cwd=tmp_path, prompt="x", expected_artifact=tmp_path / "a.md",
                    log_dir=tmp_path / "logs", timeout=1, json_mode=False)
    assert res.status == "failed" and "timeout" in res.reason


def test_nonzero_rc_is_failed(tmp_path, fake_claude, monkeypatch):
    _prepend_path(monkeypatch, fake_claude(rc=2, artifact_rel=None))
    res = run_phase(cwd=tmp_path, prompt="x", expected_artifact=tmp_path / "a.md",
                    log_dir=tmp_path / "logs", timeout=30, json_mode=False)
    assert res.status == "failed"

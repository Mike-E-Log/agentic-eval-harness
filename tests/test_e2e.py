import os
import subprocess
import sys

from aeh.state_store import StateStore


def _git(*a, cwd):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)


def test_run_creates_state_and_resume_roundtrips(tmp_path, fake_claude, monkeypatch):
    _git("init", cwd=tmp_path)
    _git("config", "user.email", "t@t", cwd=tmp_path)
    _git("config", "user.name", "t", cwd=tmp_path)
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    _git("add", ".", cwd=tmp_path)
    _git("commit", "-m", "init", cwd=tmp_path)

    bindir = fake_claude(rc=0, artifact_rel=None)
    monkeypatch.setenv("PATH", bindir + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.chdir(tmp_path)

    r = subprocess.run([sys.executable, "-m", "aeh", "run", "."],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert "resume with 'aeh resume" in r.stdout

    runs = list((tmp_path / ".aeh" / "runs").iterdir())
    assert len(runs) == 1
    rid = runs[0].name
    assert StateStore(tmp_path, rid).read()["status"] == "running"

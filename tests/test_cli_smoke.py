import subprocess
import sys


def test_aeh_version_runs():
    r = subprocess.run(
        [sys.executable, "-m", "aeh", "--version"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert r.returncode == 0
    assert "aeh" in r.stdout.lower()


def test_bare_aeh_leads_with_demo():
    r = subprocess.run(
        [sys.executable, "-m", "aeh"],
        capture_output=True, text=True, encoding="utf-8",
    )
    # bare invocation prints usage whose first suggested command is `aeh demo`
    assert "aeh demo" in r.stdout

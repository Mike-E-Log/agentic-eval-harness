import stat
import sys
import textwrap

import pytest


@pytest.fixture
def fake_claude(tmp_path):
    """Factory writing a fake `claude` binary on a temp dir, returned for PATH."""
    def make(*, rc=0, artifact_rel=None, artifact_body="# out\n", sleep=0, stdout="ok"):
        d = tmp_path / "bin"
        d.mkdir(exist_ok=True)
        name = "claude.cmd" if sys.platform == "win32" else "claude"
        p = d / name
        py = sys.executable.replace("\\", "/")
        body = textwrap.dedent(f'''\
            import sys, time, pathlib
            time.sleep({sleep})
            if {artifact_rel!r}:
                _a = pathlib.Path({artifact_rel!r})
                _a.parent.mkdir(parents=True, exist_ok=True)
                _a.write_text({artifact_body!r}, encoding="utf-8")
            sys.stdout.write({stdout!r})
            sys.exit({rc})
        ''')
        script = d / "fake_claude.py"
        script.write_text(body, encoding="utf-8")
        if sys.platform == "win32":
            p.write_text(f'@echo off\r\n"{py}" "{script}" %*\r\n', encoding="utf-8")
        else:
            p.write_text(f'#!/usr/bin/env bash\nexec "{py}" "{script}" "$@"\n', encoding="utf-8")
            p.chmod(p.stat().st_mode | stat.S_IEXEC)
        return str(d)
    return make

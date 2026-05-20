from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_CLAUDE_VERSION = (1, 0, 0)   # pin; bump when tested against a newer envelope


@dataclass(frozen=True)
class PhaseResult:
    status: str            # "gated" | "failed"
    reason: str
    artifact: Path | None


def _kill_tree(proc: subprocess.Popen):
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass


def run_phase(*, cwd: Path, prompt: str, expected_artifact: Path,
              log_dir: Path, timeout: int, json_mode: bool) -> PhaseResult:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    phase = Path(expected_artifact).stem.lower()
    logf = log_dir / f"{phase}.log"

    exe = shutil.which("claude")   # resolves the Windows .cmd shim via PATHEXT
    if exe is None:
        return PhaseResult("failed", "'claude' not found on PATH", None)
    args = [exe, "--print"]
    if json_mode:
        args += ["--output-format", "json"]
    args += [prompt]

    popen_kw = dict(cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    encoding="utf-8", errors="replace")
    if sys.platform != "win32":
        popen_kw["start_new_session"] = True             # own process group for tree-kill
    else:
        popen_kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(args, **popen_kw)
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        out, _ = proc.communicate()
        logf.write_text(out or "", encoding="utf-8")
        return PhaseResult("failed", f"timeout after {timeout}s", None)

    logf.write_text(out or "", encoding="utf-8")
    if proc.returncode != 0:
        return PhaseResult("failed", f"claude exited {proc.returncode}; see {logf}", None)
    ea = Path(expected_artifact)
    if not ea.is_file() or ea.stat().st_size == 0:
        return PhaseResult("failed", f"expected artifact {ea} missing/empty", None)
    return PhaseResult("gated", "ok", ea)

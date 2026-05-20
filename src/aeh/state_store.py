from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from aeh.models import STATE_SCHEMA_VERSION


class StateError(Exception):
    pass


class StateStore:
    def __init__(self, project: Path, run_id: str):
        self.run_id = run_id
        self.dir = Path(project) / ".aeh" / "runs" / run_id
        self.path = self.dir / "state.json"
        self.lockpath = self.dir / "run.lock"

    def write(self, state: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        state = {**state, "state_schema_version": STATE_SCHEMA_VERSION, "run_id": self.run_id}
        tmp = self.path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)   # atomic on POSIX + Windows (same fs)

    def read(self) -> dict:
        if not self.path.is_file():
            raise StateError(f"no run '{self.run_id}' found at {self.path} — try `aeh list`")
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise StateError(
                f"state for run '{self.run_id}' is corrupt at {self.path} — "
                f"`aeh cleanup {self.run_id} --force` to discard")
        v = d.get("state_schema_version")
        if v != STATE_SCHEMA_VERSION:
            raise StateError(
                f"run '{self.run_id}' was created by a newer aeh "
                f"(schema {v} > {STATE_SCHEMA_VERSION}) — upgrade aeh")
        return d

    @contextlib.contextmanager
    def lock(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.lockpath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StateError(
                f"run '{self.run_id}' is already in progress "
                f"(lock at {self.lockpath}); if stale, delete it")
        try:
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            yield
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(self.lockpath)

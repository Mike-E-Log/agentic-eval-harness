from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from aeh.models import GateResult
from aeh.renderer import render_gate


def fixture_path() -> Path:
    # packaged under aeh/_data/recorded-run/run.json; fall back to the repo
    # path for editable installs (data-file packaging lands in T14).
    try:
        p = files("aeh").joinpath("_data/recorded-run/run.json")
        if p.is_file():
            return Path(str(p))
    except (ModuleNotFoundError, FileNotFoundError):
        pass
    return Path(__file__).resolve().parents[2] / "examples" / "recorded-run" / "run.json"


def run_demo(*, color=None, width=None) -> None:
    fp = fixture_path()
    if not fp.is_file():
        raise SystemExit(
            f"recorded-run fixture not found at {fp} — reinstall aeh "
            f"or clone the full repo, then run `aeh demo`")
    data = json.loads(fp.read_text(encoding="utf-8"))
    for phase in data["phases"]:
        g = GateResult.from_dict(phase)   # validates schema_version
        print(render_gate(g, color=color, width=width))
        print()

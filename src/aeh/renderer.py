from __future__ import annotations

import os
import shutil
import sys

from aeh.models import GateResult


def _env_color(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    if os.environ.get("NO_COLOR") is not None:
        return False
    return sys.stdout.isatty()


def _truncate(s: str, n: int, ell: str = "…") -> str:
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[: max(0, n - len(ell))].rstrip() + ell


def _supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "σ·⚠…".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def render_gate(g: GateResult, *, color: bool | None = None,
                width: int | None = None, unicode: bool | None = None) -> str:
    color = _env_color(color)
    if unicode is None:
        unicode = _supports_unicode()
    width = width or shutil.get_terminal_size((80, 24)).columns
    warn = "⚠" if unicode else "(!)"
    sig = "σ" if unicode else "sd"
    sep = "·" if unicode else "|"
    ell = "…" if unicode else "..."
    lines: list[str] = []

    head = g.headline
    h = f"PHASE: {g.phase} (gated)"
    if head is not None:
        h += f" - exemplar match {round(head, 2)}/10"
    d = g.dispersion
    if d is not None:
        h += f" {sep} dispersion {sig}={round(d, 1)}"
    elif len(g.present) == 1:
        h += f" {sep} single judge - no cross-vendor signal"
    lines.append(h)

    # Legend on its own line so the headline never gets truncated past the warning.
    if d is not None:
        legend = f"  [{sig} = stdev of judge scores, 0-10"
        if g.disagree:
            legend += f"; {warn} judges disagree"
        legend += "]"
        lines.append(legend)

    name_w, score_w = 8, 6
    crit_w = max(10, width - name_w - score_w - 4)
    lines.append(f"  {'judge':<{name_w}}{'score':<{score_w}}critique")
    for s in g.scores:
        if s.error is not None:
            lines.append(f"  {s.judge:<{name_w}}{'-':<{score_w}}{s.error} (excluded from {sig})")
        else:
            sc = int(s.score) if float(s.score) == int(s.score) else s.score
            lines.append(f"  {s.judge:<{name_w}}{str(sc):<{score_w}}{_truncate(s.critique, crit_w, ell)}")
    lines.append("")
    lines.append("[a]pprove  [r]eject  [d]iff  [v]erbose-critiques")

    out = "\n".join(_truncate(l, width, ell) for l in lines)
    if color:
        out = out.replace(warn, f"\x1b[33m{warn}\x1b[0m")
    return out

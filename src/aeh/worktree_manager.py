from __future__ import annotations

import subprocess
from pathlib import Path


class WorktreeError(Exception):
    pass


def _run(args, cwd):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")


def _ensure_repo(project: Path):
    r = _run(["git", "rev-parse", "--is-inside-work-tree"], project)
    if r.returncode != 0:
        raise WorktreeError(f"{project} is not a git repository — run `git init` first")
    if _run(["git", "rev-parse", "HEAD"], project).returncode != 0:
        raise WorktreeError(
            f"{project} has no commits yet — make an initial commit before `aeh run`")


def create_worktree(project: Path, run_id: str) -> Path:
    project = Path(project)
    _ensure_repo(project)
    wt = project / ".aeh" / "worktrees" / run_id
    if wt.exists():
        raise WorktreeError(
            f"a worktree for run '{run_id}' already exists at {wt} — "
            f"`aeh resume {run_id}` to continue or `aeh cleanup {run_id} --force` to discard")
    wt.parent.mkdir(parents=True, exist_ok=True)
    r = _run(["git", "worktree", "add", "--detach", str(wt), "HEAD"], project)
    if r.returncode != 0:
        raise WorktreeError(f"git worktree add failed: {r.stderr.strip()}")
    return wt


def remove_worktree(project: Path, run_id: str) -> None:
    project = Path(project)
    wt = project / ".aeh" / "worktrees" / run_id
    _run(["git", "worktree", "remove", "--force", str(wt)], project)
    # state.json lives outside the worktree and is intentionally preserved

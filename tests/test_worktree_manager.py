import subprocess

import pytest

from aeh.worktree_manager import WorktreeError, create_worktree, remove_worktree


def _git(*a, cwd):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)


def _repo(tmp_path):
    _git("init", cwd=tmp_path)
    _git("config", "user.email", "t@t", cwd=tmp_path)
    _git("config", "user.name", "t", cwd=tmp_path)
    (tmp_path / "f.txt").write_text("hi", encoding="utf-8")
    _git("add", ".", cwd=tmp_path)
    _git("commit", "-m", "init", cwd=tmp_path)
    return tmp_path


def test_create_and_remove(tmp_path):
    repo = _repo(tmp_path)
    wt = create_worktree(repo, "run1")
    assert wt.is_dir() and (wt / "f.txt").is_file()
    assert wt == repo / ".aeh" / "worktrees" / "run1"
    remove_worktree(repo, "run1")
    assert not wt.is_dir()


def test_not_a_git_repo(tmp_path):
    with pytest.raises(WorktreeError) as e:
        create_worktree(tmp_path, "run1")
    assert "not a git repository" in str(e.value)


def test_repo_with_no_commits(tmp_path):
    _git("init", cwd=tmp_path)
    with pytest.raises(WorktreeError) as e:
        create_worktree(tmp_path, "run1")
    assert "no commits" in str(e.value)


def test_existing_worktree_collision(tmp_path):
    repo = _repo(tmp_path)
    create_worktree(repo, "run1")
    with pytest.raises(WorktreeError) as e:
        create_worktree(repo, "run1")
    assert "already exists" in str(e.value)

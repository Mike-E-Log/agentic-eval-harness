import json

import pytest

from aeh.state_store import StateError, StateStore


def test_write_then_read_roundtrips(tmp_path):
    s = StateStore(tmp_path, "run1")
    s.write({"phase": "spec", "status": "gated"})
    assert s.read()["phase"] == "spec"
    assert s.read()["state_schema_version"] == 1


def test_atomic_write_leaves_no_partial(tmp_path):
    s = StateStore(tmp_path, "run1")
    s.write({"phase": "spec", "status": "running"})
    assert not list((tmp_path / ".aeh" / "runs" / "run1").glob("*.tmp"))


def test_corrupt_state_raises_actionable(tmp_path):
    s = StateStore(tmp_path, "run1")
    s.write({"phase": "spec", "status": "gated"})
    s.path.write_text("{ this is not json", encoding="utf-8")
    with pytest.raises(StateError) as e:
        s.read()
    assert "corrupt" in str(e.value).lower() and "run1" in str(e.value)


def test_schema_mismatch_raises(tmp_path):
    s = StateStore(tmp_path, "run1")
    s.write({"phase": "spec", "status": "gated"})
    d = json.loads(s.path.read_text(encoding="utf-8"))
    d["state_schema_version"] = 999
    s.path.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(StateError) as e:
        s.read()
    assert "newer aeh" in str(e.value)


def test_lock_blocks_second_holder(tmp_path):
    s = StateStore(tmp_path, "run1")
    with s.lock():
        s2 = StateStore(tmp_path, "run1")
        with pytest.raises(StateError):
            with s2.lock():
                pass

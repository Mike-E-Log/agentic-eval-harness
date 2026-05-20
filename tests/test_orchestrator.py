from aeh.orchestrator import next_phase, resume_action


def test_next_phase_advances_through_five():
    assert next_phase(None) == "ideate"
    assert next_phase("ideate") == "spec"
    assert next_phase("review") is None


def test_resume_from_gated_reprompts():
    assert resume_action({"phase": "spec", "status": "gated"}) == "reprompt"


def test_resume_from_running_reruns():
    assert resume_action({"phase": "spec", "status": "running"}) == "rerun"


def test_resume_from_failed_reruns():
    assert resume_action({"phase": "spec", "status": "failed"}) == "rerun"


def test_resume_from_completed_is_noop():
    assert resume_action({"phase": "review", "status": "completed"}) == "noop"

import pytest
from agent_os.continuity import ContinuityVerifier

def test_continuity_no_drift():
    verifier = ContinuityVerifier("test")
    verifier.capture_pre_state("a", "s", {}, "v1", ["root"], {})
    trace = verifier.capture_post_state("a", "s", {}, "v1", ["root"], {})
    assert trace.admissible is True
    assert trace.decision == "ALLOW"

def test_continuity_policy_drift():
    verifier = ContinuityVerifier("test")
    verifier.capture_pre_state("a", "s", {}, "v1", ["root"], {})
    trace = verifier.capture_post_state("a", "s", {}, "v2", ["root"], {})
    assert trace.admissible is False
    assert trace.decision == "DENY"
    assert "policy" in trace.diff

def test_continuity_delegation_drift():
    verifier = ContinuityVerifier("test")
    verifier.capture_pre_state("a", "s", {}, "v1", ["root", "alice"], {})
    trace = verifier.capture_post_state("a", "s", {}, "v1", ["root"], {})
    assert trace.admissible is False
    assert "delegation" in trace.diff

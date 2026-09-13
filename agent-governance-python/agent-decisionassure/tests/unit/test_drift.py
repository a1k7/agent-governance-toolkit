# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from datetime import datetime, timezone, timedelta

from agent_decisionassure.drift import DriftDetector
from agent_decisionassure.models.admissibility import GovernanceState


def _snapshot(policy_version="v4", age_hours=0.0):
    return GovernanceState(
        policy_version=policy_version,
        authority_chain=["delegation_123"],
        evidence_age_hours=0.5,
        model_version="approved_v1",
        timestamp=datetime.now(timezone.utc) - timedelta(hours=age_hours),
    )


def test_no_drift_when_policy_matches_and_session_fresh():
    detector = DriftDetector(drift_threshold_hours=1.0)
    result = detector.detect_drift(_snapshot("v4", 0.1), "v4", {"delegations": []})
    assert result["is_drifted"] is False


def test_policy_version_drift_detected():
    detector = DriftDetector(drift_threshold_hours=1.0)
    result = detector.detect_drift(_snapshot("v4", 0.1), "v5", {"delegations": []})
    assert result["is_drifted"] is True
    types = {e["type"] for e in result["drift_events"]}
    assert "policy_version_drift" in types


def test_session_age_drift_detected():
    detector = DriftDetector(drift_threshold_hours=1.0)
    result = detector.detect_drift(_snapshot("v4", 5.0), "v4", {"delegations": []})
    assert result["is_drifted"] is True
    types = {e["type"] for e in result["drift_events"]}
    assert "session_age_drift" in types


def test_should_deny_returns_true_on_high_severity_drift():
    detector = DriftDetector(drift_threshold_hours=1.0)
    deny, reason = detector.should_deny(_snapshot("v4", 0.1), "v5", {"delegations": []})
    assert deny is True
    assert "drift" in reason.lower()


def test_should_deny_returns_false_when_stable():
    detector = DriftDetector(drift_threshold_hours=1.0)
    deny, _ = detector.should_deny(_snapshot("v4", 0.1), "v4", {"delegations": []})
    assert deny is False

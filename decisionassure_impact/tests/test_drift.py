import pytest
from datetime import datetime, timedelta, timezone
from src.decisionassure_impact.drift import DriftDetector
from src.decisionassure_impact.models.admissibility import GovernanceState

def test_drift_detection():
    snapshot = GovernanceState(
        policy_version="v4",
        authority_chain=["delegation_123"],
        evidence_age_hours=0.5,
        model_version="approved_v1",
        timestamp=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    detector = DriftDetector(drift_threshold_hours=1.0)
    result = detector.detect_drift(snapshot, "v5", {"delegations": []})
    assert result["is_drifted"] is True
    assert len(result["drift_events"]) > 0
import pytest
import uuid
from datetime import datetime, timezone
from src.decisionassure_impact.engine import ImpactEngine
from src.decisionassure_impact.models.trace import TraceBatch, DecisionTrace, Action
from src.decisionassure_impact.models.impact import ImpactReport

def create_single_decision_trace(amount, risk_score=25):
    action = Action(
        id=uuid.uuid4(),
        name="refund",
        parameters={"amount": amount},
        tool="payment-api",
        version="v3",
        transaction_amount=amount
    )
    decision = DecisionTrace(
        action=action,
        agent_id=uuid.uuid4(),
        agent_version="1.0",
        timestamp=datetime.now(timezone.utc),
        policy_version="v4",
        authority_chain=["delegation_123"],
        context={"risk_score": risk_score, "evidence_age_hours": 0.5},
        evidence_used=[],
        evidence_age_hours=0.5,
        tool_permissions_at_time=["read"],
        model_version="approved_v1",
        result="ALLOW"
    )
    trace = TraceBatch(
        trace_id=uuid.uuid4(),
        decisions=[decision],
        environment={},
        metadata={}
    )
    return [trace]

def test_impact_engine_policy_change():
    traces = create_single_decision_trace(amount=45000)
    engine = ImpactEngine(traces)

    curr_policy = {
        "version": "v4",
        "rules": [{"condition": "action.parameters.get('amount',0) <= 50000", "effect": "ALLOW", "priority": 5}],
        "default_effect": "DENY"
    }
    prop_policy = {
        "version": "v5",
        "rules": [{"condition": "action.parameters.get('amount',0) <= 40000", "effect": "ALLOW", "priority": 5}],
        "default_effect": "DENY"
    }
    authority = {"delegations": [], "global_tool_capabilities": {}}

    report = engine.analyze_impact(curr_policy, authority, prop_policy, authority)
    assert report.transitions.admissible_to_inadmissible == 1
    assert report.total_decisions_evaluated == 1
    assert report.recommendation == "BLOCK"

def test_impact_engine_no_change():
    traces = create_single_decision_trace(amount=30000)
    engine = ImpactEngine(traces)

    curr_policy = {
        "version": "v4",
        "rules": [{"condition": "action.parameters.get('amount',0) <= 50000", "effect": "ALLOW", "priority": 5}],
        "default_effect": "DENY"
    }
    prop_policy = curr_policy.copy()
    authority = {"delegations": [], "global_tool_capabilities": {}}

    report = engine.analyze_impact(curr_policy, authority, prop_policy, authority)
    assert report.transitions.unchanged == 1
    assert report.recommendation == "ALLOW"
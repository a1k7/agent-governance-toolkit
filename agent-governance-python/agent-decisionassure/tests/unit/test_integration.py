# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import json

import pytest

from agent_decisionassure.integration import analyze_impact_for_pr


def _fixtures(tmp_path):
    traces = tmp_path / "traces.jsonl"
    traces.write_text(json.dumps({
        "trace_id": "00000000-0000-4000-8000-000000000001",
        "decisions": [{
            "action": {
                "id": "00000000-0000-4000-8000-000000000002",
                "name": "refund",
                "parameters": {"amount": 45000},
                "tool": "payment-api",
                "version": "v3",
                "transaction_amount": 200000,
            },
            "agent_id": "00000000-0000-4000-8000-000000000003",
            "agent_version": "1.0",
            "timestamp": "2026-09-03T12:00:00+00:00",
            "policy_version": "v4",
            "authority_chain": ["delegation_123"],
            "context": {"risk_score": 35, "model_version": "approved_v1"},
            "evidence_used": [],
            "evidence_age_hours": 0.5,
            "tool_permissions_at_time": ["read"],
            "model_version": "approved_v1",
            "result": "ALLOW",
        }],
        "environment": {},
        "metadata": {},
    }) + "\n")

    policy4 = tmp_path / "p4.yaml"
    policy4.write_text(
        "version: v4\n"
        "rules:\n"
        "  - priority: 10\n"
        "    condition:\n"
        "      lt: [{field: context.risk_score}, 30]\n"
        "    effect: ALLOW\n"
        "  - priority: 5\n"
        "    condition:\n"
        "      all:\n"
        "        - eq: [{field: action.name}, refund]\n"
        "        - lte: [{field: action.parameters.amount}, 50000]\n"
        "    effect: ALLOW\n"
        "default_effect: DENY\n"
    )
    policy5 = tmp_path / "p5.yaml"
    policy5.write_text(
        "version: v5\n"
        "rules:\n"
        "  - priority: 10\n"
        "    condition:\n"
        "      lt: [{field: context.risk_score}, 30]\n"
        "    effect: ALLOW\n"
        "  - priority: 5\n"
        "    condition:\n"
        "      all:\n"
        "        - eq: [{field: action.name}, refund]\n"
        "        - lte: [{field: action.parameters.amount}, 40000]\n"
        "    effect: ALLOW\n"
        "default_effect: DENY\n"
    )
    auth = tmp_path / "auth.yaml"
    auth.write_text(
        "delegations:\n"
        "  - id: delegation_123\n"
        "    permissions: [refund]\n"
        "    valid_from: '2026-01-01T00:00:00+00:00'\n"
        "    valid_until: '2027-01-01T00:00:00+00:00'\n"
        "global_tool_capabilities:\n"
        "  payment-api: [read, write]\n"
    )
    return traces, policy4, policy5, auth


def test_analyze_impact_for_pr_shared_authority(tmp_path):
    traces, p4, p5, auth = _fixtures(tmp_path)
    report = analyze_impact_for_pr(
        current_policy_path=str(p4),
        proposed_policy_path=str(p5),
        traces_path=str(traces),
        authority_shared_path=str(auth),
    )
    assert report["transitions"]["admissible_to_inadmissible"] == 1
    assert report["recommendation"] == "BLOCK"


def test_analyze_impact_for_pr_two_authorities(tmp_path):
    traces, p4, p5, auth = _fixtures(tmp_path)
    report = analyze_impact_for_pr(
        current_policy_path=str(p4),
        proposed_policy_path=str(p4),
        traces_path=str(traces),
        authority_current_path=str(auth),
        authority_proposed_path=str(auth),
    )
    assert report["transitions"]["unchanged"] == 1


def test_analyze_impact_for_pr_requires_authority(tmp_path):
    traces, p4, p5, auth = _fixtures(tmp_path)
    with pytest.raises(ValueError):
        analyze_impact_for_pr(
            current_policy_path=str(p4),
            proposed_policy_path=str(p5),
            traces_path=str(traces),
        )

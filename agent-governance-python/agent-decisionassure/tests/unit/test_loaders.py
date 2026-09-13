# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import json

import pytest

from agent_decisionassure.loaders import (
    AuthorityError,
    PolicyError,
    TraceError,
    load_authority,
    load_policy,
    load_traces,
)


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return p


def test_policy_empty_file_fails(tmp_path):
    with pytest.raises(PolicyError):
        load_policy(_write(tmp_path, "p.yaml", ""))


def test_policy_bad_rules_fails(tmp_path):
    with pytest.raises(PolicyError):
        load_policy(_write(tmp_path, "p.yaml", "version: v1\nrules: not-a-list\n"))


def test_policy_int_version_fails(tmp_path):
    with pytest.raises(PolicyError):
        load_policy(_write(tmp_path, "p.yaml", "version: 1\nrules: []\n"))


def test_policy_bad_condition_fails(tmp_path):
    with pytest.raises(PolicyError):
        load_policy(_write(tmp_path, "p.yaml",
            "version: v1\nrules:\n  - condition:\n      frobnicate: [1, 2]\n    effect: ALLOW\n"))


def test_policy_good_loads(tmp_path):
    p = _write(tmp_path, "p.yaml",
        "version: v1\nrules:\n"
        "  - priority: 10\n    condition:\n      lt: [{field: context.risk_score}, 30]\n    effect: ALLOW\n"
        "default_effect: DENY\n")
    out = load_policy(p)
    assert out["version"] == "v1"


def test_authority_empty_fails(tmp_path):
    with pytest.raises(AuthorityError):
        load_authority(_write(tmp_path, "a.yaml", ""))


def test_authority_no_delegations_fails(tmp_path):
    with pytest.raises(AuthorityError):
        load_authority(_write(tmp_path, "a.yaml", "delegations: []\n"))


def test_authority_good_loads(tmp_path):
    p = _write(tmp_path, "a.yaml",
        "delegations:\n"
        "  - id: d1\n    permissions: [refund]\n"
        "    valid_from: '2026-01-01T00:00:00+00:00'\n"
        "    valid_until: '2027-01-01T00:00:00+00:00'\n")
    out = load_authority(p)
    assert out["delegations"][0]["id"] == "d1"


def _good_trace():
    return {
        "trace_id": "00000000-0000-4000-8000-000000000001",
        "decisions": [{
            "action": {
                "id": "00000000-0000-4000-8000-000000000002",
                "name": "refund",
                "parameters": {"amount": 1000},
                "tool": "payment-api",
                "version": "v3",
                "transaction_amount": 1000,
            },
            "agent_id": "00000000-0000-4000-8000-000000000003",
            "agent_version": "1.0",
            "timestamp": "2026-09-03T12:00:00+00:00",
            "policy_version": "v4",
            "authority_chain": ["delegation_123"],
            "context": {"risk_score": 25, "evidence_age_hours": 0.5},
            "evidence_used": [],
            "evidence_age_hours": 0.5,
            "tool_permissions_at_time": ["read"],
            "model_version": "approved_v1",
            "result": "ALLOW",
        }],
        "environment": {},
        "metadata": {},
    }


@pytest.mark.parametrize("bad", [
    "null",
    "[]",
    "42",
    '"a string"',
    '{"trace_id": "not-a-uuid", "decisions": []}',
    '{"trace_id": "00000000-0000-4000-8000-000000000001", "decisions": "oops"}',
    '{"trace_id": "00000000-0000-4000-8000-000000000001", "decisions": []}',
])
def test_trace_bad_shapes_fail(tmp_path, bad):
    with pytest.raises(TraceError):
        load_traces(_write(tmp_path, "t.jsonl", bad + "\n"))


def test_trace_empty_file_fails(tmp_path):
    with pytest.raises(TraceError):
        load_traces(_write(tmp_path, "t.jsonl", ""))


def test_trace_good_loads(tmp_path):
    p = _write(tmp_path, "t.jsonl", json.dumps(_good_trace()) + "\n")
    out = load_traces(p)
    assert len(out) == 1
    assert out[0].decisions[0].action.name == "refund"

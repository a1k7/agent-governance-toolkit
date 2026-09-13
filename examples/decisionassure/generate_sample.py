# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Generate a fully deterministic synthetic trace fixture (seed=42)."""
import json
import random
import uuid
from pathlib import Path

FIXED_TS = "2026-09-03T12:00:00+00:00"
SEED = 42
OUT = Path(__file__).parent / "sample_traces.jsonl"


def _uuid_from_rng(rng: random.Random) -> uuid.UUID:
    """Deterministic UUIDv4 derived from the seeded RNG."""
    return uuid.UUID(int=rng.getrandbits(128), version=4)


def generate_trace(rng, num_decisions=5):
    trace_id = str(_uuid_from_rng(rng))
    decisions = []
    for _ in range(num_decisions):
        amount = rng.randint(30000, 60000)
        risk_score = rng.randint(20, 50)
        action = {
            "id": str(_uuid_from_rng(rng)),
            "name": "refund",
            "parameters": {"amount": amount},
            "tool": "payment-api",
            "version": "v3",
            "transaction_amount": amount,
        }
        decision = {
            "action": action,
            "agent_id": str(_uuid_from_rng(rng)),
            "agent_version": "1.2",
            "timestamp": FIXED_TS,
            "policy_version": "v4",
            "authority_chain": ["delegation_123"],
            "context": {
                "risk_score": risk_score,
                "evidence_age_hours": rng.choice([0.5, 1.0, 2.0]),
                "model_version": "approved_v1",
            },
            "evidence_used": [str(_uuid_from_rng(rng))],
            "result": "ALLOW" if rng.random() > 0.3 else "DENY",
            "tool_permissions_at_time": ["read"],
            "model_version": "approved_v1",
        }
        decisions.append(decision)
    return {
        "trace_id": trace_id,
        "decisions": decisions,
        "environment": {"model_version": "approved_v1"},
        "metadata": {},
    }


if __name__ == "__main__":
    rng = random.Random(SEED)
    traces = [generate_trace(rng, rng.randint(1, 5)) for _ in range(100)]
    with OUT.open("w", encoding="utf-8") as f:
        for trace in traces:
            f.write(json.dumps(trace) + "\n")
    print(f"Wrote {len(traces)} traces to {OUT} (seed={SEED})")

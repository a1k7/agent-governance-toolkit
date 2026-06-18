import pytest
from agent_os.continuity import ContinuityVerifier
import random

def random_context():
    return {
        "agent_id": f"agent_{random.randint(0,1000)}",
        "session_id": f"session_{random.randint(0,100)}",
        "memory_state": {"step": random.randint(0,100)},
        "policy_version": f"v{random.randint(1,5)}",
        "delegation_chain": ["root", f"delegate_{random.randint(1,3)}"],
        "evidence_state": {"nonce": random.randint(0,10000)},
    }

def test_false_admits():
    false_admits = 0
    for _ in range(100_000):
        verifier = ContinuityVerifier("test")
        pre = random_context()
        verifier.capture_pre_state(**pre)
        # Mutate exactly one field
        post = dict(pre)
        field = random.choice(["agent_id", "policy_version", "delegation_chain", "evidence_state"])
        if field == "agent_id":
            post["agent_id"] = pre["agent_id"] + "_mutated"
        elif field == "policy_version":
            post["policy_version"] = pre["policy_version"] + "_mutated"
        elif field == "delegation_chain":
            post["delegation_chain"] = pre["delegation_chain"] + ["mutated"]
        else:
            post["evidence_state"] = {**pre["evidence_state"], "nonce": pre["evidence_state"]["nonce"] + 1}
        trace = verifier.capture_post_state(**post)
        if trace.admissible:
            false_admits += 1
    assert false_admits == 0, f"False admits: {false_admits}"

def test_false_denies():
    false_denies = 0
    for _ in range(100_000):
        verifier = ContinuityVerifier("test")
        context = random_context()
        verifier.capture_pre_state(**context)
        trace = verifier.capture_post_state(**context)
        if not trace.admissible:
            false_denies += 1
    assert false_denies == 0, f"False denies: {false_denies}"
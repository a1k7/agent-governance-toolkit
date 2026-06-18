#!/usr/bin/env python3
"""
Simplified demo showing the "approval is not enough" vulnerability and how
continuity verification (Nanogate) fixes it.
"""

import time
import hashlib
import json

# ----------------------------------------------------------------------
# Minimal continuity verifier (stub of Nanogate)
# ----------------------------------------------------------------------
class ContinuityVerifier:
    def __init__(self, execution_id):
        self.execution_id = execution_id
        self.pre_hash = None

    def compute_hash(self, identity, policy, delegation, evidence):
        data = json.dumps({
            "identity": identity,
            "policy": policy,
            "delegation": delegation,
            "evidence": evidence
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def capture_pre_state(self, identity, policy, delegation, evidence):
        self.pre_hash = self.compute_hash(identity, policy, delegation, evidence)

    def capture_post_state(self, identity, policy, delegation, evidence):
        post_hash = self.compute_hash(identity, policy, delegation, evidence)
        valid = (self.pre_hash == post_hash)
        return {"continuity_valid": valid, "decision": "ALLOW" if valid else "DENY"}

# ----------------------------------------------------------------------
# Simple tool function
# ----------------------------------------------------------------------
def execute_query(query):
    return f"Executed: {query}"

# ----------------------------------------------------------------------
# Simulate policy change
# ----------------------------------------------------------------------
policy_version = "v1"
def get_policy():
    return policy_version

def set_policy(new_version):
    global policy_version
    policy_version = new_version

# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
def main():
    print("=== WITHOUT CONTINUITY ===")
    # First call (policy v1)
    print("First call (allowed):", execute_query("SELECT * FROM users"))
    # Simulate policy change mid-flight
    set_policy("v2")
    print("Policy changed to v2")
    # Second call – still allowed, unsafe
    print("Second call (still allowed, but unsafe):", execute_query("DELETE FROM users"))

    print("\n=== WITH CONTINUITY (Nanogate) ===")
    set_policy("v1")
    verifier = ContinuityVerifier("demo")
    # Pre-state capture
    identity = "agent_alice"
    delegation = ["root"]
    evidence = {"timestamp": time.time()}
    verifier.capture_pre_state(identity, get_policy(), delegation, evidence)
    # First execution
    print("First call (allowed):", execute_query("SELECT * FROM users"))
    # Simulate policy change
    set_policy("v2")
    print("Policy changed to v2")
    # Post-state capture – drift detected
    trace = verifier.capture_post_state(identity, get_policy(), delegation, evidence)
    if not trace["continuity_valid"]:
        print(f"Continuity drift detected! Decision: {trace['decision']} -> Execution DENIED")
    else:
        print("Second call (should be denied, but continuity passed – unexpected)")

if __name__ == "__main__":
    main()
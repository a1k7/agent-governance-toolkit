#!/usr/bin/env python3
"""
Standalone demo of Continuous Admissibility and Governance Flight Recorder.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class AdmissibilitySnapshot:
    identity_hash: str
    policy_hash: str
    delegation_hash: str
    evidence_hash: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ContinuityTrace:
    execution_id: str
    admissible: bool
    decision: str
    identity_hash: str
    policy_hash: str
    delegation_hash: str
    evidence_hash: str
    diff: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, default=str)


class ContinuityVerifier:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._pre: Optional[AdmissibilitySnapshot] = None

    def _hash_obj(self, obj: Any) -> str:
        canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def capture_pre_state(self, agent_id, session_id, memory_state, policy_version, delegation_chain, evidence_state):
        identity_hash = self._hash_obj({"agent_id": agent_id, "session_id": session_id, "memory_state": memory_state})
        policy_hash = self._hash_obj(policy_version)
        delegation_hash = self._hash_obj(delegation_chain)
        evidence_hash = self._hash_obj(evidence_state)
        self._pre = AdmissibilitySnapshot(identity_hash, policy_hash, delegation_hash, evidence_hash)

    def capture_post_state(self, agent_id, session_id, memory_state, policy_version, delegation_chain, evidence_state):
        if self._pre is None:
            raise RuntimeError("pre‑state not captured")
        identity_hash = self._hash_obj({"agent_id": agent_id, "session_id": session_id, "memory_state": memory_state})
        policy_hash = self._hash_obj(policy_version)
        delegation_hash = self._hash_obj(delegation_chain)
        evidence_hash = self._hash_obj(evidence_state)
        admissible = (identity_hash == self._pre.identity_hash and policy_hash == self._pre.policy_hash and
                      delegation_hash == self._pre.delegation_hash and evidence_hash == self._pre.evidence_hash)
        diff = None
        if not admissible:
            diff = {}
            if identity_hash != self._pre.identity_hash:
                diff["identity"] = {"old": self._pre.identity_hash, "new": identity_hash}
            if policy_hash != self._pre.policy_hash:
                diff["policy"] = {"old": self._pre.policy_hash, "new": policy_hash}
            if delegation_hash != self._pre.delegation_hash:
                diff["delegation"] = {"old": self._pre.delegation_hash, "new": delegation_hash}
            if evidence_hash != self._pre.evidence_hash:
                diff["evidence"] = {"old": self._pre.evidence_hash, "new": evidence_hash}
        return ContinuityTrace(self.execution_id, admissible, "ALLOW" if admissible else "DENY",
                               identity_hash, policy_hash, delegation_hash, evidence_hash, diff)


def transfer_funds(amount: float, to_account: str) -> str:
    return f"Transferred ${amount} to {to_account}"

_DELEGATION_CHAIN = ["root", "delegate_alice"]

def get_delegation_chain():
    return _DELEGATION_CHAIN.copy()

def revoke_delegation():
    global _DELEGATION_CHAIN
    _DELEGATION_CHAIN = ["root"]

def grant_delegation():
    global _DELEGATION_CHAIN
    _DELEGATION_CHAIN = ["root", "delegate_alice"]

def main():
    grant_delegation()
    print("Initial delegation:", get_delegation_chain())
    print("\n=== WITHOUT CONTINUITY ===")
    print("First call (allowed):", transfer_funds(1000, "vendor"))
    revoke_delegation()
    print("Delegation revoked (new chain):", get_delegation_chain())
    print("Second call (still allowed, unsafe):", transfer_funds(1000, "vendor"))

    grant_delegation()
    print("\n=== WITH CONTINUITY (Continuous Admissibility) ===")
    verifier = ContinuityVerifier("demo")
    context = {"agent_id": "alice", "session_id": "s1", "memory_state": {},
               "policy_version": "v1", "delegation_chain": get_delegation_chain(), "evidence_state": {"fresh": True}}
    verifier.capture_pre_state(**context)
    print("First call (allowed):", transfer_funds(1000, "vendor"))
    revoke_delegation()
    print("Delegation revoked")
    context["delegation_chain"] = get_delegation_chain()
    trace = verifier.capture_post_state(**context)
    if trace.admissible:
        print("Second call (unexpectedly allowed):", transfer_funds(1000, "vendor"))
    else:
        print(f"Continuity drift detected – {trace.decision}. Flight recorder:\n{trace.to_json()}")

if __name__ == "__main__":
    main()

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""
Continuous Admissibility Verifier for AGT.

Formal Definition:
    A request is continuously admissible iff:
        identity_t == identity_approval
        policy_version_t == policy_version_approval
        delegation_chain_t == delegation_chain_approval
        evidence_hash_t == evidence_hash_approval

If any of these change between approval and execution, the gate denies.
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
    """Replayable proof of admissibility (the "flight recorder")."""
    execution_id: str
    admissible: bool
    decision: str  # "ALLOW" or "DENY"
    identity_hash: str
    policy_hash: str
    delegation_hash: str
    evidence_hash: str
    diff: Optional[Dict[str, Any]] = None
    recommended_action: Optional[str] = None
    control_objective: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, default=str)


class ContinuityVerifier:
    """
    Pre‑/post‑execution verifier for continuous admissibility.
    Use:
        verifier = ContinuityVerifier(execution_id)
        verifier.capture_pre_state(...)
        # ... execute tool ...
        trace = verifier.capture_post_state(...)
        if not trace.admissible:
            raise GovernanceDenied(...)
    """

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._pre: Optional[AdmissibilitySnapshot] = None

    def _hash_obj(self, obj: Any) -> str:
        """Deterministic SHA‑256 of any JSON‑serializable object."""
        canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def capture_pre_state(
        self,
        agent_id: str,
        session_id: str,
        memory_state: Dict,
        policy_version: str,
        delegation_chain: list,
        evidence_state: Dict,
    ) -> None:
        """Capture approval‑time context."""
        identity_hash = self._hash_obj({
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_state": memory_state,
        })
        policy_hash = self._hash_obj(policy_version)
        delegation_hash = self._hash_obj(delegation_chain)
        evidence_hash = self._hash_obj(evidence_state)
        self._pre = AdmissibilitySnapshot(
            identity_hash, policy_hash, delegation_hash, evidence_hash
        )

    def capture_post_state(
        self,
        agent_id: str,
        session_id: str,
        memory_state: Dict,
        policy_version: str,
        delegation_chain: list,
        evidence_state: Dict,
    ) -> ContinuityTrace:
        """Compare execution‑time context with approval‑time snapshot."""
        if self._pre is None:
            raise RuntimeError("pre‑state not captured; call capture_pre_state first")

        identity_hash = self._hash_obj({
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_state": memory_state,
        })
        policy_hash = self._hash_obj(policy_version)
        delegation_hash = self._hash_obj(delegation_chain)
        evidence_hash = self._hash_obj(evidence_state)

        identity_ok = identity_hash == self._pre.identity_hash
        policy_ok = policy_hash == self._pre.policy_hash
        delegation_ok = delegation_hash == self._pre.delegation_hash
        evidence_ok = evidence_hash == self._pre.evidence_hash

        admissible = identity_ok and policy_ok and delegation_ok and evidence_ok

        diff = None
        recommended = None
        control = None
        if not admissible:
            diff = {}
            if not identity_ok:
                diff["identity"] = {"old": self._pre.identity_hash, "new": identity_hash}
            if not policy_ok:
                diff["policy"] = {"old": self._pre.policy_hash, "new": policy_hash}
            if not delegation_ok:
                diff["delegation"] = {"old": self._pre.delegation_hash, "new": delegation_hash}
            if not evidence_ok:
                diff["evidence"] = {"old": self._pre.evidence_hash, "new": evidence_hash}
            recommended = "reauthorize"
            control = "CO-001"  # authority continuity

        return ContinuityTrace(
            execution_id=self.execution_id,
            admissible=admissible,
            decision="ALLOW" if admissible else "DENY",
            identity_hash=identity_hash,
            policy_hash=policy_hash,
            delegation_hash=delegation_hash,
            evidence_hash=evidence_hash,
            diff=diff,
            recommended_action=recommended,
            control_objective=control,
        )
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Continuity verification primitives.

This module captures pre-/post-execution hashes of an agent's observer identity
and reference frame and reports drift as a structured trace.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256_hex(payload: Any) -> str:
    digest = hashlib.sha256(_canonical_json(payload)).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class ContinuityTrace:
    execution_id: str
    admissible: bool
    decision: str
    observer_identity_hash: str
    reference_frame_hash: str
    diff: dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ContinuityVerifier:
    """Captures continuity state before/after execution and detects drift."""

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._pre_observer_snapshot: bytes | None = None
        self._pre_reference_snapshot: bytes | None = None
        self._pre_observer_dict: dict | None = None
        self._pre_reference_dict: dict | None = None

    def capture_pre_state(
        self,
        *,
        agent_id: str,
        session_id: str,
        memory_state: Any,
        policy_version: str,
        delegation_chain: Any,
        evidence_state: Any,
    ) -> None:
        observer = {
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_state": memory_state,
        }
        reference = {
            "policy_version": policy_version,
            "delegation_chain": delegation_chain,
            "evidence_state": evidence_state,
        }
        # Store deep copies to avoid in-place mutation affecting diff
        self._pre_observer_dict = copy.deepcopy(observer)
        self._pre_reference_dict = copy.deepcopy(reference)
        self._pre_observer_snapshot = _canonical_json(observer)
        self._pre_reference_snapshot = _canonical_json(reference)

    def capture_post_state(
        self,
        *,
        agent_id: str,
        session_id: str,
        memory_state: Any,
        policy_version: str,
        delegation_chain: Any,
        evidence_state: Any,
    ) -> ContinuityTrace:
        if self._pre_observer_snapshot is None or self._pre_reference_snapshot is None:
            raise ValueError("capture_pre_state() must be called before capture_post_state()")

        observer = {
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_state": memory_state,
        }
        reference = {
            "policy_version": policy_version,
            "delegation_chain": delegation_chain,
            "evidence_state": evidence_state,
        }

        post_observer_snapshot = _canonical_json(observer)
        post_reference_snapshot = _canonical_json(reference)

        admissible = (post_observer_snapshot == self._pre_observer_snapshot) and (
            post_reference_snapshot == self._pre_reference_snapshot
        )

        # Build diff by comparing the stored pre-state dicts (deep copies) with the current ones.
        diff: dict[str, Any] = {}
        pre_observer = self._pre_observer_dict
        pre_reference = self._pre_reference_dict

        if pre_observer and (pre_observer.get("agent_id") != observer.get("agent_id") or
                             pre_observer.get("session_id") != observer.get("session_id")):
            diff["identity"] = {
                "old": {
                    "agent_id": pre_observer.get("agent_id"),
                    "session_id": pre_observer.get("session_id"),
                },
                "new": {
                    "agent_id": observer.get("agent_id"),
                    "session_id": observer.get("session_id"),
                },
            }

        if pre_observer and pre_observer.get("memory_state") != observer.get("memory_state"):
            diff["memory"] = {
                "old": pre_observer.get("memory_state"),
                "new": observer.get("memory_state"),
            }

        if pre_reference and pre_reference.get("policy_version") != reference.get("policy_version"):
            diff["policy"] = {
                "old": pre_reference.get("policy_version"),
                "new": reference.get("policy_version"),
            }

        if pre_reference and pre_reference.get("delegation_chain") != reference.get("delegation_chain"):
            diff["delegation"] = {
                "old": pre_reference.get("delegation_chain"),
                "new": reference.get("delegation_chain"),
            }

        if pre_reference and pre_reference.get("evidence_state") != reference.get("evidence_state"):
            diff["evidence"] = {
                "old": pre_reference.get("evidence_state"),
                "new": reference.get("evidence_state"),
            }

        decision = "ALLOW" if admissible else "DENY"

        return ContinuityTrace(
            execution_id=self.execution_id,
            admissible=admissible,
            decision=decision,
            observer_identity_hash=_sha256_hex(observer),
            reference_frame_hash=_sha256_hex(reference),
            diff=diff,
        )
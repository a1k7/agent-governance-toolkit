# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Extract current governance context from AGT runtime for continuity verification."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


# Placeholder functions – to be replaced with actual AGT runtime APIs.
# Maintainers should wire these to the live agent context (DID, session, policy, delegation, evidence).
def _get_agent_id() -> str:
    raise NotImplementedError(
        "Must wire to AGT runtime: get current agent ID (DID)."
    )


def _get_session_id() -> str:
    raise NotImplementedError(
        "Must wire to AGT runtime: get current session ID."
    )


def _get_policy_version() -> str:
    raise NotImplementedError(
        "Must wire to AGT runtime: get active policy version."
    )


def _get_delegation_chain() -> list:
    raise NotImplementedError(
        "Must wire to AGT runtime: get current delegation chain."
    )


def _get_evidence_state() -> Dict[str, Any]:
    raise NotImplementedError(
        "Must wire to AGT runtime: get evidence freshness, timestamp, etc."
    )


def get_execution_context() -> Dict[str, Any]:
    """
    Returns the current governance context from the live AGT runtime.

    This is used for continuity verification (pre‑/post‑execution hashing).
    It captures:
    - agent_id: the agent's DID or stable identifier
    - session_id: current session ID
    - policy_version: the policy version active at execution time
    - delegation_chain: the current delegation chain (scope)
    - evidence_state: a dict containing evidence freshness, timestamp, etc.

    Raises:
        RuntimeError: if the runtime context is not available.
        NotImplementedError: if the helper functions are not wired.
    """
    try:
        return {
            "agent_id": _get_agent_id(),
            "session_id": _get_session_id(),
            "memory_state": {},  # future extension for memory state if needed
            "policy_version": _get_policy_version(),
            "delegation_chain": _get_delegation_chain(),
            "evidence_state": _get_evidence_state(),
        }
    except NotImplementedError as e:
        # Re-raise with a clear message for maintainers.
        raise RuntimeError(
            "Continuity verification is not wired to the AGT runtime. "
            "Please implement the helper functions in continuity_helpers.py "
            "to fetch live agent identity, policy, delegation, and evidence."
        ) from e
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Extract current governance context from AGT runtime for continuity verification."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


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
        RuntimeError: always – this is a placeholder that must be wired to the
            actual AGT runtime by the maintainers.
    """
    raise RuntimeError(
        "continuity_helpers.get_execution_context() is not wired to the AGT runtime. "
        "Please implement this function to fetch the live agent identity, "
        "policy version, delegation chain, and evidence state from the running "
        "agent context (e.g., AgentMesh identity, PolicyEngine, current scope)."
    )
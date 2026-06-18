# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Governance decorator with optional continuous admissibility."""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from agent_os.continuity import ContinuityVerifier
from agent_os.exceptions import GovernanceDenied
from agent_os.policy_engine import PolicyEngine
from agentmesh.continuity_helpers import get_execution_context

logger = logging.getLogger(__name__)


def govern(
    tool_func: Callable,
    policy: Union[PolicyEngine, Dict, str],
    *,
    enable_continuity: bool = False,
    enforcement_mode: str = "enforce",
) -> Callable:
    if not isinstance(policy, PolicyEngine):
        # In production, load policy from file or dict
        policy = PolicyEngine.from_dict(policy) if isinstance(policy, dict) else PolicyEngine()

    @wraps(tool_func)
    def wrapper(*args, **kwargs):
        # 1. Capture pre‑state (if continuity enabled)
        verifier = None
        if enable_continuity:
            verifier = ContinuityVerifier(execution_id=f"{tool_func.__name__}-{id(tool_func)}")
            ctx = get_execution_context()
            verifier.capture_pre_state(**ctx)

        # 2. Evaluate policy (actual AGT policy evaluation)
        action_context = {"action": kwargs.get("action", tool_func.__name__), "args": args, "kwargs": kwargs}
        decision = policy.evaluate(action_context)
        if decision != "allow":
            raise GovernanceDenied(f"Policy denied: {decision}")

        # 3. Execute tool
        try:
            result = tool_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise

        # 4. Post‑execution continuity check
        if verifier is not None:
            ctx = get_execution_context()   # re‑fetch (may have changed)
            trace = verifier.capture_post_state(**ctx)
            if not trace.admissible:
                msg = f"Continuity drift: {trace.diff}"
                if enforcement_mode == "enforce":
                    raise GovernanceDenied(msg)
                else:
                    logger.warning(msg)
        return result

    return wrapper
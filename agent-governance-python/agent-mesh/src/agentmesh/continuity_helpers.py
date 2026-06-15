# Placeholder – in a real AGT integration, this would read from AGT's state.
from typing import Any, Dict

_DELEGATION_CHAIN = ["root"]
# This is a stub; in a real AGT integration, this would read from AGT's internal state.
def get_execution_context():
    # This function will be implemented by AGT maintainers to return current governance context.
    raise NotImplementedError("To use continuity, implement get_execution_context() with AGT's identity, policy, delegation, and evidence.")
def set_delegation_chain(chain):
    global _DELEGATION_CHAIN
    _DELEGATION_CHAIN = chain

def get_delegation_chain():
    return _DELEGATION_CHAIN

def get_execution_context() -> Dict[str, Any]:
    return {
        "agent_id": "current-agent",
        "session_id": "current-session",
        "memory_state": {},
        "policy_version": "current-policy",
        "delegation_chain": get_delegation_chain(),
        "evidence_state": {"evidence_hash": "fresh"},
    }
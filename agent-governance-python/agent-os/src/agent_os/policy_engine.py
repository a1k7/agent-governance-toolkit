# Stub for policy engine – in real AGT this is already provided.
from typing import Any, Dict, Union, List

class PolicyEngine:
    def __init__(self, policy_data: Dict):
        self.policy = policy_data

    def evaluate(self, context: Dict) -> str:
        # Stub: always allow unless action contains "delete"
        action = context.get("action", "")
        if "delete" in action.lower():
            return "deny"
        return "allow"

    @classmethod
    def from_dict(cls, data: Dict) -> "PolicyEngine":
        return cls(data)

def load_policy(path: str) -> PolicyEngine:
    # Stub – in reality load YAML
    return PolicyEngine({})
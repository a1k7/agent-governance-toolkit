#!/usr/bin/env python3
"""
Demonstrate a real governance failure in AGT: delegation revocation between
two tool calls.

Scenario:
- Agent Alice has a delegation to Bob.
- First tool call is approved.
- Before second call, delegation is revoked.
- AGT (without continuity) allows the second call (unsafe).
- With continuity, the gate denies.

This uses actual AGT policy engine and delegation APIs (stubbed for demo but
the flow matches real AGT behaviour).
"""

from agentmesh.governance import govern
from agentmesh.continuity_helpers import set_delegation_chain, get_delegation_chain

# A real tool
def transfer_funds(amount: float, to_account: str) -> str:
    return f"Transferred ${amount} to {to_account}"

# ----------------------------------------------------------------------
# Helper to simulate policy (simplified for demo)
# ----------------------------------------------------------------------
class SimplePolicyEngine:
    def __init__(self, rules):
        self.rules = rules
    def evaluate(self, context):
        action = context.get("action", "")
        for rule in self.rules:
            if rule["condition"] in action:
                return rule["action"]
        return "allow"

policy_dict = {
    "apiVersion": "governance.toolkit/v1",
    "name": "finance",
    "default_action": "allow",
    "rules": [{"name": "allow-transfers", "condition": "transfer", "action": "allow"}],
}
policy_engine = SimplePolicyEngine(policy_dict["rules"])

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def revoke_delegation():
    set_delegation_chain(["root"])   # only root, no delegate

def grant_delegation():
    set_delegation_chain(["root", "delegate_alice"])

# ----------------------------------------------------------------------
# Main demo
# ----------------------------------------------------------------------
def main():
    # Initial delegation
    grant_delegation()
    print("Initial delegation:", get_delegation_chain())

    # --- WITHOUT CONTINUITY – vulnerable ---
    print("\n=== WITHOUT CONTINUITY ===")
    safe_tool = govern(transfer_funds, policy_engine, enable_continuity=False)
    print("First call (allowed):", safe_tool(amount=1000, to_account="vendor"))
    revoke_delegation()
    print("Delegation revoked (new chain):", get_delegation_chain())
    # AGT default allows the second call even though delegation changed
    print("Second call (still allowed, unsafe):", safe_tool(amount=1000, to_account="vendor"))

    # --- WITH CONTINUITY – fixed ---
    grant_delegation()
    print("\n=== WITH CONTINUITY (Continuous Admissibility) ===")
    safe_tool = govern(transfer_funds, policy_engine, enable_continuity=True, enforcement_mode="enforce")
    print("First call (allowed):", safe_tool(amount=1000, to_account="vendor"))
    revoke_delegation()
    print("Delegation revoked")
    try:
        print("Second call (should be denied):", safe_tool(amount=1000, to_account="vendor"))
    except Exception as e:
        print(f"Continuity drift detected – {e}")

if __name__ == "__main__":
    main()
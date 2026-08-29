#!/usr/bin/env python3
"""Integration example with AGT."""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from decisionassure_impact.engine import ImpactEngine
from decisionassure_impact.cli import load_traces
from decisionassure_impact.models.impact import ImpactReport
from decisionassure_impact.drift import DriftDetector
from decisionassure_impact.models.admissibility import GovernanceState
import yaml

logging.basicConfig(level=logging.INFO)

def main():
    # 1. Load traces
    traces = load_traces("examples/sample_traces.jsonl")
    print(f"Loaded {len(traces)} traces.")

    # 2. Load policies
    with open("examples/policy_v4.yaml", "r") as f:
        curr_policy = yaml.safe_load(f)
    with open("examples/policy_v5.yaml", "r") as f:
        prop_policy = yaml.safe_load(f)

    # 3. Run impact analysis
    engine = ImpactEngine(traces)
    authority = {"delegations": [], "global_tool_capabilities": {}}
    report = engine.analyze_impact(curr_policy, authority, prop_policy, authority)

    # 4. Print summary
    print("\n=== Impact Analysis Summary ===")
    print(f"  ADMISSIBLE → INADMISSIBLE: {report.transitions.admissible_to_inadmissible}")
    print(f"  INADMISSIBLE → ADMISSIBLE: {report.transitions.inadmissible_to_admissible}")
    print(f"  Impact rate: {report.impact_rate:.2f}%")
    print(f"  Severity: {report.severity}")
    print(f"  Recommendation: {report.recommendation}")
    if report.recommendation == "BLOCK":
        print("❌ BLOCK deployment")
        sys.exit(1)
    else:
        print("✅ Deployment allowed")
        sys.exit(0)

if __name__ == "__main__":
    main()
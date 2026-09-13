# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Example: import real AGT trace data and run DecisionAssure Impact."""
from agent_decisionassure.models import TraceBatch
from agent_decisionassure.loaders import load_traces
from agent_decisionassure.engine import ImpactEngine

# Real usage: point `load_traces` at a JSONL export of AGT decisions.
# The exporter format is documented in examples/decisionassure/README.md.
# This file is intentionally minimal; it just shows the entry points.


def main(traces_path: str, policy_current: dict, policy_proposed: dict, authority: dict):
    raw = load_traces(traces_path)
    # Convert to TraceBatch objects (see cli._build_trace_batches for the full version)
    from agent_decisionassure.cli import _build_trace_batches
    batches = _build_trace_batches(raw)
    engine = ImpactEngine(batches)
    return engine.analyze_impact(policy_current, authority, policy_proposed, authority)


if __name__ == "__main__":
    print("See docstring; this example is a stub.")

# agent-decisionassure

DecisionAssure Impact — counterfactual governance replay for AGT.

All commands below assume the current directory is the repository root.

## Install

    cd agent-governance-python/agent-decisionassure
    pip install -e ".[dev]"
    cd ../..

## Generate fixtures

    python examples/decisionassure/generate_sample.py

## Run impact analysis (policy change)

    decisionassure impact --traces examples/decisionassure/sample_traces.jsonl --policy-current examples/decisionassure/policy_v4.yaml --policy-proposed examples/decisionassure/policy_v5.yaml --authority examples/decisionassure/authority_baseline.yaml

## Run impact analysis (authority change)

    decisionassure impact --traces examples/decisionassure/sample_traces.jsonl --policy-current examples/decisionassure/policy_v4.yaml --policy-proposed examples/decisionassure/policy_v4.yaml --authority-current examples/decisionassure/authority_baseline.yaml --authority-proposed examples/decisionassure/authority_proposed.yaml

## Detect evidence drift

    decisionassure detect-drift --traces examples/decisionassure/sample_traces.jsonl --drift-threshold 1.0

## Exit codes

- 0 — ALLOW
- 1 — BLOCK (or drift detected)
- 2 — input error

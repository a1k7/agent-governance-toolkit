# agent-decisionassure

DecisionAssure Impact — counterfactual governance replay for AGT.

## Install

```bash
pip install -e ".[dev]"
Generate Fixtures
python examples/decisionassure/generate_sample.py

Run Impact Analysis
decisionassure impact \
    --traces examples/decisionassure/sample_traces.jsonl \
    --policy-current examples/decisionassure/policy_v4.yaml \
    --policy-proposed examples/decisionassure/policy_v5.yaml \
    --authority examples/decisionassure/authority_baseline.yaml

To test an authority change, pass two authorities:

decisionassure impact \
    --traces examples/decisionassure/sample_traces.jsonl \
    --policy-current examples/decisionassure/policy_v4.yaml \
    --policy-proposed examples/decisionassure/policy_v4.yaml \
    --authority-current examples/decisionassure/authority_baseline.yaml \
    --authority-proposed examples/decisionassure/authority_proposed.yaml

Exit codes: 0 (allow), 1 (block), 2 (input error).


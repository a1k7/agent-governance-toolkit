# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
.PHONY: install test demo demo-authority

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

demo:
	python ../../examples/decisionassure/generate_sample.py
	decisionassure impact \
	    --traces ../../examples/decisionassure/sample_traces.jsonl \
	    --policy-current ../../examples/decisionassure/policy_v4.yaml \
	    --policy-proposed ../../examples/decisionassure/policy_v5.yaml \
	    --authority ../../examples/decisionassure/authority_baseline.yaml

demo-authority:
	decisionassure impact \
	    --traces ../../examples/decisionassure/sample_traces.jsonl \
	    --policy-current ../../examples/decisionassure/policy_v4.yaml \
	    --policy-proposed ../../examples/decisionassure/policy_v4.yaml \
	    --authority-current ../../examples/decisionassure/authority_baseline.yaml \
	    --authority-proposed ../../examples/decisionassure/authority_proposed.yaml

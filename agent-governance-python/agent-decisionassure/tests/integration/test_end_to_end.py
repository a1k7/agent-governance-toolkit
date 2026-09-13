# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from pathlib import Path

import pytest
import yaml

from agent_decisionassure.engine import ImpactEngine
from agent_decisionassure.cli import _build_trace_batches
from agent_decisionassure.loaders import load_traces


def _repo_root() -> Path:
    # tests/integration/test_end_to_end.py -> repo root is 4 levels up
    return Path(__file__).resolve().parents[4]


def test_end_to_end_replay():
    root = _repo_root()
    traces = root / "examples/decisionassure/sample_traces.jsonl"
    policy4 = root / "examples/decisionassure/policy_v4.yaml"
    policy5 = root / "examples/decisionassure/policy_v5.yaml"
    authority = root / "examples/decisionassure/authority_baseline.yaml"

    if not all(p.exists() for p in (traces, policy4, policy5, authority)):
        pytest.skip("fixtures not present; run examples/decisionassure/generate_sample.py")

    with policy4.open() as f:
        curr = yaml.safe_load(f)
    with policy5.open() as f:
        prop = yaml.safe_load(f)
    with authority.open() as f:
        auth = yaml.safe_load(f)

    batches = _build_trace_batches(load_traces(traces))
    engine = ImpactEngine(batches)
    report = engine.analyze_impact(curr, auth, prop, auth)

    affected = report.transitions.admissible_to_inadmissible + report.transitions.inadmissible_to_admissible
    assert affected > 0
    assert report.recommendation in ("BLOCK", "REVIEW")

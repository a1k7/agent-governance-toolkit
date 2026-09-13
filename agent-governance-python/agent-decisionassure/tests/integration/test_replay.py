# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import subprocess
import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    # tests/integration/test_replay.py -> repo root is 4 levels up
    return Path(__file__).resolve().parents[4]


def test_cli_impact():
    root = _repo_root()
    traces = root / "examples/decisionassure/sample_traces.jsonl"
    policy4 = root / "examples/decisionassure/policy_v4.yaml"
    policy5 = root / "examples/decisionassure/policy_v5.yaml"
    authority = root / "examples/decisionassure/authority_baseline.yaml"

    if not all(p.exists() for p in (traces, policy4, policy5, authority)):
        pytest.skip("fixtures not present; run examples/decisionassure/generate_sample.py")

    result = subprocess.run(
        [
            sys.executable, "-m", "agent_decisionassure.cli", "impact",
            "--traces", str(traces),
            "--policy-current", str(policy4),
            "--policy-proposed", str(policy5),
            "--authority", str(authority),
        ],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert result.returncode in (0, 1)
    assert "DECISIONASSURE IMPACT REPORT" in result.stdout

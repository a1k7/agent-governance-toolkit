# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Integration helpers for CI/PR gates."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .engine import ImpactEngine
from .loaders import load_authority, load_policy, load_traces

logger = logging.getLogger(__name__)


def analyze_impact_for_pr(
    current_policy_path: str,
    proposed_policy_path: str,
    traces_path: str,
    authority_current_path: Optional[str] = None,
    authority_proposed_path: Optional[str] = None,
    authority_shared_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience wrapper used by CI gates. All paths are file paths."""
    if authority_current_path and authority_proposed_path:
        baseline_auth = load_authority(authority_current_path)
        proposed_auth = load_authority(authority_proposed_path)
    elif authority_shared_path:
        baseline_auth = proposed_auth = load_authority(authority_shared_path)
    else:
        raise ValueError(
            "provide authority_shared_path or both authority_current_path and authority_proposed_path"
        )

    batches = load_traces(traces_path)
    curr = load_policy(current_policy_path)
    prop = load_policy(proposed_policy_path)
    engine = ImpactEngine(batches)
    report = engine.analyze_impact(curr, baseline_auth, prop, proposed_auth)
    return report.model_dump(mode="json", exclude_none=True)

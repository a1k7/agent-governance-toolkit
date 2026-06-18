# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""
Continuity verification bridge for AgentMesh.

Provides a simple wrapper around the ContinuityVerifier to be used in
the governance decorator and policy evaluator.
"""

from agent_os.continuity import ContinuityVerifier, ContinuityTrace

__all__ = ["ContinuityVerifier", "ContinuityTrace"]
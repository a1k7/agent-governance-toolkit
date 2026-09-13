# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Fail-closed loaders for policy, authority, and trace files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, ConfigDict, Field, UUID4, ValidationError, field_validator

from .models.trace import Action, DecisionTrace, TraceBatch
from .policy.evaluator import PolicyError as DslPolicyError, validate_condition


class PolicyError(ValueError):
    pass


class AuthorityError(ValueError):
    pass


class TraceError(ValueError):
    pass


# --------------------------------------------------------------------------
# Policy
# --------------------------------------------------------------------------
class RuleModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: int = 0
    condition: Any
    effect: str

    @field_validator("effect")
    @classmethod
    def _effect_valid(cls, v: str) -> str:
        if v not in ("ALLOW", "DENY"):
            raise ValueError(f"effect must be ALLOW or DENY, got {v!r}")
        return v


class PolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str
    rules: List[RuleModel] = Field(default_factory=list)
    default_effect: str = "DENY"

    @field_validator("version", mode="before")
    @classmethod
    def _version_str(cls, v: Any) -> str:
        if not isinstance(v, str) or not v:
            raise ValueError(f"version must be a non-empty string, got {v!r}")
        return v

    @field_validator("default_effect")
    @classmethod
    def _default_valid(cls, v: str) -> str:
        if v not in ("ALLOW", "DENY"):
            raise ValueError(f"default_effect must be ALLOW or DENY, got {v!r}")
        return v


def load_policy(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text())
    except Exception as exc:
        raise PolicyError(f"failed to parse policy YAML: {exc}") from exc
    if raw is None or not isinstance(raw, dict):
        raise PolicyError(f"policy must be a mapping, got {type(raw).__name__}")
    try:
        model = PolicyModel(**raw)
    except ValidationError as exc:
        raise PolicyError(f"invalid policy: {exc}") from exc
    for idx, rule in enumerate(model.rules):
        try:
            validate_condition(rule.condition)
        except DslPolicyError as exc:
            raise PolicyError(f"rule {idx}: {exc}") from exc
    return model.model_dump()


# --------------------------------------------------------------------------
# Authority
# --------------------------------------------------------------------------
class DelegationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    grantor: str = "unknown"
    grantee: str = "unknown"
    permissions: List[str]
    valid_from: datetime
    valid_until: datetime

    @field_validator("valid_from", "valid_until", mode="before")
    @classmethod
    def _aware(cls, v: Any) -> datetime:
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            pass
        else:
            raise ValueError(f"datetime must be a string or datetime, got {type(v).__name__}")
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v


class AuthorityModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    delegations: List[DelegationModel] = Field(default_factory=list)
    global_tool_capabilities: Dict[str, List[str]] = Field(default_factory=dict)


def load_authority(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text())
    except Exception as exc:
        raise AuthorityError(f"failed to parse authority YAML: {exc}") from exc
    if raw is None:
        raise AuthorityError("authority file is empty")
    if not isinstance(raw, dict):
        raise AuthorityError(f"authority must be a mapping, got {type(raw).__name__}")
    if not raw.get("delegations"):
        raise AuthorityError("authority has no delegations")
    try:
        model = AuthorityModel(**raw)
    except ValidationError as exc:
        raise AuthorityError(f"invalid authority: {exc}") from exc
    return model.model_dump()


# --------------------------------------------------------------------------
# Traces
# --------------------------------------------------------------------------
class ActionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID4
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    tool: str
    version: str
    transaction_amount: float | None = None


class DecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: ActionModel
    agent_id: UUID4
    agent_version: str
    timestamp: datetime
    policy_version: str
    authority_chain: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    evidence_used: List[UUID4] = Field(default_factory=list)
    evidence_age_hours: float = 0.0
    tool_permissions_at_time: List[str] = Field(default_factory=list)
    model_version: str = ""
    result: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def _aware(cls, v: Any) -> datetime:
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if not isinstance(v, datetime):
            raise ValueError(f"timestamp must be a string or datetime, got {type(v).__name__}")
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v


class TraceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: UUID4
    decisions: List[DecisionModel]
    environment: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _to_trace_batch(m: TraceModel) -> TraceBatch:
    decisions = [
        DecisionTrace(
            action=Action(
                id=d.action.id,
                name=d.action.name,
                parameters=d.action.parameters,
                tool=d.action.tool,
                version=d.action.version,
                transaction_amount=d.action.transaction_amount,
            ),
            agent_id=d.agent_id,
            agent_version=d.agent_version,
            timestamp=d.timestamp,
            policy_version=d.policy_version,
            authority_chain=d.authority_chain,
            context=d.context,
            evidence_used=d.evidence_used,
            evidence_age_hours=d.evidence_age_hours,
            tool_permissions_at_time=d.tool_permissions_at_time,
            model_version=d.model_version,
            result=d.result,
        )
        for d in m.decisions
    ]
    return TraceBatch(
        trace_id=m.trace_id,
        decisions=decisions,
        environment=m.environment,
        metadata=m.metadata,
    )


def load_traces(path: str | Path) -> List[TraceBatch]:
    """Load and validate trace records; raise TraceError on any shape error."""
    p = Path(path)
    out: List[TraceBatch] = []
    with p.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TraceError(f"malformed JSON on line {lineno}: {exc}") from exc
            if not isinstance(data, dict):
                raise TraceError(f"line {lineno}: record must be a JSON object")
            try:
                model = TraceModel(**data)
            except ValidationError as exc:
                raise TraceError(f"line {lineno}: {exc}") from exc
            if not model.decisions:
                raise TraceError(f"line {lineno}: trace has no decisions")
            out.append(_to_trace_batch(model))
    if not out:
        raise TraceError("trace file contains no records")
    return out

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Fail-closed loaders for policy, authority, and trace files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class PolicyError(ValueError):
    pass


class AuthorityError(ValueError):
    pass


class TraceError(ValueError):
    pass


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

    @field_validator("version")
    @classmethod
    def _version_str(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError(f"version must be a string, got {type(v).__name__}")
        return v

    @field_validator("default_effect")
    @classmethod
    def _default_valid(cls, v: str) -> str:
        if v not in ("ALLOW", "DENY"):
            raise ValueError(f"default_effect must be ALLOW or DENY, got {v!r}")
        return v


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
    return model.model_dump()


def load_authority(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text())
    except Exception as exc:
        raise AuthorityError(f"failed to parse authority YAML: {exc}") from exc
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise AuthorityError(f"authority must be a mapping, got {type(raw).__name__}")
    try:
        model = AuthorityModel(**raw)
    except ValidationError as exc:
        raise AuthorityError(f"invalid authority: {exc}") from exc
    return model.model_dump()


def load_traces(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    out: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise TraceError(f"malformed JSON on line {lineno}: {exc}") from exc
    if not out:
        raise TraceError("trace file contains no records")
    return out

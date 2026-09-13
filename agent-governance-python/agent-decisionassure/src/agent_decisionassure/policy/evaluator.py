# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Safe policy DSL evaluator - no eval, no attribute access, no calls."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping, Sequence

_ROOTS = ("action", "context", "agent_id", "timestamp")
_MAX_PATH_DEPTH = 8


class PolicyError(ValueError):
    """Raised when a policy condition is malformed or not evaluable."""


def _resolve_field(path, env):
    if not isinstance(path, str) or not path:
        raise PolicyError(f"field path must be a non-empty string, got {path!r}")
    parts = path.split(".")
    if len(parts) > _MAX_PATH_DEPTH:
        raise PolicyError(f"field path too deep: {path!r}")
    root = parts[0]
    if root not in _ROOTS:
        raise PolicyError(f"unknown root '{root}' in path '{path}'")
    current = env.get(root)
    for part in parts[1:]:
        if current is None:
            return None
        if isinstance(current, Mapping):
            current = current.get(part)
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            try:
                idx = int(part)
            except ValueError as exc:
                raise PolicyError(
                    f"cannot index sequence with non-integer '{part}' in path '{path}'"
                ) from exc
            if idx < 0 or idx >= len(current):
                return None
            current = current[idx]
        else:
            return None
    return current


def _is_field_ref(value):
    return isinstance(value, Mapping) and set(value.keys()) == {"field"}


def _resolve_value(value, env):
    if _is_field_ref(value):
        return _resolve_field(value["field"], env)
    return value


def _as_pair(value, op):
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 2:
        raise PolicyError(f"operator '{op}' expects a list of exactly 2 items, got {value!r}")
    return value[0], value[1]


def _as_list(value, op):
    if not isinstance(value, list):
        raise PolicyError(f"operator '{op}' expects a list, got {value!r}")
    return value


def _cmp(a, b, symbol):
    if a is None or b is None:
        return False
    try:
        if symbol == ">":
            return a > b
        if symbol == ">=":
            return a >= b
        if symbol == "<":
            return a < b
        if symbol == "<=":
            return a <= b
    except TypeError:
        return False
    raise PolicyError(f"unsupported comparison '{symbol}'")


def _evaluate(node, env):
    if not isinstance(node, Mapping):
        raise PolicyError(f"condition node must be a mapping, got {type(node).__name__}")
    if len(node) != 1:
        raise PolicyError(f"condition node must have exactly one key, got {list(node.keys())}")
    (op, operand), = node.items()

    if op == "all":
        return all(_evaluate(child, env) for child in _as_list(operand, op))
    if op == "any":
        return any(_evaluate(child, env) for child in _as_list(operand, op))
    if op == "not":
        return not _evaluate(operand, env)

    if op in ("eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"):
        a_raw, b_raw = _as_pair(operand, op)
        a = _resolve_value(a_raw, env)
        b = _resolve_value(b_raw, env)
        if op == "eq":
            return a == b
        if op == "ne":
            return a != b
        if op == "gt":
            return _cmp(a, b, ">")
        if op == "gte":
            return _cmp(a, b, ">=")
        if op == "lt":
            return _cmp(a, b, "<")
        if op == "lte":
            return _cmp(a, b, "<=")
        if op == "in":
            if not isinstance(b, (Sequence, str, set, frozenset)) or b is None:
                return False
            try:
                return a in b
            except TypeError:
                return False
        if op == "nin":
            if not isinstance(b, (Sequence, str, set, frozenset)) or b is None:
                return True
            try:
                return a not in b
            except TypeError:
                return True

    raise PolicyError(f"unsupported operator '{op}'")


def evaluate_condition(condition, env):
    return _evaluate(condition, env)


def build_env(decision, context=None):
    return {
        "action": {
            "name": decision.action.name,
            "tool": decision.action.tool,
            "version": decision.action.version,
            "parameters": dict(decision.action.parameters or {}),
            "transaction_amount": decision.action.transaction_amount,
        },
        "context": dict(context or decision.context or {}),
        "agent_id": str(decision.agent_id),
        "timestamp": decision.timestamp,
    }


# ---------------------------------------------------------------------------
# Load-time validation
# ---------------------------------------------------------------------------

def validate_condition(node):
    """Recursively validate that node is a well-formed DSL expression."""
    _validate_node(node, depth=0)


def _validate_node(node, depth):
    if depth > _MAX_PATH_DEPTH:
        raise PolicyError("condition nesting too deep")
    if not isinstance(node, Mapping):
        raise PolicyError(f"condition must be a mapping, got {type(node).__name__}")
    if len(node) != 1:
        raise PolicyError(f"condition must have exactly one key, got {list(node.keys())}")
    (op, operand), = node.items()
    if op in ("all", "any"):
        if not isinstance(operand, list) or not operand:
            raise PolicyError(f"'{op}' requires a non-empty list")
        for child in operand:
            _validate_node(child, depth + 1)
        return
    if op == "not":
        _validate_node(operand, depth + 1)
        return
    if op in ("eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"):
        if not isinstance(operand, Sequence) or isinstance(operand, (str, bytes)):
            raise PolicyError(f"'{op}' requires a list of two items")
        if len(operand) != 2:
            raise PolicyError(f"'{op}' requires exactly two items, got {len(operand)}")
        for item in operand:
            _validate_field_ref(item)
        return
    raise PolicyError(f"unknown operator '{op}'")


def _validate_field_ref(value):
    """If value is a field reference, verify its root and path depth."""
    if not isinstance(value, Mapping):
        return
    if set(value.keys()) != {"field"}:
        raise PolicyError(f"unexpected mapping in operand: {value!r}")
    path = value["field"]
    if not isinstance(path, str) or not path:
        raise PolicyError(f"field reference must be a non-empty string, got {path!r}")
    parts = path.split(".")
    if len(parts) > _MAX_PATH_DEPTH:
        raise PolicyError(f"field path too deep ({len(parts)} > {_MAX_PATH_DEPTH}): {path!r}")
    if parts[0] not in _ROOTS:
        raise PolicyError(f"unknown root '{parts[0]}' in path {path!r}; must be one of {_ROOTS}")

# Policy Model

DecisionAssure Impact uses a **pure data DSL** for policy conditions. No Python
is ever executed; no attributes, calls, or subscripts on user input are allowed.

## Operators

- `all: [cond, ...]` — logical AND
- `any: [cond, ...]` — logical OR
- `not: cond` — logical NOT
- `eq: [a, b]`, `ne: [a, b]` — equality / inequality
- `gt: [a, b]`, `gte: [a, b]`, `lt: [a, b]`, `lte: [a, b]` — comparisons
- `in: [needle, haystack]`, `nin: [needle, haystack]` — membership

## Field References

A value is either a literal or `{"field": "path.to.value"}` where the path root
must be one of: `action`, `context`, `agent_id`, `timestamp`. Traversal uses
mapping keys and integer indices only — no `getattr`, no method calls.

## Example

```yaml
version: v5
rules:
  - priority: 10
    condition:
      lt: [{field: context.risk_score}, 30]
    effect: ALLOW
  - priority: 5
    condition:
      all:
        - eq: [{field: action.name}, refund]
        - lte: [{field: action.parameters.amount}, 40000]
    effect: ALLOW
default_effect: DENY

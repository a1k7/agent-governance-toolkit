# CI Integration

Use `decisionassure impact` as a pre-merge gate. It exits non-zero on `BLOCK`.

## Example: policy change

```yaml
- name: Governance impact
  run: |
    decisionassure impact \
        --traces ./audit/sample_traces.jsonl \
        --policy-current ./policies/current.yaml \
        --policy-proposed ./policies/proposed.yaml \
        --authority ./policies/authority.yaml

Example: authority change
- name: Authority change impact
  run: |
    decisionassure impact \
        --traces ./audit/sample_traces.jsonl \
        --policy-current ./policies/current.yaml \
        --policy-proposed ./policies/current.yaml \
        --authority-current ./policies/authority-baseline.yaml \
        --authority-proposed ./policies/authority-proposed.yaml

Exit codes

0 — ALLOW
1 — BLOCK
2 — input error (malformed policy, authority, or trace file)

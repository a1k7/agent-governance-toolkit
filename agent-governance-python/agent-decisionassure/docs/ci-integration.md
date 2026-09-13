# CI integration

Run the `impact` command with `--ci`. Exit code 0 means analysis completed without a block, 1 means the governance gate blocked, 2 means input/configuration error, and 3 is reserved for integrity/system error.
# CI Integration

Use decisionassure impact as a pre-merge gate. It exits non-zero on BLOCK.

Example CI step:

  - name: Governance impact
    run: |
      decisionassure impact \
          --traces ./audit/sample_traces.jsonl \
          --policy-current ./policies/current.yaml \
          --policy-proposed ./policies/proposed.yaml \
          --authority ./policies/authority.yaml

For authority change analysis:

  - name: Authority change impact
    run: |
      decisionassure impact \
          --traces ./audit/sample_traces.jsonl \
          --policy-current ./policies/current.yaml \
          --policy-proposed ./policies/current.yaml \
          --authority-current ./policies/authority-baseline.yaml \
          --authority-proposed ./policies/authority-proposed.yaml

Exit codes:

- 0 = ALLOW
- 1 = BLOCK (fail the job)
- 2 = input error (fail the job)

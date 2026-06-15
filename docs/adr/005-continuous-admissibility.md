# ADR 005: Continuous Admissibility and Governance Flight Recorder

## Status

Proposed (2026-06-15)

## Context

AGT evaluates policy at approval time and at tool‑call boundaries. It does **not** verify that the governance context (agent identity, policy version, delegation chain, evidence freshness) remains unchanged between approval and execution. A delegation can be revoked, a policy updated, or evidence become stale after approval but before execution. This creates a governance gap: an action may be allowed based on obsolete authority.

Furthermore, even if an action is correctly denied, there is no replayable record that proves *why* the authority was invalid at the moment of execution.

## Decision

Introduce **Continuous Admissibility** as a new governance primitive, and **Governance Flight Recorder** as its practical embodiment.

### Continuous Admissibility – Formal Definition

A request is continuously admissible iff:
identity_t == identity_approval
policy_version_t == policy_version_approval
delegation_chain_t == delegation_chain_approval
evidence_hash_t == evidence_hash_approval


If any of these change between approval and execution, the gate MUST deny execution (fail‑closed) unless overridden by an explicit, audited emergency procedure.

### Governance Flight Recorder

A replayable cryptographic snapshot containing:

- The decision (allow/deny)
- The approval‑time governance snapshot (identity, policy, delegation, evidence hashes)
- The execution‑time governance snapshot (if different)
- The diff (which elements changed)
- A timestamp and signature chain

This allows an auditor to replay the exact governance state years later and verify whether the action was admissible at the time of execution.

### Implementation

- `ContinuityVerifier` class with pre‑/post‑execution hashing.
- `SandboxConfig.enable_continuity` and `enforcement_mode`.
- `govern()` decorator with same flags.
- `ContinuityTrace` (JSON) – the flight recorder output.

### Enforcement Modes

- `enforce` (default) – raise `GovernanceDenied` on drift.
- `audit` – log warning only, do not block.

## Consequences

- **Positive**: Closes the “approval is not enough” gap. Adds deterministic, replayable audit trail.
- **Negative**: Small CPU overhead when enabled. Requires callers to provide continuity context.
- **Alternatives**: Re‑running policy evaluation does not detect context drift; external service adds latency.

## Performance

Reference implementation (Nanogate) achieves **530 ns** median evaluation latency, **0 false admits** after 100k adversarial mutations, **0 false denies** after 100k stable traces.

## References

- Nanogate: https://github.com/a1k7/nanogate
- DecisionAssure: https://github.com/a1k7/DecisionAssure-Runtime-Governance
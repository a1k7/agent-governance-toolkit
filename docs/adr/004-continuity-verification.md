# ADR 004: Continuity Verification for Agent Tool Calls and Sandbox

## Status

Accepted (2026-06-15)

## Context

AGT evaluates policy at the time of a tool call or sandbox execution. However, in multi‑step agent workflows (e.g., a LangGraph agent that takes seconds to decide), the authority context – policy version, delegation chain, evidence freshness, agent identity – can change *after* policy evaluation but *before* the final execution. This creates a governance gap: an action may be allowed based on stale or invalid authority.

## Decision

Add an **optional continuity verification module** to AGT with:

- **Pre‑execution hook**: captures SHA‑256 hashes of:
  - `observer_identity_hash` (agent_id, session_id, memory_state)
  - `reference_frame_hash` (policy_version, delegation_chain, external_reference_state)
- **Post‑execution hook**: recomputes both hashes and compares.
- **Drift detection**: if either hash changes, the module produces a JSON trace and, depending on `enforcement_mode`, either raises a `GovernanceDenied` (fail‑closed) or only logs (audit mode).
- **Configurable enforcement**: `enforcement_mode` – `"enforce"` (default) or `"audit"`.
- **Opt‑in**: disabled by default (`enable_continuity=False`).

## Consequences

- **Positive**: Closes the “approval is not enough” gap; adds deterministic, replayable audit trail for authority continuity.
- **Negative**: Adds small CPU overhead when enabled (SHA‑256 hashing). The `continuity_context` must be supplied by the caller.
- **Alternatives considered**: audit‑only, external service, probabilistic anomaly detection – rejected.

## References

- RFC #2873 (original proposal)
- DecisionAssure trace schema: https://github.com/a1k7/DecisionAssure-Runtime-Governance
- Nanogate: https://github.com/a1k7/nanogate
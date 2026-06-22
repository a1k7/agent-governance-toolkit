# ADR 0027: Authority Persistence Protocol (APP) Integration

**Status:** Draft  
**Date:** 2026-06-23  
**Author:** Akhilesh Warik (a1k7)  
**PR:** (to be opened)  
**Issue:** (to be opened)

---

## Context

The Agent Governance Toolkit (AGT) currently provides:

- Policy evaluation (YAML/OPA/Cedar)
- Identity (SPIFFE/DID/mTLS)
- Audit logging (tamper‑evident)
- Replay
- MCP Security Gateway
- Trust and sandboxing

However, AGT does **not** currently verify that:

1. **Authority remains valid** between approval and execution.
2. **Capability evolution** is tracked semantically (e.g., `read → write` vs `read → delete`).
3. **Long‑running agents** can persist with periodic reauthorization without losing governability.
4. **Replayable traces** provide independent verification of authority state at commit time.
5. **Attribution reports** explain why authority was granted, degraded, or denied.

Current AGT assumes that once an agent is approved, authority persists until explicitly revoked. This creates a governance gap: policies, delegation chains, evidence freshness, and observer identity can change mid‑flight, and AGT does not detect this.

This ADR proposes integrating the **Authority Persistence Protocol (APP)** as an optional extension to AGT that closes this gap.

---

## Decision

We will integrate **APP** into AGT as an extension under `contrib/agt_integration/`. APP provides:

### 1. Cryptographic Authority Chain

- Every state change is hashed and cryptographically linked.
- The chain is tamper‑evident and replayable.
- Independent verifiers can recompute hashes and validate integrity.

### 2. Continuous Authority Score (0–100)

- Score starts at 100 (initial authority).
- Each state change adjusts the score based on impact.
- Score thresholds:
  - **VALID** (80–100)
  - **DEGRADED** (50–79)
  - **UNKNOWN** (20–49)
  - **DENIED** (0–19)
- Execution is allowed only if score ≥ 50 (VALID or DEGRADED).

### 3. Capability Impact Model

- Capabilities are classified into:
  - `READ`
  - `WRITE`
  - `DELETE`
  - `EXPORT`
  - `DELEGATE`
  - `ADMIN`
- Impact matrix quantifies the risk of changing from one class to another (0–50).
- **High impact** (≥30) → immediate `DENIED`.
- **Medium impact** (8–29) → score reduction (`DEGRADED`).
- **Low/No impact** (<8) → no penalty (`VALID`).

### 4. Authority Epochs & Restoration

- Reauthorization creates a **new epoch**.
- Score resets to 100, and previous invalidations are **cleared** for verification.
- `refresh_evidence()` restores score to at least 50.
- `reauthorization()` restores score to 100 and clears invalidation history.

### 5. Replayable Traces & Independent Verifier

- APP produces a structured JSON trace of every authority decision.
- The trace includes: step index, decision, score, attribution, confidence, recommended action.
- AGT operators can verify traces offline using the included `verify_trace_selfcontained.py`.

### 6. Attribution Reports

- Every link stores: rule, reason, actual outcome, recommendation, confidence, false‑positive rate.
- Reports identify which rules generate the most false positives, enabling systematic tuning.

### 7. Integration Points

- AGT policy evaluator can call APP’s `append_link()` before committing actions.
- AGT audit log can store APP certificates.
- AGT replay can consume APP traces.

---

## Alternatives Considered

### Alternative 1: Manual Authority Checks

**Description:** Add manual checks in policy evaluation to verify authority.

**Why rejected:** Manual checks are brittle, not cryptographically verifiable, and cannot track capability evolution or long‑running persistence.

### Alternative 2: Separate Service (External)

**Description:** Run APP as a standalone service outside AGT.

**Why rejected:** Adds operational complexity, does not integrate with AGT’s policy/identity/audit, and breaks the unified governance experience.

### Alternative 3: Extend Existing AGT Modules

**Description:** Add authority persistence to AGT’s existing modules (e.g., MCP, Agent OS).

**Why rejected:** Scope is too large. APP has a distinct lifecycle (create → drift → invalidate → restore) and requires dedicated data structures (chains, epochs, capability taxonomies). Keeping it as a cohesive extension preserves modularity.

---

## Consequences

### Positive

- AGT gains continuous authority verification, not just point‑in‑time approval.
- Long‑running agents can survive with periodic governance maintenance.
- Capability drift is measured semantically, reducing false positives.
- Traces are replayable and auditable by independent reviewers.
- Attribution reports enable systematic governance tuning.

### Negative

- Adds a new integration (`authority‑persistence‑protocol`) with dependencies (`pydantic`, `typing`).
- Operators must configure thresholds (e.g., evidence freshness window, delegation depth limits).
- Requires human‑in‑the‑loop for reauthorization (unless automated).

### Neutral

- The integration is optional – AGT users can enable it.
- The extension is MIT licensed and maintained by the contributor.

---

## Security Considerations

### Threat Model

1. **Tampered Traces** – An attacker modifies a trace after generation.
   - **Mitigation:** Each link is cryptographically hashed. The verifier recomputes hashes and detects tampering.

2. **Authority Score Inflation** – An attacker attempts to keep score high artificially.
   - **Mitigation:** Score is derived deterministically from the chain. Reauthorization requires explicit governance action, not arbitrary inflation.

3. **Epoch Spoofing** – An attacker tries to start a new epoch without proper reauthorization.
   - **Mitigation:** Reauthorization events are cryptographically linked. The verifier checks that each epoch starts with a valid reauthorization link.

4. **Denial of Service (DoS)** – High‑frequency trace submissions.
   - **Mitigation:** APP is not inline; it processes traces asynchronously. AGT’s existing rate‑limiting applies.

### Blast‑Radius Bounds

If APP converges on a bad authority decision:

- **Impact is bounded**: Only actions that violate APP rules are blocked; AGT’s existing policies still apply.
- **Replay provides validation**: If APP mis‑denies, the trace can be reviewed and the decision can be overridden by AGT’s existing escalation paths.
- **Fail‑closed default**: If APP is unavailable, AGT falls back to its existing policy‑only governance.

### Interaction with AGT’s Immutable Audit Trail

- APP does not modify AGT’s existing audit logs.
- It creates new, append‑only records: chains, certificates, attribution reports.
- These records can be independently verified alongside AGT’s audit trail.

---

## Assurance Classes and Reviewability

| Guarantee Class | Reviewer Checks By | Provided by this ADR? |
|-----------------|-------------------|----------------------|
| **Detection / what happened** | Replaying the chain and verifying hashes | ✅ Yes – APP provides replayable traces |
| **Enforced at the gate** | Checking AGT policy logs | ✅ Existing AGT structural controls (referenced, not modified) |
| **Unreachable by construction** | Inspecting reachable surface without replaying | ❌ No – out of scope for this ADR |

---

## Status

**Draft** – awaiting maintainer review.

**Next Steps:**
1. Maintainers review and approve ADR.
2. Implementation PR is opened referencing this ADR.
3. Integration is merged into AGT under `contrib/agt_integration/`.

---

## References

- [Authority Persistence Protocol Repository](https://github.com/a1k7/authority-persistence-protocol)
- [DecisionAssure Verifier Schema v1.3](https://github.com/a1k7/DecisionAssure-Runtime-Governance)
- [SAFE‑Matter Constitutional State Transition Rules](https://github.com/a1k7/safe-matter)
- [Microsoft Agent Governance Toolkit – ADR-0030](https://github.com/microsoft/agent-governance-toolkit)

---
title: "ADR 0033: DecisionAssure Impact – Counterfactual Governance Replay"
last_reviewed: 2026-09-13
owner: "@a1k7"
---

# ADR 0033: DecisionAssure Impact – Counterfactual Governance Replay

## Context

AGT records decisions via `MerkleAuditChain` / `AuditEntry` but provides no way
to predict the effect of a governance change on historical decisions. This ADR
introduces a standalone package, `agent-decisionassure`, that replays a JSONL
trace export against a proposed policy/authority change.

The module is new and optional; it does **not** modify `agentmesh`,
`agent_os`, or any existing governance interface. It does **not** import
`decisionassure_continuity`. Its trace input is a JSONL export produced by
the user (there is no built-in exporter for `AuditEntry` in this PR).

## Decision

Add `agent-governance-python/agent-decisionassure/` providing:

- A **pure data DSL** for policy conditions (`all`/`any`/`not`/`eq`/`lte`/…).
- A **counterfactual replay engine** comparing baseline and proposed states.
- A CLI (`decisionassure`) with `impact` and `detect-drift`.
- Fail-closed defaults (missing model, stale evidence, malformed policy).

## Consequences

- New package; cannot regress existing behaviour.
- Requires its own CI registration (added in this PR).
- Users must export traces to JSONL; no built-in exporter ships here.

## Related

- ADR 0032 (TRACE v0.1)

## Signed-off-by

Akhilesh Warik <warikakhilesh@gmail.com>

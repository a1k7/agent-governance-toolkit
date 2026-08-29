# DecisionAssure Impact

**Governance change impact analysis for agentic AI.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is DecisionAssure Impact?

DecisionAssure Impact answers the critical question every governance team faces:

> *“What happens to my production agents if I change a policy, authority, model, or tool?”*

Instead of blindly deploying governance changes, you can now **replay real production decision traces** against the proposed future state and see exactly:

- **How many previously admissible decisions become inadmissible**
- **Which agents, tools, and decision types are affected** (blast radius)
- **Estimated financial exposure**
- **Clear severity and actionable recommendation** – `ALLOW`, `REVIEW`, or `BLOCK`

It is the missing **“What‑If”** engine for AI governance — designed to integrate seamlessly with the [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) and any other agentic platform.

---

## Key Features

- 🔄 **Counterfactual Replay** – Re‑evaluate historical traces against new policies, authorities, models, or capabilities.
- 📊 **Governance Diff** – Identify every `ADMISSIBLE → INADMISSIBLE` and `INADMISSIBLE → ADMISSIBLE` transition.
- 💥 **Blast Radius** – See which agents, tools, policy versions, and decision types are impacted.
- 💰 **Business Exposure** – Sum transaction values from affected decisions to estimate financial risk.
- ⚖️ **Multi‑Factor Severity** – Combines exposure, impact rate, action criticality, and authority changes for a realistic severity score.
- 🧩 **Drift Detection** – Detect governance drift at runtime (policy version changes, stale evidence, expired authority).
- 🚀 **CI/CD Ready** – CLI returns non‑zero exit code on `BLOCK`, perfect for pre‑merge gates.
- 🧪 **Extensible & Tested** – Fully typed, Pydantic models, and comprehensive test suite.

---

## Quick Start

### 1. Installation

```bash
git clone https://github.com/your-org/decisionassure-impact.git
cd decisionassure-impact
pip install -e .



2. Generate Sample Data

bash
python examples/generate_sample.py
This creates examples/sample_traces.jsonl with 1000 synthetic decision traces.

3. Run Impact Analysis

bash
decisionassure impact \
    --traces examples/sample_traces.jsonl \
    --policy-current examples/policy_v4.yaml \
    --policy-proposed examples/policy_v5.yaml
4. Detect Drift

bash
decisionassure detect-drift \
    --traces examples/sample_traces.jsonl \
    --policy-current examples/policy_v4.yaml \
    --drift-threshold 1.0
Example Output:

================================================================================
  DECISIONASSURE IMPACT REPORT
================================================================================

Change: Policy v4 → v5 (limit 50k→40k)
Environment: Banking / Refund Agent (Demo)

--------------------------------------------------------------------------------
EXECUTION DATA
--------------------------------------------------------------------------------
Traces analyzed:                       10,000
Decisions evaluated:                   55,531

--------------------------------------------------------------------------------
COUNTERFACTUAL GOVERNANCE DIFF
--------------------------------------------------------------------------------
ADMISSIBLE → INADMISSIBLE:               7,024
INADMISSIBLE → ADMISSIBLE:                   0
Invalidated:                                 0
Unchanged:                              48,507
Impact rate:                             12.65%

--------------------------------------------------------------------------------
BLAST RADIUS
--------------------------------------------------------------------------------
Agents affected:                          4,633
Tools affected:                               1
Policy versions affected:                     1
Decision types affected:                      4

--------------------------------------------------------------------------------
BUSINESS EXPOSURE
--------------------------------------------------------------------------------
Estimated exposure:                  ₹35.12 crore

--------------------------------------------------------------------------------
GOVERNANCE ASSESSMENT
--------------------------------------------------------------------------------
Severity:                             CRITICAL

Primary regression:
  Previously admissible decisions become inadmissible under v5.

--------------------------------------------------------------------------------
DECISION
--------------------------------------------------------------------------------

                         ❌ BLOCK
================================================================================


Integration with Microsoft Agent Governance Toolkit (AGT)

DecisionAssure Impact is designed to drop into AGT without touching its core code.

Use in CI/CD (Pre‑merge Gate):

from decisionassure_impact.integration import analyze_impact_for_pr

report = analyze_impact_for_pr(
    current_policy=current_policy,
    proposed_policy=pr_policy,
    traces_path="./audit_logs/last_30_days.jsonl"
)

if report["recommendation"] == "BLOCK":
    # Fail the PR / deployment
    exit(1)


Runtime Drift Detection


from decisionassure_impact.integration import check_runtime_drift, create_snapshot_from_context

# At session start
snapshot = create_snapshot_from_context(context)

# Before each sensitive action
drift_result = check_runtime_drift(
    snapshot=snapshot,
    current_policy_version=current_policy.version,
    current_authority=current_authority
)

if drift_result["is_drifted"]:
    # Log, alert, or block
    logger.warning("Governance drift detected!")


CLI Reference

decisionassure impact

Run counterfactual impact analysis.

--traces PATH – Required. Path to traces JSONL file.
--policy-current PATH – Required. Path to current policy YAML.
--policy-proposed PATH – Required. Path to proposed policy YAML.
--output-json PATH – Export report to JSON file.
--verbose – Enable debug logging.
decisionassure detect-drift

Detect governance drift in production traces.

--traces PATH – Required. Path to traces JSONL file.
--policy-current PATH – Required. Path to current policy YAML.
--drift-threshold FLOAT – Drift threshold in hours (default: 1.0).

File Structure

decisionassure_impact/
├── src/decisionassure_impact/
│   ├── models/          # Pydantic data models
│   ├── engine.py        # Core counterfactual replay
│   ├── drift.py         # Runtime drift detection
│   ├── cli.py           # CLI commands
│   └── integration.py   # AGT integration helpers
├── examples/            # Sample data and policies
├── tests/               # Unit and integration tests
├── pyproject.toml       # Build and dependency config
└── README.md


Development & Testing

Run All Tests

bash
pytest tests/
Generate Sample Traces (Custom)

You can adjust the number of traces and decision distribution in examples/generate_sample.py.

Build and Install Locally

bash
pip install -e .
License

This project is licensed under the MIT License – see the LICENSE file for details.

Contributing

We welcome contributions! Please read our Contributing Guide and Code of Conduct.

Support

Full Documentation
Issue Tracker
Discussions
Acknowledgements

Built for the Microsoft Agent Governance Toolkit and inspired by the need for deterministic governance change impact analysis.

DecisionAssure Impact – Governance that survives change.

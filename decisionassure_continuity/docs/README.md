# DecisionAssure Continuity Kernel

**Prove the agent remained the same agent – and discover dangerous capabilities that emerge from multi‑agent interactions.**

DecisionAssure Continuity Kernel is a governance toolkit for AI agents that goes beyond traditional policy checks. It provides:

- **Continuity Verification** – prove an agent’s identity, policy, and context remained intact across actions.
- **Witness Chains** – blockchain‑style hash chains for tamper‑evident agent identity continuity.
- **Collusion Detection** – real‑time detection of hidden coordination between agents (activation‑level).
- **Deception Probe** – jailbreak detection via internal hidden‑state monitoring.
- **Capability Discovery** – unsupervised discovery of emergent capabilities from agent traces.
- **Capability Witness Engine** – cryptographic proof of why a capability existed, with counterfactual verification and governance recommendations.

---

## 🧩 What It Does

| Feature | Description |
|---------|-------------|
| **Continuity Verification** | Re‑test identity, policy, delegation, and evidence freshness at every step. |
| **Witness Chains** | Cryptographic hash chain that proves the agent did not drift without re‑authorisation. |
| **Collusion Interceptor** | Monitors hidden neural states to detect cross‑agent collusion in real time. |
| **Deception Probe** | Scans hidden states for jailbreak patterns before generation. |
| **Capability Discovery** | Finds recurring patterns in agent traces without any pre‑defined rules. |
| **Capability Witness Engine** | Produces verifiable witnesses: required actions, counterfactual proof, confidence, and a governance recommendation (DENY, HUMAN_REVIEW, MONITOR, ADMIT). |

---

## 🔌 Supported Frameworks

- **Microsoft AutoGen**
- **LangGraph**
- **CrewAI**
- **OpenAI Agents SDK**
- Custom (via `BaseAdapter`)

---

## 📦 Installation

```bash
# Clone or download the repository
cd decisionassure_continuity
pip install -e .
```

---

## 🚀 Quick Start – Continuity Verification

```python
from src.models import ContinuityWitness
from src.ccv_engine import CCVEngine

w1 = ContinuityWitness(
    index=0, previous_witness_hash="0"*64,
    agent_id="alice", session_id="s1",
    constitution_hash="hash1", observer_hash="hash1",
    reference_frame_hash="hash1", action_hash="action1"
)
w2 = ContinuityWitness(
    index=1, previous_witness_hash=w1.witness_hash,
    agent_id="alice", session_id="s1",
    constitution_hash="hash1", observer_hash="hash2",  # Drift!
    reference_frame_hash="hash1", action_hash="action2"
)

engine = CCVEngine()
result = engine.verify_continuity([w1, w2])
print(f"Continuity Score: {result.continuity_score}")
print(f"Status: {result.verification_status}")
```

---

## 🧠 Quick Start – Capability Witness Engine

```python
from src.capability_witness_engine import CapabilityWitnessEngine
from src.models import AgentAction

# Load traces from any supported framework (AutoGen, LangGraph, etc.)
# Each trace is a list of AgentAction objects.
traces = [[
    AgentAction(agent_id="alice", action_type="read_credentials"),
    AgentAction(agent_id="charlie", action_type="export_data")
]]

engine = CapabilityWitnessEngine(min_samples=2, eps=0.5)
witnesses = engine.process_traces(traces)

for w in witnesses:
    print(f"Capability: {w['capability']}")
    print(f"Confidence: {w['confidence']:.2%}")
    print(f"Recommendation: {w['governance_recommendation']}")
    print(f"Witness Hash: {w['witness_hash'][:16]}...")
```

---

## 🖥️ CLI Usage

```bash
# Continuity verification
continuity verify witnesses.json --output result.json

# Collusion detection
continuity collusion '{"alice":[0.9,0.8,0.7],"bob":[0.1,0.2,0.3]}'

# Capability discovery (from traces)
continuity discover traces.json

# Capability Court (end‑to‑end verdict)
continuity court traces.json --output verdicts.json

# Generate a witness from a single action list
continuity witness '{"agent":"alice","action":"read_database"}'
```

---

## 📁 Processing Real Traces

The toolkit includes adapters for popular agent frameworks. To process a directory of AutoGen traces:

```bash
python examples/real_trace_demo.py ./sample_traces/ autogen
```

Output will include:

- Discovered emergent capability clusters
- Cryptographic witness hashes
- Counterfactual verification results
- Governance recommendations (DENY / HUMAN_REVIEW / MONITOR / ADMIT)

---

## 📊 Capability Witness Output Example

```json
{
  "capability": "Credential Exfiltration",
  "confidence": 0.94,
  "required_actions": [
    {"agent": "alice", "action": "read_credentials"},
    {"agent": "charlie", "action": "export_data"}
  ],
  "minimal_witness": true,
  "counterfactual_verified": true,
  "governance_recommendation": "DENY",
  "witness_hash": "bb57369c232d1ad7...",
  "trace_claim": {
    "format": "TRACE v0.1",
    "claim_type": "capability_witness",
    "hash": "bb57369c...",
    "evidence": [...]
  }
}
```

---

## 🔐 Integration with AgentTrust / TRACE

The `trace_claim` field is **TRACE‑compatible**, meaning capability witnesses can be consumed by AgentTrust, TRACE, and other governance systems as portable evidence.

---

## 📚 Documentation

- `docs/CONTINUITY_SPEC.md` – Specification for continuity verification
- `docs/EMERGENT_SPEC.md` – Specification for emergent capability discovery
- `docs/WITNESS_STANDARD.md` – Capability Witness Standard (v1.0)
- `docs/METHODOLOGY.md` – Benchmark methodology and metrics

---
## 🚀 Batch Processing Hundreds of Traces

To process a large number of traces from a directory tree:

```bash
python examples/batch_witness_demo.py ./my_traces/ autogen


This will:

Recursively find all JSON trace files
Parse them with the appropriate adapter
Run the Capability Witness Engine
Generate a summary report with:

Total traces processed
Total witnesses generated
Recommendations breakdown (DENY, HUMAN_REVIEW, MONITOR, ADMIT)
Human reviews triggered
Low Confidence Witness
Average confidence
Save a JSON report for further analysis




---

## 🧪 How to Run the Full Batch

1. **Generate synthetic traces** (or use your own real traces):
   ```bash
   python examples/generate_sample_traces.py

2. Run the batch processor:
python examples/batch_witness_demo.py sample_traces_large/ autogen 2 0.5

3. Expected output:
📂 Scanning sample_traces_large/ for autogen traces...
📁 Found 150 trace files
✅ Parsed 150 traces successfully (errors: 0)
   Agents: alice, bob, charlie, dave, eve, frank, grace, heidi, ivan, jack, karen
🧾 Generated 4 Capability Witness(es)
==============================================================================
🧾 Capability Witness Engine – Batch Report
==============================================================================
   Timestamp:                2026-06-18T18:00:00
   Total traces processed:   150
   Total witnesses generated: 4
   Parse errors:             0
   Agents involved:          alice, bob, charlie, ...
   Frameworks:               autogen: 150

   Recommendations:
      HUMAN_REVIEW: 3
      MONITOR: 1

   Severities:
      critical: 3
      high: 1

   Human reviews triggered:  3
   Low Confidence Witness:      0
   Average confidence:        94.5%

   Witness Details:
      #1: Credential Exfiltration (conf: 96.67%, rec: HUMAN_REVIEW)
           Actions: alice->read_credentials, charlie->export_data
           Hash: bb57369c232d1ad7...
      ...
==============================================================================
✅ Full report saved to witness_report_20260618_180000.json

## 🧠 Governance Learning Loop

Unknown capability witnesses can be labelled and added to the ontology:

```bash


The system will suggest labels for unknown witnesses. Analysts can then:

Review the witness and action set.
Add a label using the learner.
Export the updated ontology.
This creates a self-improving governance system.


---

## 🧪 How to Run with Learning

```bash
# Generate synthetic traces (or use real ones)
python examples/generate_sample_traces.py

# Run batch with learning enabled
python examples/batch_witness_demo.py sample_traces_large/ --framework autogen --learn

## 📄 License

MIT

# DecisionAssure Continuity

**Discover what AI systems can do before they do it.**

DecisionAssure Continuity is a governance engine for multi-agent systems that discovers emergent capabilities directly from execution traces, generates replayable capability witnesses, verifies them through counterfactual replay, and continuously evolves governance knowledge through human review.

Traditional security systems look for known attacks.

DecisionAssure looks for **capabilities**.

A capability is not a single action.

It is a coordinated sequence of actions that collectively enable a dangerous outcome.

Examples include:

* Credential Exfiltration
* Privilege Escalation
* Model Exfiltration
* Secret Leakage
* Backdoor Installation
* Collusive Coordination
* Identity Theft

The system discovers these capabilities from traces, produces cryptographic evidence, and enables governance teams to continuously improve detection through ontology evolution.

---

## Why This Exists

Modern AI systems increasingly operate as teams of agents.

Individual actions may appear harmless:

Agent A reads credentials.

Agent B accesses a database.

Agent C exports data.

Viewed independently, none of these actions necessarily indicate malicious behavior.

Viewed together, they form a capability:

**Credential Exfiltration**

Most monitoring systems reason about events.

DecisionAssure reasons about capabilities.

---

## Core Innovation

DecisionAssure introduces the concept of a:

### Capability Witness

A Capability Witness is a replayable governance artifact proving that a capability existed within a trace.

Each witness contains:

* Capability classification
* Required actions
* Confidence score
* Severity
* Counterfactual verification
* Witness hash
* Governance recommendation

Example:

Credential Exfiltration

Required Actions:

* alice → read_credentials
* charlie → export_data

Counterfactual Verification:

Remove either action and the capability disappears.

This produces evidence that can be replayed, audited, and independently verified.

---

## Governance Learning Loop

DecisionAssure continuously learns.

Unknown capabilities are not discarded.

They enter a governance review workflow.

Unknown Capability
→ Human Review
→ Ontology Update
→ Historical Replay
→ Governance Improvement

Every approval expands governance knowledge.

Every ontology update becomes auditable.

Every historical replay measures governance impact.

---

## Governance Knowledge Accumulation Index (GKAI)

Most governance systems measure compliance.

DecisionAssure measures learning.

GKAI tracks:

* Governance knowledge growth
* Ontology expansion
* Capability coverage improvements
* Knowledge gained per review cycle

Example:

Base Coverage: 23.1%

After Ontology Evolution: 28.6%

Knowledge Gain: +5.5%

GKAI provides a quantitative measure of governance maturity.

---

## Historical Replay

When governance knowledge changes, the system asks:

"What incidents would have been detected if this capability had been known earlier?"

DecisionAssure replays historical traces using the evolved ontology and calculates:

* Previously missed incidents
* Newly detected incidents
* Coverage improvements
* Governance impact

This transforms governance from static policy into a continuously improving system.

---

## Architecture

Trace Files
↓
Capability Discovery
↓
Classification
↓
Capability Witness
↓
Counterfactual Verification
↓
Governance Recommendation
↓
Review Queue
↓
Human Analyst
↓
Ontology Evolution
↓
Historical Replay
↓
Coverage Analysis
↓
GKAI

---

## Key Capabilities

### Emergent Capability Discovery

Discovers capabilities directly from traces without requiring predefined labels.

### Capability Witness Engine

Generates replayable evidence artifacts.

### Counterfactual Verification

Proves minimal capability requirements.

### TRACE-Compatible Claims

Exports capability witnesses as governance evidence.

### Human Review Queue

Routes unknown capabilities to analysts.

### Ontology Evolution

Converts reviewed capabilities into governance knowledge.

### Historical Replay

Measures the impact of newly acquired governance knowledge.

### GKAI

Tracks long-term governance learning.

---

## Example Governance Outcome

Before Learning

Classification Rate: 75%

Unknown Capabilities: 1

After Learning

Classification Rate: 100%

Unknown Capabilities: 0

Governance Improvement

+25% Classification Rate

+5.5% Ontology Coverage

+3 Historical Incidents Detected

---

## Vision

Security systems answer:

"What happened?"

Governance systems answer:

"Was it allowed?"

DecisionAssure answers:

"What capability emerged, how do we prove it existed, and how does governance improve after learning about it?"



📦 1. Install Dependencies

bash
cd /Users/akhileshwarik/agent-governance-toolkit/decisionassure_continuity
pip install -r requirements.txt
Or install the package in editable mode:

bash
pip install -e .
🔍 2. Run the End‑to‑End Demo

bash
python examples/review_queue_demo.py
This runs the full governance learning loop:

Capability discovery
Review queue submission
Human approval simulation
Ontology evolution
Historical replay
Coverage curve & GKAI output
Clean start (reset data):

bash
rm -rf data/ evolved_ontology.json coverage_history.json
python examples/review_queue_demo.py
📊 3. Run the Batch Witness Engine

Process a directory of traces (e.g., sample_traces_large/):

bash
python examples/batch_witness_demo.py sample_traces_large/ --framework autogen --learn
Options:

Argument	Description
--framework	autogen, langgraph, crewai, openai, agenttrust
--min_samples	Minimum traces per cluster (default 3)
--eps	DBSCAN clustering parameter (default 0.5)
--confidence_threshold	Accept only witnesses above this (default 0.5)
--learn	Enable the governance learning loop (suggest labels)
Example with custom values:

bash
python examples/batch_witness_demo.py ./my_traces/ --framework autogen --min_samples 5 --eps 0.3 --confidence_threshold 0.6 --learn
🧪 4. Run the Real‑Trace Demo (Single Directory)

bash
python examples/real_trace_demo.py sample_traces_large/ autogen 2 0.5
Arguments: directory framework min_samples eps

🖥️ 5. CLI Commands

The continuity CLI is available after installation:

bash
continuity --help
Verify Continuity

bash
continuity verify witnesses.json --output result.json
Generate Capability Witness

bash
continuity witness '{"agent":"alice","action":"read_database"}'
Show Capability Lineage

bash
continuity lineage '[{"agent":"alice","action":"read_database"},{"agent":"bob","action":"export_data"}]'
Detect Collusion

bash
continuity collusion '{"alice":[0.9,0.8,0.7],"bob":[0.1,0.2,0.3]}'
Discover Capabilities from Traces

bash
continuity discover traces.json
Run Capability Court (End‑to‑End Verdict)

bash
continuity court traces.json --output verdicts.json
List Known Capabilities

bash
continuity capabilities
🧪 6. Run Unit Tests

bash
pytest tests/
Run a specific test file:

bash
pytest tests/test_ccv_engine.py -v
📁 7. Generate Sample Traces (for Testing)

bash
python examples/generate_sample_traces.py
This creates 150 synthetic traces in sample_traces_large/.

🧠 8. Key Modules Overview

Module	Purpose
src/capability_discovery.py	Unsupervised discovery of capability clusters from traces
src/capability_witness.py	Cryptographic witness generation
src/capability_witness_language.py	Formal witness language format
src/capability_replay.py	Replay verification engine
src/capability_learner.py	Review queue, label suggestion, novelty/impact/priority scoring
src/capability_review_queue.py	Persistence for review queue & ontology ledger
src/capability_drift_replay.py	Historical replay and counterfactual analytics
src/governance_coverage_curve.py	Coverage tracking & GKAI
src/capability_ontology.py	Known & hidden patterns, combined ontology loading
src/adapters/	Parsers for AutoGen, LangGraph, CrewAI, OpenAI Agents, AgentTrust
src/continuity_cli.py	Command-line interface
🚀 9. Tips for Development

Reset all state before a clean run: rm -rf data/ evolved_ontology.json coverage_history.json
Check coverage history after runs: cat coverage_history.json
View evolved ontology: cat evolved_ontology.json
Check review queue: cat data/review_queue.json
Check ontology ledger: cat data/ontology_ledger.json
✅ 10. Quick Test Sequence

bash
rm -rf data/ evolved_ontology.json coverage_history.json
python examples/generate_sample_traces.py
python examples/review_queue_demo.py
python examples/batch_witness_demo.py sample_traces_large/ --framework autogen --learn
continuity capabilities
You should see discovery, review, approval, replay, and the coverage curve.


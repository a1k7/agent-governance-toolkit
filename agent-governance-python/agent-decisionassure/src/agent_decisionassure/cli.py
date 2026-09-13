# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""CLI for DecisionAssure Impact – fail-closed."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import List

import click

from .engine import ImpactEngine
from .loaders import (
    AuthorityError,
    PolicyError,
    TraceError,
    load_authority,
    load_policy,
    load_traces,
)
from .models.trace import Action, DecisionTrace, TraceBatch
from .models.impact import ImpactReport

logger = logging.getLogger(__name__)

_EXIT_USAGE = 2  # usage / input error
_EXIT_BLOCK = 1  # governance regression
_EXIT_OK = 0


@click.group()
def cli():
    """DecisionAssure Impact – governance change impact analysis."""
    pass


def _build_trace_batches(raw_records: List[dict]) -> List[TraceBatch]:
    batches: List[TraceBatch] = []
    for data in raw_records:
        decisions = []
        for d in data.get("decisions", []):
            a = d.get("action", {})
            action = Action(
                id=a.get("id"),
                name=a.get("name", ""),
                parameters=a.get("parameters", {}),
                tool=a.get("tool", ""),
                version=a.get("version", ""),
                transaction_amount=a.get("transaction_amount"),
            )
            model_version = d.get("context", {}).get("model_version", "") or d.get("model_version", "")
            decisions.append(
                DecisionTrace(
                    action=action,
                    agent_id=d.get("agent_id"),
                    agent_version=d.get("agent_version", ""),
                    timestamp=d.get("timestamp"),
                    policy_version=d.get("policy_version", ""),
                    authority_chain=d.get("authority_chain", []),
                    context=d.get("context", {}),
                    evidence_used=d.get("evidence_used", []),
                    evidence_age_hours=d.get("context", {}).get("evidence_age_hours", 0.0),
                    tool_permissions_at_time=d.get("tool_permissions_at_time", []),
                    model_version=model_version,
                    result=d.get("result", ""),
                )
            )
        batches.append(
            TraceBatch(
                trace_id=data.get("trace_id"),
                decisions=decisions,
                environment=data.get("environment", {}),
                metadata=data.get("metadata", {}),
            )
        )
    return batches


@cli.command()
@click.option("--traces", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--policy-current", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--policy-proposed", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--authority", required=True, type=click.Path(exists=True, dir_okay=False),
              help="Path to authority YAML (required).")
@click.option("--output-json", type=click.Path(dir_okay=False))
@click.option("--verbose", is_flag=True)
def impact(traces, policy_current, policy_proposed, authority, output_json, verbose):
    """Run counterfactual impact analysis."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    try:
        trace_batches = _build_trace_batches(load_traces(traces))
        curr_policy = load_policy(policy_current)
        prop_policy = load_policy(policy_proposed)
        authority_data = load_authority(authority)
    except (TraceError, PolicyError, AuthorityError) as exc:
        click.echo(f"❌ Input error: {exc}", err=True)
        sys.exit(_EXIT_USAGE)

    engine = ImpactEngine(trace_batches)
    report = engine.analyze_impact(curr_policy, authority_data, prop_policy, authority_data)

    print_report(report)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json", exclude_none=True), f, indent=2, default=str)
        click.echo(f"Report saved to {output_json}")

    if report.recommendation == "BLOCK":
        click.echo("❌ BLOCK recommended", err=True)
        sys.exit(_EXIT_BLOCK)
    sys.exit(_EXIT_OK)


@cli.command("detect-drift")
@click.option("--traces", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--policy-current", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--drift-threshold", default=1.0, type=float)
def detect_drift(traces, policy_current, drift_threshold):
    """Detect governance drift in production traces."""
    try:
        trace_batches = _build_trace_batches(load_traces(traces))
        load_policy(policy_current)  # validate
    except (TraceError, PolicyError, AuthorityError) as exc:
        click.echo(f"❌ Input error: {exc}", err=True)
        sys.exit(_EXIT_USAGE)

    if not trace_batches:
        click.echo("❌ No traces loaded", err=True)
        sys.exit(_EXIT_USAGE)

    drifted = 0
    for tb in trace_batches:
        for decision in tb.decisions:
            if decision.evidence_age_hours > drift_threshold:
                drifted += 1
                break

    total = len(trace_batches)
    rate = (drifted / total * 100) if total else 0.0
    click.echo(f"Sessions analyzed: {total}")
    click.echo(f"Sessions with drift: {drifted}")
    click.echo(f"Drift rate: {rate:.2f}%")


def print_report(report: ImpactReport):
    print("\n" + "=" * 80)
    print("  DECISIONASSURE IMPACT REPORT")
    print("=" * 80)
    print(f"\nChange: {report.change_description}")
    print("-" * 80)
    print(f"Traces analyzed:              {report.total_traces_analyzed:>15,}")
    print(f"Decisions evaluated:          {report.total_decisions_evaluated:>15,}")
    print(f"ADMISSIBLE → INADMISSIBLE:    {report.transitions.admissible_to_inadmissible:>15,}")
    print(f"INADMISSIBLE → ADMISSIBLE:    {report.transitions.inadmissible_to_admissible:>15,}")
    print(f"Unchanged:                    {report.transitions.unchanged:>15,}")
    print(f"Impact rate:                  {report.impact_rate:>14.2f}%")
    print(f"Agents affected:              {len(report.blast_radius.agents_affected):>15}")
    print(f"Tools affected:               {len(report.blast_radius.tools_affected):>15}")
    exposure = report.estimated_exposure
    exposure_str = f"₹{exposure/1e7:,.2f} crore" if exposure >= 1e7 else f"₹{exposure:,.2f}"
    print(f"Estimated exposure:           {exposure_str:>15}")
    print(f"Severity:                     {report.severity:>15}")
    print(f"Recommendation:               {report.recommendation:>15}")
    if report.per_decision_explanations:
        print("-" * 80)
        print("TOP 5 AFFECTED DECISIONS")
        for i, (aid, expl) in enumerate(list(report.per_decision_explanations.items())[:5]):
            print(f"  {i+1}. {aid[:8]}: {expl}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    cli()

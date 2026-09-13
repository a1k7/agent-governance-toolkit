# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""CLI for DecisionAssure Impact - fail-closed, exit codes 0/1/2."""
from __future__ import annotations

import json
import logging
import sys

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
from .models.impact import ImpactReport

logger = logging.getLogger(__name__)

_EXIT_USAGE = 2
_EXIT_BLOCK = 1
_EXIT_OK = 0


@click.group()
def cli():
    """DecisionAssure Impact - governance change impact analysis."""
    pass


@cli.command()
@click.option("--traces", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--policy-current", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--policy-proposed", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--authority", "authority_shared", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Single authority YAML used for both baseline and proposed.")
@click.option("--authority-current", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Baseline authority YAML.")
@click.option("--authority-proposed", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Proposed authority YAML.")
@click.option("--output-json", type=click.Path(dir_okay=False), default=None)
@click.option("--verbose", is_flag=True)
def impact(traces, policy_current, policy_proposed,
           authority_shared, authority_current, authority_proposed, output_json, verbose):
    """Run counterfactual impact analysis."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    if authority_current and authority_proposed:
        baseline_auth_path, proposed_auth_path = authority_current, authority_proposed
    elif authority_shared:
        baseline_auth_path = proposed_auth_path = authority_shared
    else:
        click.echo(
            "Provide either --authority (single) or both --authority-current and --authority-proposed.",
            err=True,
        )
        sys.exit(_EXIT_USAGE)

    try:
        trace_batches = load_traces(traces)
        curr_policy = load_policy(policy_current)
        prop_policy = load_policy(policy_proposed)
        baseline_auth = load_authority(baseline_auth_path)
        proposed_auth = load_authority(proposed_auth_path)
    except (TraceError, PolicyError, AuthorityError) as exc:
        click.echo(f"Input error: {exc}", err=True)
        sys.exit(_EXIT_USAGE)

    engine = ImpactEngine(trace_batches)
    report = engine.analyze_impact(curr_policy, baseline_auth, prop_policy, proposed_auth)

    print_report(report)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json", exclude_none=True), f, indent=2, default=str)
        click.echo(f"Report saved to {output_json}")

    if report.recommendation == "BLOCK":
        click.echo("BLOCK recommended", err=True)
        sys.exit(_EXIT_BLOCK)
    sys.exit(_EXIT_OK)


@cli.command("detect-drift")
@click.option("--traces", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--drift-threshold", default=1.0, type=float,
              help="Evidence age threshold in hours. Decisions older than this are 'drifted'.")
def detect_drift(traces, drift_threshold):
    """Detect evidence drift in production traces."""
    try:
        trace_batches = load_traces(traces)
    except TraceError as exc:
        click.echo(f"Input error: {exc}", err=True)
        sys.exit(_EXIT_USAGE)

    if not trace_batches:
        click.echo("No traces loaded", err=True)
        sys.exit(_EXIT_USAGE)

    drifted_sessions = 0
    total_decisions = 0
    for tb in trace_batches:
        session_drifted = False
        for decision in tb.decisions:
            total_decisions += 1
            if decision.evidence_age_hours > drift_threshold:
                session_drifted = True
        if session_drifted:
            drifted_sessions += 1

    total = len(trace_batches)
    rate = (drifted_sessions / total * 100) if total else 0.0
    click.echo(f"Sessions analyzed: {total}")
    click.echo(f"Decisions analyzed: {total_decisions}")
    click.echo(f"Sessions with drift: {drifted_sessions}")
    click.echo(f"Drift rate: {rate:.2f}%")
    if drifted_sessions > 0:
        click.echo("Drift detected - exiting non-zero", err=True)
        sys.exit(_EXIT_BLOCK)
    sys.exit(_EXIT_OK)

def print_report(report: ImpactReport):
    print("\n" + "=" * 80)
    print("  DECISIONASSURE IMPACT REPORT")
    print("=" * 80)
    print(f"\nChange: {report.change_description}")
    print("-" * 80)
    print(f"Traces analyzed:              {report.total_traces_analyzed:>15,}")
    print(f"Decisions evaluated:          {report.total_decisions_evaluated:>15,}")
    print(f"ADMISSIBLE to INADMISSIBLE:   {report.transitions.admissible_to_inadmissible:>15,}")
    print(f"INADMISSIBLE to ADMISSIBLE:   {report.transitions.inadmissible_to_admissible:>15,}")
    print(f"Unchanged:                    {report.transitions.unchanged:>15,}")
    print(f"Impact rate:                  {report.impact_rate:>14.2f}%")
    print(f"Agents affected:              {len(report.blast_radius.agents_affected):>15}")
    print(f"Tools affected:               {len(report.blast_radius.tools_affected):>15}")
    exposure = report.estimated_exposure
    print(f"Estimated exposure:           INR {exposure:>13,.2f}")
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

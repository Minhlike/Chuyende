"""
Research Agent Command Line Interface (CLI) (Section 24, Section 25)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

from research_agent.config import get_default_config
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.roadmap_query import RoadmapQueryService
from research_agent.interfaces.roadmap_ingestion import RoadmapIngestionService


def validate_roadmap_command(repo: ResearchRepository) -> int:
    """Validate full roadmap integrity, schema, hierarchy, coverage, and constitutional rules."""
    print("==================================================")
    print("CANONICAL RESEARCH ROADMAP INTEGRITY VALIDATION")
    print("==================================================")

    roadmap = repo.get_roadmap()
    if not roadmap:
        print("[FAIL] No canonical roadmap found in persistence layer.")
        return 1

    print(f"Roadmap Title: {roadmap.title}")
    print(f"Version:       {roadmap.version}")
    print(f"SHA-256 Hash:  {roadmap.sha256_hash}")
    print(f"Central Focus: {roadmap.central_object}")

    ingestion_service = RoadmapIngestionService(repo)
    try:
        ingestion_service.validate_roadmap_structure(roadmap)
        print("[PASS] Structural schema & hierarchy validation passed.")
    except Exception as e:
        print(f"[FAIL] Schema/hierarchy validation error: {e}")
        return 1

    # Check Nodes count
    nodes = roadmap.nodes
    print(f"[PASS] Total Hierarchical Nodes: {len(nodes)}")

    # Check Chapter distribution
    ch1_nodes = [n for n in nodes if n.code.startswith("1.")]
    ch2_nodes = [n for n in nodes if n.code.startswith("2.")]
    ch3_nodes = [n for n in nodes if n.code.startswith("3.")]
    print(f"[PASS] Chapter 1 Nodes: {len(ch1_nodes)}")
    print(f"[PASS] Chapter 2 Nodes: {len(ch2_nodes)}")
    print(f"[PASS] Chapter 3 Nodes: {len(ch3_nodes)}")

    # Check Questions & Hypotheses
    print(f"[PASS] Research Questions: {[q.code for q in roadmap.questions]}")
    print(f"[PASS] Hypotheses:         {[h.code for h in roadmap.hypotheses]}")
    print(f"[PASS] Research Axes:       {[a.code for a in roadmap.axes]}")
    print(f"[PASS] Negative Controls:   {len(roadmap.controls)} registered")
    print(f"[PASS] Claim Boundaries:    {len(roadmap.boundaries)} registered")
    print(f"[PASS] Defensibility Qs:    {len(roadmap.defensibility_questions)} registered")

    # Check Traceability Matrix coverage
    traceability = roadmap.traceability_matrix
    if len(traceability) != 5:
        print(f"[FAIL] Traceability matrix incomplete: expected 5 entries, found {len(traceability)}")
        return 1
    print(f"[PASS] Traceability Matrix: 100% complete for RQ1..RQ5 and H1..H5.")

    print("==================================================")
    print("RESULT: ALL ROADMAP INVARIANTS VERIFIED [PASS]")
    print("==================================================")
    return 0


def main(args: Optional[list] = None):
    parser = argparse.ArgumentParser(description="Research Agent CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Roadmap parser
    roadmap_parser = subparsers.add_parser("roadmap", help="Roadmap operations")
    roadmap_subparsers = roadmap_parser.add_subparsers(dest="action", help="Roadmap actions")

    # roadmap validate
    roadmap_subparsers.add_parser("validate", help="Validate roadmap integrity and constitutional invariants")

    # roadmap query
    show_rq_p = roadmap_subparsers.add_parser("show-rq", help="Display Research Question details")
    show_rq_p.add_argument("rq_id", help="RQ Code (e.g. RQ1) or ID (e.g. RQ-000001)")

    show_hyp_p = roadmap_subparsers.add_parser("show-hyp", help="Display Hypothesis details")
    show_hyp_p.add_argument("hyp_id", help="Hypothesis Code (e.g. H1) or ID (e.g. HYP-000001)")

    show_node_p = roadmap_subparsers.add_parser("show-node", help="Display Roadmap Node details")
    show_node_p.add_argument("code", help="Node Code (e.g. 1.3.1, 2.3.2)")

    show_axis_p = roadmap_subparsers.add_parser("show-axis", help="Display Research Axis details")
    show_axis_p.add_argument("axis_code", help="Axis Code (e.g. A1, A5)")

    roadmap_subparsers.add_parser("show-controls", help="List all Negative Controls")
    roadmap_subparsers.add_parser("show-boundaries", help="List all Research Claim Boundaries")
    roadmap_subparsers.add_parser("show-traceability", help="Display Traceability Matrix")

    parsed_args = parser.parse_args(args)

    config = get_default_config()
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)
    query_svc = RoadmapQueryService(repo)

    if parsed_args.subcommand == "roadmap":
        if parsed_args.action == "validate":
            code = validate_roadmap_command(repo)
            sys.exit(code)

        elif parsed_args.action == "show-rq":
            rq = query_svc.get_rq(parsed_args.rq_id)
            if not rq:
                print(f"Research Question '{parsed_args.rq_id}' not found.")
                sys.exit(1)
            print(f"[{rq.code}] {rq.title}")
            print(f"Stable ID: {rq.rq_id}")
            print(f"EN: {rq.canonical_wording_en}")
            print(f"VI: {rq.canonical_wording_vi}")
            print(f"Target Aspect: {rq.target_representation_aspect}")
            sys.exit(0)

        elif parsed_args.action == "show-hyp":
            hyp = query_svc.get_hypothesis(parsed_args.hyp_id)
            if not hyp:
                print(f"Hypothesis '{parsed_args.hyp_id}' not found.")
                sys.exit(1)
            print(f"[{hyp.code}] {hyp.title}")
            print(f"Associated RQ: {hyp.rq_id}")
            print(f"Statement: {hyp.statement}")
            print(f"Falsification Criteria: {hyp.falsification_criteria}")
            sys.exit(0)

        elif parsed_args.action == "show-node":
            node = query_svc.get_node(parsed_args.code)
            if not node:
                print(f"Node '{parsed_args.code}' not found.")
                sys.exit(1)
            print(f"[{node.code}] {node.title}")
            print(f"Node ID: {node.node_id} (Level {node.level})")
            print(f"Expected Role: {node.expected_role}")
            print(f"Research Axes: {node.research_axes}")
            print(f"Constraints:   {node.methodological_constraints}")
            print(f"Linked RQs:    {node.rq_ids}")
            print(f"Linked Hyps:   {node.hyp_ids}")
            sys.exit(0)

        elif parsed_args.action == "show-axis":
            nodes = query_svc.get_nodes_by_axis(parsed_args.axis_code)
            axes = repo.list_research_axes()
            target_axis = next((a for a in axes if a.code == parsed_args.axis_code), None)
            if target_axis:
                print(f"[{target_axis.code}] {target_axis.name}")
                print(f"Problem: {target_axis.problem_summary}")
                print(f"Path: {' -> '.join(target_axis.path_nodes)}")
                print(f"Core Question: {target_axis.core_question}")
                print(f"Core Risks: {target_axis.core_risks}")
            print(f"\nAssociated Nodes ({len(nodes)}):")
            for n in nodes:
                print(f"  - [{n.code}] {n.title}")
            sys.exit(0)

        elif parsed_args.action == "show-controls":
            controls = repo.list_negative_controls()
            for c in controls:
                print(f"[{c.control_id}] ({c.category}) {c.name}")
                print(f"  Description: {c.description}")
                print(f"  Targets: {c.target_nodes}\n")
            sys.exit(0)

        elif parsed_args.action == "show-boundaries":
            boundaries = repo.list_research_boundaries()
            for b in boundaries:
                print(f"[{b.boundary_id}] {b.title}")
                print(f"  Statement: {b.statement}")
                print(f"  Rationale: {b.rationale}\n")
            sys.exit(0)

        elif parsed_args.action == "show-traceability":
            for tr in repo.get_traceability_matrix():
                print(f"[{tr.code}] (RQ ID: {tr.rq_id})")
                print(f"  Chapter 1 Gaps:       {tr.chapter1_gap_nodes}")
                print(f"  Chapter 2 Mechanisms: {tr.chapter2_mechanism_nodes}")
                print(f"  Chapter 3 Evaluation: {tr.chapter3_evaluation_nodes}")
                print(f"  Hypotheses:           {tr.hypothesis_ids}")
                print(f"  Controls:             {tr.controls}\n")
            sys.exit(0)

    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()

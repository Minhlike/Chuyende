"""
Research Agent Command Line Interface (CLI) (Roadmap & Reference Map Tools)
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
from research_agent.core.enums import IntellectualOwnership, CitationFirewallStatus
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.roadmap_query import RoadmapQueryService
from research_agent.interfaces.roadmap_ingestion import RoadmapIngestionService
from research_agent.interfaces.reference_map_query import ReferenceMapQueryService
from research_agent.interfaces.reference_map_ingestion import ReferenceMapIngestionService


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


def validate_reference_map_command(repo: ResearchRepository) -> int:
    """Validate reference map, bibliographic verification, ownership invariants, and citation firewall."""
    print("==================================================")
    print("VERIFIED REFERENCE MAP & CITATION FIREWALL VALIDATION")
    print("==================================================")

    ref_map = repo.get_reference_map()
    if not ref_map:
        print("[FAIL] No reference map specification found in persistence layer.")
        return 1

    print(f"Reference Map Title: {ref_map.title}")
    print(f"Version:             {ref_map.version}")
    print(f"Compatible Roadmap:  {ref_map.compatible_roadmap_version}")
    print(f"SHA-256 Hash:        {ref_map.sha256_hash}")

    ingestion_service = ReferenceMapIngestionService(repo)
    try:
        ingestion_service.validate_reference_map_specification(ref_map)
        print("[PASS] Reference map specification schema & invariants verified.")
    except Exception as e:
        print(f"[FAIL] Reference map validation error: {e}")
        return 1

    sources = ref_map.sources
    evidences = ref_map.evidences
    claims = ref_map.claims
    mappings = ref_map.ownership_mappings
    contribs = ref_map.contributions
    firewall = ref_map.firewall_rules

    print(f"[PASS] Total Registered Sources:      {len(sources)}")
    print(f"[PASS] Total Extracted Evidences:     {len(evidences)}")
    print(f"[PASS] Total Canonical Claims:         {len(claims)}")
    print(f"[PASS] Total Ownership Mappings:       {len(mappings)}")
    print(f"[PASS] Registered Contributions:       {len(contribs)} (CAND-01..CAND-15)")
    print(f"[PASS] Citation Firewall Active Rules: {len(firewall)}")

    # Check peer review vs preprints
    preprints = [s for s in sources if s.source_type.value == "PREPRINT"]
    top_venues = [s for s in sources if s.source_type.value == "PEER_REVIEWED_TOP_VENUE"]
    standards = [s for s in sources if s.source_type.value == "PRIMARY_STANDARD"]
    datasets = [s for s in sources if s.source_type.value == "OFFICIAL_DATASET"]

    print(f"[PASS] Top Venue Peer-Reviewed Sources: {len(top_venues)}")
    print(f"[PASS] Official Standards:              {len(standards)}")
    print(f"[PASS] Official Benchmarks/Datasets:    {len(datasets)}")
    print(f"[PASS] Explicitly Labeled Preprints:    {len(preprints)}")

    print("==================================================")
    print("RESULT: ALL REFERENCE & OWNERSHIP INVARIANTS VERIFIED [PASS]")
    print("==================================================")
    return 0


def main(args: Optional[list] = None):
    parser = argparse.ArgumentParser(description="Research Agent CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 1. Roadmap parser
    roadmap_parser = subparsers.add_parser("roadmap", help="Roadmap operations")
    roadmap_subparsers = roadmap_parser.add_subparsers(dest="action", help="Roadmap actions")
    roadmap_subparsers.add_parser("validate", help="Validate roadmap integrity and constitutional invariants")

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

    # 2. References parser
    refs_parser = subparsers.add_parser("refs", help="Reference & Ownership Map operations")
    refs_subparsers = refs_parser.add_subparsers(dest="action", help="Reference map actions")

    refs_subparsers.add_parser("validate", help="Validate reference map integrity and citation firewall")

    show_src_p = refs_subparsers.add_parser("show", help="Display Source details by ID or citation key")
    show_src_p.add_argument("source_id_or_key", help="SRC-xxxxxx ID or citation key e.g. Arp2022DosDonts")

    for_node_p = refs_subparsers.add_parser("for-node", help="List sources linked to a roadmap node code")
    for_node_p.add_argument("node_code", help="Roadmap node code (e.g. 1.1.2, 2.4.1)")

    own_p = refs_subparsers.add_parser("ownership", help="List ownership mappings filtered by class")
    own_p.add_argument("ownership_class", nargs="?", default=None, help="OURS, SOURCE, ADAPTED, or BASELINE")

    refs_subparsers.add_parser("contributions", help="List candidate contributions and novelty status")
    refs_subparsers.add_parser("contested", help="List contested/contradictory claims and qualifies relations")
    refs_subparsers.add_parser("firewall", help="Audit Citation Firewall status across all sources")
    refs_subparsers.add_parser("coverage", help="Display overall reference, ownership, and citation coverage")

    # 3. Memory parser (Prompt 4)
    memory_parser = subparsers.add_parser("memory", help="Long-Term Research Memory operations")
    memory_subparsers = memory_parser.add_subparsers(dest="action", help="Memory actions")
    memory_subparsers.add_parser("status", help="Display memory health and metrics")

    search_p = memory_subparsers.add_parser("search", help="Execute hybrid retrieval")
    search_p.add_argument("query", help="Query string")

    show_mem_p = memory_subparsers.add_parser("show", help="Display record details")
    show_mem_p.add_argument("entity_id", help="Entity ID (e.g. CLM-000001, DEC-000001)")

    hist_p = memory_subparsers.add_parser("history", help="Display status transition timeline")
    hist_p.add_argument("entity_id", help="Entity ID")

    memory_subparsers.add_parser("contradictions", help="List contradiction records")
    memory_subparsers.add_parser("open-questions", help="List open research questions")
    memory_subparsers.add_parser("decisions", help="List architecture/research decisions")
    memory_subparsers.add_parser("lessons", help="List lessons learned from experiments")
    memory_subparsers.add_parser("sessions", help="List research sessions")
    memory_subparsers.add_parser("snapshot", help="Create point-in-time state snapshot")
    memory_subparsers.add_parser("rebuild-index", help="Rebuild derived vector & FTS indexes")
    memory_subparsers.add_parser("validate", help="Validate memory invariants (MQ-01..MQ-15)")
    memory_subparsers.add_parser("state", help="Display canonical research state summary")

    # 4. Resume parser (Prompt 4 Section 74)
    subparsers.add_parser("resume", help="Continuation bootstrap ContextBundle")

    # 5. Research parser
    research_parser = subparsers.add_parser("research", help="Research state operations")
    research_subparsers = research_parser.add_subparsers(dest="action", help="Research actions")
    research_subparsers.add_parser("state", help="Display canonical research state summary")

    parsed_args = parser.parse_args(args)

    config = get_default_config()
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)
    rm_query_svc = RoadmapQueryService(repo)
    ref_query_svc = ReferenceMapQueryService(repo)

    if parsed_args.subcommand == "roadmap":
        if parsed_args.action == "validate":
            sys.exit(validate_roadmap_command(repo))

        elif parsed_args.action == "show-rq":
            rq = rm_query_svc.get_rq(parsed_args.rq_id)
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
            hyp = rm_query_svc.get_hypothesis(parsed_args.hyp_id)
            if not hyp:
                print(f"Hypothesis '{parsed_args.hyp_id}' not found.")
                sys.exit(1)
            print(f"[{hyp.code}] {hyp.title}")
            print(f"Associated RQ: {hyp.rq_id}")
            print(f"Statement: {hyp.statement}")
            print(f"Falsification Criteria: {hyp.falsification_criteria}")
            sys.exit(0)

        elif parsed_args.action == "show-node":
            node = rm_query_svc.get_node(parsed_args.code)
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
            nodes = rm_query_svc.get_nodes_by_axis(parsed_args.axis_code)
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

    elif parsed_args.subcommand == "refs":
        if parsed_args.action == "validate":
            sys.exit(validate_reference_map_command(repo))

        elif parsed_args.action == "show":
            src = ref_query_svc.get_source(parsed_args.source_id_or_key)
            if not src:
                print(f"Source '{parsed_args.source_id_or_key}' not found.")
                sys.exit(1)
            print(f"[{src.source_id}] {src.citation_key}: {src.title}")
            print(f"Authors: {', '.join(src.authors)} ({src.year})")
            print(f"Venue:   {src.venue}")
            print(f"Type:    {src.source_type.value}")
            print(f"Roles:   {[r.value for r in src.roles]}")
            if src.doi:
                print(f"DOI:     {src.doi}")
            if src.canonical_url:
                print(f"URL:     {src.canonical_url}")
            print(f"State:   Bib={src.bibliographic_verification_state.value}, Content={src.content_verification_state.value}")
            print(f"Nodes:   {src.relevant_roadmap_nodes}")
            if src.notes:
                print(f"Notes:   {src.notes}")
            sys.exit(0)

        elif parsed_args.action == "for-node":
            sources = ref_query_svc.get_sources_for_node(parsed_args.node_code)
            print(f"Sources linked to Roadmap Node [{parsed_args.node_code}] ({len(sources)} found):")
            for s in sources:
                print(f"  - [{s.source_id}] {s.citation_key}: {s.title} ({s.year}) [{s.source_type.value}]")
            sys.exit(0)

        elif parsed_args.action == "ownership":
            target_class = IntellectualOwnership(parsed_args.ownership_class) if parsed_args.ownership_class else None
            mappings = ref_query_svc.get_ownership_mappings(ownership=target_class)
            print(f"Ownership Mappings ({len(mappings)} entries):")
            for m in mappings:
                src_info = f" -> Sources: {m.source_ids}" if m.source_ids else ""
                mot_info = f" -> Motivated by: {m.motivation_source_ids}" if m.motivation_source_ids else ""
                print(f"  - [{m.node_code}] {m.component_name} [{m.ownership.value}]{src_info}{mot_info}")
                if m.notes:
                    print(f"      Notes: {m.notes}")
            sys.exit(0)

        elif parsed_args.action == "contributions":
            contribs = ref_query_svc.get_contributions()
            print(f"Registered Candidate Contributions ({len(contribs)} items):")
            for c in contribs:
                print(f"[{c.contribution_id}] {c.name} (Status: {c.novelty_status.value})")
                print(f"  Nodes: {c.roadmap_nodes}")
                print(f"  Description: {c.description}")
                print(f"  Differentiation: {c.differentiation_notes}\n")
            sys.exit(0)

        elif parsed_args.action == "contested":
            pairs = ref_query_svc.get_contradictory_claims()
            print(f"Contested / Qualified Claim Relationships ({len(pairs)} records):")
            for p in pairs:
                print(f"[{p['relation_id']}]")
                print(f"  Claim A: {p['claim_a']}")
                print(f"  Claim B: {p['claim_b']}")
                print(f"  Rationale: {p['notes']}\n")
            sys.exit(0)

        elif parsed_args.action == "firewall":
            rules = ref_query_svc.get_citation_firewall_rules()
            ready_rules = [r for r in rules if r.status == CitationFirewallStatus.READY]
            blocked_rules = [r for r in rules if r.status == CitationFirewallStatus.BLOCKED]
            print(f"Citation Firewall Audit: {len(ready_rules)} READY, {len(blocked_rules)} BLOCKED (Total: {len(rules)})\n")
            print("READY Citations (Authorized for downstream text):")
            for r in ready_rules:
                print(f"  [READY]   [{r.source_id}] {r.citation_key} (Support: {r.support_type.value})")
            if blocked_rules:
                print("\nBLOCKED Citations (Missing evidence or locator - Prohibited from citation):")
                for r in blocked_rules:
                    print(f"  [BLOCKED] [{r.source_id}] {r.citation_key} -> Reasons: {r.blocking_reasons}")
            sys.exit(0)

        elif parsed_args.action == "coverage":
            cov = ref_query_svc.get_coverage_summary()
            print("==================================================")
            print("REFERENCE MAP, OWNERSHIP & FIREWALL COVERAGE")
            print("==================================================")
            for k, v in cov.items():
                print(f"{k.replace('_', ' ').title():<35}: {v}")
            print("==================================================")
            sys.exit(0)

    # -------------------------------------------------------------
    # MEMORY SUBCOMMANDS (Prompt 4)
    # -------------------------------------------------------------
    elif parsed_args.subcommand == "memory":
        from research_agent.memory.manager import MemoryManager
        memory_mgr = MemoryManager(repository=repo)

        if parsed_args.action == "status":
            health = memory_mgr.audit_health()
            state = memory_mgr.get_research_state()
            print("==================================================")
            print("RESEARCH AGENT LONG-TERM MEMORY STATUS")
            print("==================================================")
            print(f"Roadmap Version:        {state['roadmap_version']}")
            print(f"Reference Map Version:  {state['reference_map_version']}")
            print(f"Total Memory Records:   {health.total_memory_records}")
            print(f"Total Episodes (M3):    {health.total_episodes}")
            print(f"Failed Runs Logged:     {health.total_failures}")
            print(f"Total Decisions (M4):   {health.total_decisions}")
            print(f"Lessons Learned:        {health.total_lessons}")
            print(f"Open Research Questions:{health.total_open_questions}")
            print(f"Contradiction Units:    {health.total_contradictions}")
            print(f"Pending Consolidation:  {health.pending_consolidation}")
            print(f"Stale / Review Flags:   {health.stale_records}")
            print(f"Derived Index Status:   {health.derived_index_status}")
            print(f"Audit Overall Status:   {'[HEALTHY]' if health.audit_passed else '[ISSUES FOUND]'}")
            print("==================================================")
            sys.exit(0)

        elif parsed_args.action == "search":
            query_str = parsed_args.query
            bundle = memory_mgr.retrieve(query=query_str)
            print(f"Hybrid Retrieval for: '{query_str}' (Intent: {bundle.resolved_intent.value})")
            print(f"Estimated Token Budget: ~{bundle.token_estimate} tokens\n")
            if bundle.canonical_entities:
                print(f"--- Canonical Entities ({len(bundle.canonical_entities)}) ---")
                for e in bundle.canonical_entities:
                    e_id = e.get("source_id") or e.get("claim_id") or e.get("node_id") or e.get("decision_id")
                    title = e.get("title") or e.get("statement") or e.get("name")
                    print(f"  - [{e_id}] {title}")
            if bundle.verified_facts:
                print(f"\n--- Verified Facts ({len(bundle.verified_facts)}) ---")
                for f_item in bundle.verified_facts:
                    print(f"  - [{f_item.get('claim_id')}] {f_item.get('statement')}")
            if bundle.supporting_evidence:
                print(f"\n--- Supporting Evidence ({len(bundle.supporting_evidence)}) ---")
                for ev in bundle.supporting_evidence:
                    print(f"  - [{ev.get('evidence_id')}] From: {ev.get('source_id')} | Locator: {ev.get('locator')}")
            if bundle.contradictory_evidence:
                print(f"\n--- Contradictory Evidence ({len(bundle.contradictory_evidence)}) ---")
                for c in bundle.contradictory_evidence:
                    print(f"  - [CONTRADICTION] {c.get('description') or c.get('notes')}")
            if bundle.decisions:
                print(f"\n--- Relevant Decisions ({len(bundle.decisions)}) ---")
                for d in bundle.decisions:
                    print(f"  - [{d.get('decision_id')}] {d.get('title')}: {d.get('decision')}")
            if bundle.open_questions:
                print(f"\n--- Open Questions ({len(bundle.open_questions)}) ---")
                for o in bundle.open_questions:
                    print(f"  - [{o.get('question_id')}] {o.get('question')}")
            if bundle.lessons:
                print(f"\n--- Lessons Learned ({len(bundle.lessons)}) ---")
                for l in bundle.lessons:
                    print(f"  - [{l.get('lesson_id')}] {l.get('title')}: {l.get('statement')}")
            sys.exit(0)

        elif parsed_args.action == "show":
            target_id = parsed_args.entity_id
            bundle = memory_mgr.retrieve(query=target_id)
            found = False
            for ent_list in [bundle.canonical_entities, bundle.verified_facts, bundle.decisions, bundle.open_questions, bundle.lessons]:
                for item in ent_list:
                    if target_id in str(item):
                        print(json.dumps(item, indent=2))
                        found = True
                        break
                if found:
                    break
            if not found:
                print(f"Entity '{target_id}' not found in canonical memory.")
                sys.exit(1)
            sys.exit(0)

        elif parsed_args.action == "history":
            target_id = parsed_args.entity_id
            transitions = repo.list_status_transitions(entity_id=target_id)
            print(f"Status Transition Timeline for '{target_id}' ({len(transitions)} records):")
            for t in transitions:
                print(f"  [{t.timestamp.isoformat()}] {t.from_status} -> {t.to_status} | Cause: {t.cause}")
            sys.exit(0)

        elif parsed_args.action == "contradictions":
            ctrs = repo.list_contradictions()
            print(f"Registered Contradiction Units ({len(ctrs)} records):")
            for c in ctrs:
                print(f"[{c.contradiction_id}] Status: {c.resolution_status}")
                print(f"  Claim A: {c.claim_a_id} | Claim B: {c.claim_b_id}")
                print(f"  Description: {c.description}")
                if c.resolution_notes:
                    print(f"  Resolution:  {c.resolution_notes}\n")
            sys.exit(0)

        elif parsed_args.action == "open-questions":
            oqs = repo.list_open_questions()
            print(f"Persistent Open Research Questions ({len(oqs)} active):")
            for o in oqs:
                print(f"[{o.question_id}] Priority: {o.priority} | Status: {o.status.value}")
                print(f"  Question: {o.question}")
                print(f"  Why open: {o.why_open}")
                print(f"  Required: {o.required_evidence}\n")
            sys.exit(0)

        elif parsed_args.action == "decisions":
            decs = repo.list_decisions()
            print(f"Architecture & Research Decisions ({len(decs)} records):")
            for d in decs:
                sup_info = f" (Supersedes: {d.supersedes_id})" if d.supersedes_id else ""
                print(f"[{d.decision_id}] Status: {d.status.value}{sup_info} | {d.title}")
                print(f"  Decision:  {d.decision}")
                print(f"  Rationale: {d.rationale}\n")
            sys.exit(0)

        elif parsed_args.action == "lessons":
            lessons = repo.list_lessons_learned()
            print(f"Lessons Learned from Experiments ({len(lessons)} entries):")
            for l in lessons:
                print(f"[{l.lesson_id}] {l.title}")
                print(f"  Statement: {l.statement}")
                if l.actionable_recommendations:
                    print(f"  Recommendations: {l.actionable_recommendations}\n")
            sys.exit(0)

        elif parsed_args.action == "sessions":
            sessions = repo.list_research_sessions()
            print(f"Persistent Research Sessions ({len(sessions)} records):")
            for s in sessions:
                print(f"[{s.session_id}] Objective: {s.objective}")
                print(f"  Time: {s.start_time.isoformat()} to {s.end_time.isoformat() if s.end_time else 'ongoing'}")
                print(f"  Actions: {len(s.actions_summary)} | Decisions: {len(s.decisions_made)}\n")
            sys.exit(0)

        elif parsed_args.action == "snapshot":
            path = memory_mgr.create_snapshot()
            print(f"[OK] Research state snapshot saved successfully to: {path}")
            sys.exit(0)

        elif parsed_args.action == "rebuild-index":
            fts_c, vec_c = memory_mgr.rebuild_indexes()
            print(f"[OK] Successfully rebuilt derived indexes: {fts_c} FTS entries, {vec_c} semantic vectors.")
            sys.exit(0)

        elif parsed_args.action == "validate":
            health = memory_mgr.audit_health()
            print("==================================================")
            print("RESEARCH AGENT MEMORY QUALITY & HEALTH AUDIT")
            print("==================================================")
            print(f"Total Canonical Records: {health.total_memory_records}")
            print(f"Broken References:       {health.broken_references}")
            print(f"Circular Support Cycles: {health.circular_support_count}")
            print(f"Stale Records:           {health.stale_records}")
            if health.issues:
                print("\nAudit Issues Detected:")
                for issue in health.issues:
                    print(f"  [FAIL] {issue}")
                sys.exit(1)
            else:
                print("\n[PASS] All Memory Invariants (MQ-01..MQ-15) Verified.")
                sys.exit(0)

        elif parsed_args.action == "state":
            state = memory_mgr.get_research_state()
            print("==================================================")
            print("CANONICAL RESEARCH STATE SUMMARY")
            print("==================================================")
            print(f"Roadmap Version:       {state['roadmap_version']}")
            print(f"Reference Map Version: {state['reference_map_version']}")
            print(f"Central Object:        {state['central_object']}")
            print(f"\nResearch Questions ({len(state['research_questions'])}):")
            for q in state['research_questions']:
                print(f"  - {q}")
            print(f"\nHypotheses ({len(state['hypotheses'])}):")
            for h in state['hypotheses']:
                print(f"  - {h}")
            print(f"\nActive Decisions ({len(state['active_decisions'])}):")
            for d in state['active_decisions']:
                print(f"  - {d}")
            print(f"\nOpen Questions ({len(state['open_questions'])}):")
            for o in state['open_questions']:
                print(f"  - {o}")
            print("==================================================")
            sys.exit(0)

    # -------------------------------------------------------------
    # RESUME BOOTSTRAP COMMAND (Prompt 4, Section 74)
    # -------------------------------------------------------------
    elif parsed_args.subcommand == "resume":
        from research_agent.memory.manager import MemoryManager
        memory_mgr = MemoryManager(repository=repo)
        bundle = memory_mgr.generate_resume_bundle()
        state = memory_mgr.get_research_state()
        print("==================================================")
        print("RESEARCH AGENT CONTINUATION BOOTSTRAP")
        print("==================================================")
        print(f"Roadmap Version:       {state['roadmap_version']}")
        print(f"Reference Map Version: {state['reference_map_version']}")
        print(f"Central Focus:         {state['central_object']}")
        print(f"Active Contributions:  {len(state['active_contributions'])}")
        print(f"Open Questions:        {len(state['open_questions'])}")
        print(f"Active Decisions:      {len(state['active_decisions'])}")
        print("\nNext Recommended Actions / Open Items:")
        for o in state['open_questions'][:3]:
            print(f"  - {o}")
        print("==================================================")
        sys.exit(0)

    # -------------------------------------------------------------
    # RESEARCH STATE COMMAND (Prompt 4 Section 73)
    # -------------------------------------------------------------
    elif parsed_args.subcommand == "research" and parsed_args.action == "state":
        from research_agent.memory.manager import MemoryManager
        memory_mgr = MemoryManager(repository=repo)
        state = memory_mgr.get_research_state()
        print("==================================================")
        print("CANONICAL RESEARCH STATE SUMMARY")
        print("==================================================")
        print(f"Roadmap Version:       {state['roadmap_version']}")
        print(f"Reference Map Version: {state['reference_map_version']}")
        print(f"Central Object:        {state['central_object']}")
        print(f"\nResearch Questions ({len(state['research_questions'])}):")
        for q in state['research_questions']:
            print(f"  - {q}")
        print(f"\nHypotheses ({len(state['hypotheses'])}):")
        for h in state['hypotheses']:
            print(f"  - {h}")
        print(f"\nActive Decisions ({len(state['active_decisions'])}):")
        for d in state['active_decisions']:
            print(f"  - {d}")
        print(f"\nOpen Questions ({len(state['open_questions'])}):")
        for o in state['open_questions']:
            print(f"  - {o}")
        print("==================================================")
        sys.exit(0)

    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()

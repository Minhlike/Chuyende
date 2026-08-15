"""
Comprehensive Test Suite for Scientific Reasoning Engine, Argumentation & Research Skills (Prompt 5)
"""

import pytest
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.manager import MemoryManager
from research_agent.reasoning.engine import ScientificReasoningEngine
from research_agent.skills.registry import ResearchSkillRegistry
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    ReasoningMode,
    EvidenceAlignmentStatus,
    ContradictionType,
    ArgumentReadinessState,
    ReasoningIssueType,
    NoveltyReasoningState,
    VerificationRequestType,
    VerificationRequestStatus,
    ArgumentNodeType,
    ArgumentEdgeType,
    ArgumentPatternType,
)
from research_agent.schemas.claim import Claim
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.roadmap import Hypothesis, ResearchQuestion
from research_agent.schemas.ownership import CandidateContribution
from research_agent.schemas.memory import EpisodeRecord
from research_agent.schemas.reasoning import (
    ArgumentNode,
    ArgumentEdge,
    ClaimScope,
    VerificationRequest,
    DiscoursePlan,
)


@pytest.fixture
def test_env(tmp_path):
    db_file = tmp_path / "test_research.db"
    db_mgr = DatabaseManager(db_path=str(db_file))
    repo = ResearchRepository(db_mgr)
    memory_mgr = MemoryManager(repository=repo)
    engine = ScientificReasoningEngine(repo=repo, memory_mgr=memory_mgr)
    registry = ResearchSkillRegistry()
    return {"repo": repo, "engine": engine, "registry": registry, "memory_mgr": memory_mgr}


# ----------------------------------------------------------------------
# GOLDEN REASONING TESTS (GOLD-01 .. GOLD-05)
# ----------------------------------------------------------------------

def test_gold_01_claim_normalization_and_scope_extraction(test_env):
    """GOLD-01: Claim Normalization, Qualifier Preservation, and Scope Extraction."""
    engine = test_env["engine"]
    raw_text = (
        "Drain parser extracts static templates with high fidelity on HDFS dataset, "
        "and continuous token embeddings might preserve rare parameters under noisy log streams."
    )
    claims = engine.extract_atomic_claims(raw_text, source_id="SRC-TEST-01", locator="Sec. 3.2")
    assert len(claims) >= 1
    # Check scope extraction
    hdfs_claims = [c for c in claims if c.scope.dataset == "HDFS Log Dataset"]
    assert len(hdfs_claims) >= 1
    # Check qualifier preservation
    qual_claims = [c for c in claims if "might" in c.qualifiers or "might" in c.statement.lower()]
    assert len(qual_claims) >= 1
    assert all(c.is_normalized for c in claims)


def test_gold_02_contradiction_10pt_analysis(test_env):
    """GOLD-02: 10-Point Contradiction Audit distinguishes Dataset Difference from True Contradiction."""
    engine = test_env["engine"]
    claim_a = Claim(
        claim_id="CLM-TEST-01",
        node_code="CH2.SEC1",
        statement="GNN achieves 0.98 F1 on DARPA TC provenance graphs.",
        ownership=IntellectualOwnership.SOURCE,
        claim_type=ClaimType.SOURCE_CLAIM,
    )
    claim_b = Claim(
        claim_id="CLM-TEST-02",
        node_code="CH2.SEC1",
        statement="Simple frequency baseline matches GNN accuracy on LANL dataset.",
        ownership=IntellectualOwnership.SOURCE,
        claim_type=ClaimType.SOURCE_CLAIM,
    )
    res = engine.analyze_contradiction(claim_a, claim_b)
    assert res.contradiction_type == ContradictionType.DATASET_DIFFERENCE
    assert res.checklist_evaluations["same_dataset"] is False
    assert "DARPA TC" in res.diagnosis or "darpa" in res.diagnosis.lower()


def test_gold_03_falsification_negative_control_design(test_env):
    """GOLD-03: Falsification Plan defines negative controls and discriminating tests."""
    engine = test_env["engine"]
    plan = engine.plan_falsification("H3", "Model generalization is not driven by shortcut learning of hostnames.")
    assert plan.target_hypothesis_id == "H3"
    assert len(plan.negative_controls) >= 2
    assert any("CTRL-01" in ctrl or "Identifier masking" in ctrl for ctrl in plan.negative_controls)
    assert len(plan.potential_falsifying_observations) >= 2
    assert len(plan.expected_outcomes_if_true) >= 1
    assert len(plan.expected_outcomes_if_false) >= 1


def test_gold_04_causality_and_graph_guard(test_env):
    """GOLD-04: Enforce DEPENDS_ON != CAUSES and flag causal vocabulary inflation."""
    engine = test_env["engine"]
    # Observational text with causal inflation
    issues = engine.causality_auditor.audit_text_causality(
        entity_id="CLM-INFLATE-01",
        text="Observing suspicious process execution in provenance graph causes unauthorized privilege escalation.",
        is_interventional=False,
    )
    assert len(issues) >= 1
    assert any(iss.issue_type == ReasoningIssueType.CAUSALITY_INFLATION for iss in issues)

    # Provenance Graph Guard
    issues_prov = engine.causality_auditor.audit_text_causality(
        entity_id="CLM-PROV-01",
        text="System provenance audit edges prove the causal effect of file read on network beaconing.",
        is_interventional=False,
    )
    assert any("DEPENDS_ON" in iss.message for iss in issues_prov)


def test_gold_05_argument_bundle_readiness_gate(test_env):
    """GOLD-05: ArgumentBundle Assembly and Readiness Gate lifecycle (DRAFT -> READY)."""
    engine = test_env["engine"]
    repo = test_env["repo"]

    # Incomplete bundle (claims but no evidence)
    bundle_draft = engine.build_argument_bundle(
        roadmap_node="CH1.SEC1",
        objective="Analyze log representation fidelity",
        claims=[{"claim_id": "CLM-01", "statement": "Continuous representations improve fidelity."}],
        evidence=[],
    )
    assert bundle_draft.readiness_state == ArgumentReadinessState.EVIDENCE_INCOMPLETE

    # Blocked bundle (critical leakage issue)
    from research_agent.schemas.reasoning import ReasoningIssue
    bundle_blocked = engine.build_argument_bundle(
        roadmap_node="CH1.SEC1",
        objective="Analyze log representation fidelity",
        claims=[{"claim_id": "CLM-01", "statement": "Continuous representations improve fidelity."}],
        evidence=[{"evidence_id": "EVD-01", "exact_quote": "Empirical F1 0.95"}],
        issues=[
            ReasoningIssue(
                issue_id="ISS-01",
                issue_type=ReasoningIssueType.LEAKAGE_RISK,
                affected_entity_id="EXP-01",
                message="Parser fitted on test split.",
                severity="CRITICAL",
            )
        ],
    )
    assert bundle_blocked.readiness_state == ArgumentReadinessState.BLOCKED

    # Ready bundle
    bundle_ready = engine.build_argument_bundle(
        roadmap_node="CH1.SEC1",
        objective="Analyze log representation fidelity",
        claims=[{"claim_id": "CLM-01", "statement": "Continuous representations improve fidelity."}],
        evidence=[{"evidence_id": "EVD-01", "exact_quote": "Empirical F1 0.95"}],
        issues=[],
    )
    assert bundle_ready.readiness_state == ArgumentReadinessState.READY
    # Ensure saved and retrievable
    retrieved = repo.get_argument_bundle(bundle_ready.bundle_id)
    assert retrieved is not None
    assert retrieved.bundle_id == bundle_ready.bundle_id


# ----------------------------------------------------------------------
# AUDITORS & METHODOLOGICAL INTEGRITY TESTS
# ----------------------------------------------------------------------

def test_leakage_auditor_12pt_checklist(test_env):
    """Verify 12-point evaluation leakage detector."""
    engine = test_env["engine"]
    setup_with_leakage = {
        "parser_fitted_on_test": True,
        "threshold_tuned_on_test": True,
        "host_ids_exposed": True,
    }
    issues = engine.leakage_auditor.audit_leakage("EXP-LEAK-01", setup_with_leakage)
    assert len(issues) == 3
    assert all(iss.issue_type == ReasoningIssueType.LEAKAGE_RISK for iss in issues)
    assert all(iss.severity == "CRITICAL" for iss in issues)


def test_shortcut_auditor(test_env):
    """Verify detection of candidate dataset shortcuts."""
    engine = test_env["engine"]
    feature_desc = "Features include raw executable paths, fixed hostnames, and static template ids."
    issues = engine.shortcut_auditor.audit_shortcuts("FEAT-01", feature_desc)
    assert len(issues) >= 2
    assert any("raw executable paths" in iss.message for iss in issues)
    assert any("fixed hostnames" in iss.message for iss in issues)


def test_security_guards(test_env):
    """Verify security guards: ANOMALY_NOT_ATTACK, UNUSUAL_NOT_MALICIOUS, REPRESENTATION_NOT_DETECTOR."""
    engine = test_env["engine"]

    # Unusual admin tool != Malicious
    issues_admin = engine.security_guards.audit_security_guards(
        "CLM-01", "Execution of PowerShell commands is strictly malicious activity."
    )
    assert any(iss.issue_type == ReasoningIssueType.ATTACK_ANOMALY_CONFLATION for iss in issues_admin)

    # Representation != Detector
    issues_det = engine.security_guards.audit_security_guards(
        "CLM-02", "High end-to-end detector accuracy proves feature representation is superior."
    )
    assert any(iss.issue_type == ReasoningIssueType.REPRESENTATION_DETECTOR_CONFOUND for iss in issues_det)

    # Pseudonymization != Privacy
    issues_priv = engine.security_guards.audit_security_guards(
        "CLM-03", "Applying pseudonymization guarantees privacy-preserving log release."
    )
    assert any(iss.issue_type == ReasoningIssueType.PRIVACY_OVERCLAIM for iss in issues_priv)


def test_anti_harking_and_negative_result_preservation(test_env):
    """Verify failed experiments transition hypotheses to CONTESTED/FALSIFIED without rescue."""
    engine = test_env["engine"]
    hyp = Hypothesis(
        hyp_id="HYP-01",
        code="H1",
        rq_id="RQ1",
        statement="Parameter-aware representation is robust against adversarial template drift.",
        falsification_criteria="F1 drops below 0.20 on shifted templates.",
    )
    # Episode with hypothesis falsification
    episodes = [
        EpisodeRecord(
            episode_id="EPISODE-000001",
            session_id="SESS-001",
            episode_type="EXPERIMENT_RUN",
            title="Ablation Run 1",
            action="Run template drift stress test",
            outcome="F1 dropped to 0.10",
            status="FAILED",
            is_failure=True,
            failure_reason="Empirical outcome directly contradicted hypothesis H1 (accuracy dropped to 0.10 under template drift).",
        )
    ]
    res = engine.hypothesis_evaluator.evaluate_hypothesis(
        hypothesis=hyp,
        episodes=episodes,
        linked_evidence_ids=[],
        contradiction_ids=[],
    )
    assert res.status == EpistemicStatus.FALSIFIED
    assert "falsified" in res.rationale.lower()


def test_assumption_extraction_and_fragility(test_env):
    """Verify implicit domain assumption extraction and classification."""
    engine = test_env["engine"]
    text = "GNN models leverage audit graphs and multiple instance learning across log event streams."
    assumptions = engine.audit_assumptions("NODE-CH2.SEC1", text)
    assert len(assumptions) >= 2
    # Ensure testability is classified
    assert any(a.testability in ["TESTABLE_BY_EXPERIMENT", "TESTABLE_BY_AUDIT", "AXIOMATIC"] for a in assumptions)
    assert all(a.status == "UNTESTED" for a in assumptions)


def test_steelman_counterargument_origin(test_env):
    """Verify steelman counterargument tags origin as OUR_COUNTERARGUMENT."""
    engine = test_env["engine"]
    ctr = engine.build_counterargument("CLM-GRAPH-01", "GNN provenance graph embeddings improve detection F1.")
    assert ctr.is_steelman is True
    assert ctr.origin == "OUR_COUNTERARGUMENT"
    assert len(ctr.response_options) >= 2


def test_contribution_novelty_safety(test_env):
    """Verify candidate contribution differentiation enforces OURS != NOVEL."""
    engine = test_env["engine"]
    from research_agent.schemas.source import Source
    from research_agent.core.enums import SourceQualityTier
    prior_source = Source(
        source_id="SRC-MITRE-01",
        citation_key="MITRE2024ATTCK",
        title="MITRE ATT&CK Framework",
        authors=["MITRE"],
        year=2024,
        venue="MITRE Corp",
        source_type=SourceQualityTier.PRIMARY_STANDARD,
    )
    cand = CandidateContribution(
        contribution_id="CAND-01",
        name="Three-Tier Representation Contract",
        description="Formal preservation contract for log telemetry.",
        roadmap_nodes=["CH1.SEC1"],
        differentiation_notes="Prior work discards parameters during template parsing.",
    )
    state, rep, issues = engine.differentiate_contribution(cand, prior_sources=[prior_source])
    assert state in [NoveltyReasoningState.POTENTIALLY_NOVEL, NoveltyReasoningState.PARTIALLY_NOVEL]
    assert rep["closest_prior_work"] == "MITRE2024ATTCK"
    assert "our_concrete_difference" in rep


# ----------------------------------------------------------------------
# M4 ARGUMENT GRAPH TESTS
# ----------------------------------------------------------------------

def test_argument_graph_dag_and_cycle_detection(test_env):
    """Verify ArgumentGraph detects circular reasoning loops."""
    engine = test_env["engine"]
    nodes = [
        ArgumentNode(node_id="N1", node_type=ArgumentNodeType.CLAIM, title="Claim 1", statement="Stmt 1"),
        ArgumentNode(node_id="N2", node_type=ArgumentNodeType.EVIDENCE, title="Evidence 2", statement="Stmt 2"),
        ArgumentNode(node_id="N3", node_type=ArgumentNodeType.INFERENCE, title="Inference 3", statement="Stmt 3"),
    ]
    # Acyclic graph: N2 -> N3 -> N1
    edges_acyclic = [
        ArgumentEdge(edge_id="E1", source_node_id="N2", target_node_id="N3", relation_type=ArgumentEdgeType.SUPPORTS),
        ArgumentEdge(edge_id="E2", source_node_id="N3", target_node_id="N1", relation_type=ArgumentEdgeType.SUPPORTS),
    ]
    g_acyclic = engine.build_argument_graph(nodes, edges_acyclic)
    assert g_acyclic.is_cyclic is False

    # Cyclic graph: N1 -> N2 -> N3 -> N1
    edges_cyclic = edges_acyclic + [
        ArgumentEdge(edge_id="E3", source_node_id="N1", target_node_id="N2", relation_type=ArgumentEdgeType.SUPPORTS),
    ]
    g_cyclic = engine.build_argument_graph(nodes, edges_cyclic)
    assert g_cyclic.is_cyclic is True

    # Check Mermaid export
    mermaid = engine.argument_graph_engine.to_mermaid(g_acyclic)
    assert "graph TD" in mermaid
    assert "N2 -->|SUPPORTS| N3" in mermaid


# ----------------------------------------------------------------------
# RHETORICAL DISCOURSE PLANNING & TEMPLATE ATTRACTOR AUDIT
# ----------------------------------------------------------------------

def test_rhetorical_discourse_planning_and_attractor_audit(test_env):
    """Verify discourse planner selects patterns and detects template attractors."""
    engine = test_env["engine"]
    p1 = engine.plan_discourse("CH1.SEC1", preferred_pattern=ArgumentPatternType.CLAIM_EVIDENCE_QUALIFICATION)
    p2 = engine.plan_discourse("CH1.SEC2", preferred_pattern=ArgumentPatternType.CLAIM_EVIDENCE_QUALIFICATION)
    p3 = engine.plan_discourse("CH1.SEC3", preferred_pattern=ArgumentPatternType.CLAIM_EVIDENCE_QUALIFICATION)

    assert len(p1.steps) >= 3
    # Audit 3 consecutive identical patterns
    issues = engine.discourse_planner.audit_template_attractors([p1, p2, p3])
    assert len(issues) == 1
    assert issues[0].issue_type == ReasoningIssueType.TEMPLATE_ATTRACTOR_RISK


# ----------------------------------------------------------------------
# RESEARCH SKILLS LIBRARY (18 SKILLS REGISTRATION & EXECUTION)
# ----------------------------------------------------------------------

def test_research_skills_registry_18_skills(test_env):
    """Verify canonical research and verification skills are registered and executable."""
    registry = test_env["registry"]
    engine = test_env["engine"]
    skills = registry.list_skills()
    assert len(skills) >= 18

    # Test executing SKILL-01 (Claim Extraction)
    res01 = registry.run_skill("SKILL-01", {"text": "Sysflow records host audit events."}, engine)
    assert res01.success is True
    assert "atomic_claims" in res01.data

    # Test executing SKILL-06 (Alternative Explanations)
    res06 = registry.run_skill("SKILL-06", {"claim_id": "CLM-01", "claim_statement": "Deep model outperforms baseline."}, engine)
    assert res06.success is True
    assert len(res06.data["alternatives"]) == 8

    # Test executing SKILL-07 (Falsification Planning)
    res07 = registry.run_skill("SKILL-07", {"hypothesis_id": "H2", "hypothesis_statement": "Cross-view alignment prevents representation collapse."}, engine)
    assert res07.success is True
    assert "falsification_plan" in res07.data

    # Test executing SKILL-17 (Discourse Planning)
    res17 = registry.run_skill("SKILL-17", {"roadmap_node": "CH2.SEC3"}, engine)
    assert res17.success is True
    assert "discourse_plan" in res17.data


# ----------------------------------------------------------------------
# PROMPT 6 VERIFICATION REQUEST INTERFACE
# ----------------------------------------------------------------------

def test_prompt_6_verification_request_interface(test_env):
    """Verify formal VerificationRequest generation for Prompt 6 hand-off."""
    engine = test_env["engine"]
    repo = test_env["repo"]

    req = engine.create_verification_request(
        request_type=VerificationRequestType.EQUATION_VERIFY,
        description="Verify dimensional invariance of representation projection operator f_theta.",
        input_payload={"equation_id": "EQ-000001", "latex": "z_t = f_\\theta(L_{1:t})", "expected_dimension": 128},
        target_claim_id="CLM-000001",
    )
    assert req.status == VerificationRequestStatus.PENDING
    assert req.request_id.startswith("VRQ-")

    # Retrieve from repository
    retrieved = repo.get_verification_request(req.request_id)
    assert retrieved is not None
    assert retrieved.request_type == VerificationRequestType.EQUATION_VERIFY
    assert retrieved.input_payload["expected_dimension"] == 128

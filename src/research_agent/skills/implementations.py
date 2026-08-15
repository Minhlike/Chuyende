"""
Executable Implementations of the 18 Canonical Research Skills (Prompt 5 Sections 75..92)
"""

import time
from typing import Dict, Any, List, Optional
from research_agent.skills.base import BaseResearchSkill, SkillMetadata, SkillResult
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    ReasoningMode,
    VerificationRequestType,
)
from research_agent.schemas.claim import Claim
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.ownership import CandidateContribution


class Skill01ClaimExtraction(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-01",
            name="claim_extraction_and_normalization",
            category="REASONING_FOUNDATION",
            description="Decomposes unstructured scientific text into atomic normalized propositional claims with scope bounds.",
            inputs=["text", "source_id", "locator"],
            outputs=["atomic_claims"],
            preconditions=["Text must be non-empty and UTF-8 encoded."],
            invariants=["Original wording preserved; qualifiers retained; proposition normalized."],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        text = payload.get("text", "")
        source_id = payload.get("source_id")
        locator = payload.get("locator")
        claims = engine.extract_atomic_claims(text, source_id=source_id, locator=locator)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"atomic_claims": [c.model_dump(mode="json") for c in claims]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill02EvidenceAlignment(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-02",
            name="evidence_alignment_and_gap_detection",
            category="EVIDENCE_EVALUATION",
            description="Evaluates semantic entailment, dataset compatibility, and flags open empirical evidence gaps.",
            inputs=["claim", "evidences"],
            outputs=["alignments", "evidence_gap"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        claim_data = payload.get("claim", {})
        evidences_data = payload.get("evidences", [])
        claim = Claim.model_validate(claim_data) if isinstance(claim_data, dict) else claim_data
        evidences = [Evidence.model_validate(e) if isinstance(e, dict) else e for e in evidences_data]

        alignments = [engine.align_evidence(e, claim) for e in evidences]
        gap = engine.detect_evidence_gap(claim, evidences)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "alignments": [{"status": a[0].value, "rationale": a[1]} for a in alignments],
                "evidence_gap": gap.model_dump(mode="json") if gap else None,
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill03StructuredSynthesis(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-03",
            name="structured_literature_synthesis",
            category="SYNTHESIS",
            description="Organizes literature by issue and mechanism, clustering agreements, disagreements, and research implications.",
            inputs=["topic", "claims", "sources", "roadmap_node"],
            outputs=["structured_synthesis"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        topic = payload.get("topic", "General Topic")
        claims_data = payload.get("claims", [])
        sources_data = payload.get("sources", [])
        node = payload.get("roadmap_node")
        claims = [Claim.model_validate(c) if isinstance(c, dict) else c for c in claims_data]
        sources = [engine.repo.get_source(s_id) for s_id in sources_data if engine.repo.get_source(s_id)]
        synth = engine.synthesize_literature(topic=topic, claims=claims, sources=sources, roadmap_node=node)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"structured_synthesis": synth.model_dump(mode="json")},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill04ContradictionAnalysis(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-04",
            name="contradiction_analysis_10pt",
            category="DIALECTIC",
            description="Evaluates apparent contradictions across 10 methodological dimensions to identify root cause.",
            inputs=["claim_a", "claim_b", "notes"],
            outputs=["contradiction_type", "checklist", "diagnosis", "resolution_strategy"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        ca = Claim.model_validate(payload["claim_a"]) if isinstance(payload["claim_a"], dict) else payload["claim_a"]
        cb = Claim.model_validate(payload["claim_b"]) if isinstance(payload["claim_b"], dict) else payload["claim_b"]
        res = engine.analyze_contradiction(ca, cb, payload.get("notes"))
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "contradiction_type": res.contradiction_type.value,
                "checklist": res.checklist_evaluations,
                "diagnosis": res.diagnosis,
                "resolution_strategy": res.resolution_strategy,
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill05AssumptionAudit(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-05",
            name="implicit_explicit_assumption_audit",
            category="METHODOLOGY",
            description="Identifies hidden assumptions and measures testability and downstream failure consequences.",
            inputs=["entity_id", "text"],
            outputs=["assumptions"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        entity_id = payload.get("entity_id", "ENTITY-001")
        text = payload.get("text", "")
        ass = engine.audit_assumptions(entity_id, text)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"assumptions": [a.model_dump(mode="json") for a in ass]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill06AlternativeExplanations(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-06",
            name="alternative_explanations_confounders",
            category="METHODOLOGY",
            description="Generates 8 standard methodological confounders and links each to negative controls.",
            inputs=["claim_id", "claim_statement"],
            outputs=["alternatives"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        cid = payload.get("claim_id", "CLM-001")
        stmt = payload.get("claim_statement", "")
        alts = engine.generate_alternatives(cid, stmt)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"alternatives": [a.model_dump(mode="json") for a in alts]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill07FalsificationPlanning(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-07",
            name="falsification_negative_control_design",
            category="EXPERIMENT_DESIGN",
            description="Designs empirical falsification protocols, negative controls, and discriminating experiments.",
            inputs=["hypothesis_id", "hypothesis_statement"],
            outputs=["falsification_plan"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        hid = payload.get("hypothesis_id", "H1")
        stmt = payload.get("hypothesis_statement", "")
        plan = engine.plan_falsification(hid, stmt)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"falsification_plan": plan.model_dump(mode="json")},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill08CounterargumentGeneration(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-08",
            name="steelman_counterargument_generation",
            category="DIALECTIC",
            description="Constructs the strongest plausible objection against an inference and tags origin as OUR_COUNTERARGUMENT.",
            inputs=["claim_id", "claim_statement"],
            outputs=["counterargument"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        cid = payload.get("claim_id", "CLM-001")
        stmt = payload.get("claim_statement", "")
        ctr = engine.build_counterargument(cid, stmt)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"counterargument": ctr.model_dump(mode="json")},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill09StructuredInference(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-09",
            name="structured_research_inference",
            category="INFERENCE",
            description="Builds justified research inference and enforces scope containment (conclusion_scope subset justified_scope).",
            inputs=["premises", "evidence_ids", "assumption_ids", "conclusion", "reasoning_type"],
            outputs=["inference", "issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        inf, issues = engine.construct_inference(
            premises=payload.get("premises", []),
            evidence_ids=payload.get("evidence_ids", []),
            assumption_ids=payload.get("assumption_ids", []),
            candidate_conclusion=payload.get("conclusion", ""),
            reasoning_type=ReasoningMode(payload.get("reasoning_type", "INDUCTIVE")),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "inference": inf.model_dump(mode="json"),
                "issues": [iss.model_dump(mode="json") for iss in issues],
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill10CausalityGuard(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-10",
            name="causality_and_graph_inflation_guard",
            category="AUDIT",
            description="Audits claims for causal vocabulary inflation and enforces DEPENDS_ON != CAUSES in audit graphs.",
            inputs=["entity_id", "text", "is_interventional"],
            outputs=["issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        issues = engine.causality_auditor.audit_text_causality(
            entity_id=payload.get("entity_id", "ENT-01"),
            text=payload.get("text", ""),
            is_interventional=payload.get("is_interventional", False),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"issues": [iss.model_dump(mode="json") for iss in issues]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill11LeakageAudit(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-11",
            name="data_and_evaluation_leakage_audit",
            category="AUDIT",
            description="Executes 12-point leakage checklist across pretraining, normalization, and test partition exposure.",
            inputs=["entity_id", "setup_dict"],
            outputs=["issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        issues = engine.leakage_auditor.audit_leakage(
            entity_id=payload.get("entity_id", "EXP-01"),
            experimental_setup=payload.get("setup_dict", {}),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"issues": [iss.model_dump(mode="json") for iss in issues]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill12ShortcutAudit(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-12",
            name="dataset_shortcut_learning_audit",
            category="AUDIT",
            description="Detects superficial dataset shortcuts (hostnames, usernames, campaign IDs, template IDs).",
            inputs=["entity_id", "feature_description"],
            outputs=["issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        issues = engine.shortcut_auditor.audit_shortcuts(
            entity_id=payload.get("entity_id", "FEAT-01"),
            feature_description=payload.get("feature_description", ""),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"issues": [iss.model_dump(mode="json") for iss in issues]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill13ValidityAudit(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-13",
            name="experimental_validity_4factor_audit",
            category="AUDIT",
            description="Audits Construct, Internal, External, and Statistical validity factors.",
            inputs=["entity_id", "setup_info"],
            outputs=["issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        issues = engine.validity_auditor.audit_validity(
            entity_id=payload.get("entity_id", "EXP-01"),
            setup_info=payload.get("setup_info", {}),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"issues": [iss.model_dump(mode="json") for iss in issues]},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill14HypothesisEvaluation(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-14",
            name="hypothesis_and_rq_epistemic_evaluation",
            category="EVALUATION",
            description="Computes EpistemicStatus for hypotheses and RQStatus without post-hoc hypothesis rescue.",
            inputs=["hypothesis_code", "evidence_ids", "contradiction_ids"],
            outputs=["evaluation_result"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        h_code = payload.get("hypothesis_code", "H1")
        hyp = engine.repo.get_hypothesis(h_code)
        if not hyp:
            return SkillResult(skill_id=self.metadata.skill_id, success=False, issues=[f"Hypothesis {h_code} not found."])
        res = engine.evaluate_hypothesis(
            hypothesis=hyp,
            linked_evidence_ids=payload.get("evidence_ids", []),
            contradiction_ids=payload.get("contradiction_ids", []),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "hyp_id": res.hyp_id,
                "status": res.status.value,
                "limitations": res.limitations,
                "rationale": res.rationale,
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill15ContributionDifferentiation(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-15",
            name="contribution_novelty_differentiation",
            category="NOVELTY",
            description="Differentiates candidate contributions from closest prior art and enforces OURS != NOVEL.",
            inputs=["candidate_id"],
            outputs=["novelty_state", "differentiation_report", "issues"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        cid = payload.get("candidate_id", "CAND-01")
        cand = engine.repo.get_candidate_contribution(cid)
        if not cand:
            return SkillResult(skill_id=self.metadata.skill_id, success=False, issues=[f"Candidate contribution {cid} not found."])
        state, rep, issues = engine.differentiate_contribution(cand)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "novelty_state": state.value,
                "differentiation_report": rep,
                "issues": [iss.model_dump(mode="json") for iss in issues],
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill16ArgumentGraphConstruction(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-16",
            name="m4_argument_graph_construction",
            category="ARGUMENTATION",
            description="Constructs M4 Argument Graph, verifies absence of circular support, and exports Mermaid/DOT/JSON.",
            inputs=["nodes", "edges", "graph_id", "roadmap_node"],
            outputs=["graph", "mermaid", "dot"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        nodes_data = payload.get("nodes", [])
        edges_data = payload.get("edges", [])
        gid = payload.get("graph_id", "ARG_GRAPH_01")
        node_code = payload.get("roadmap_node")
        from research_agent.schemas.reasoning import ArgumentNode, ArgumentEdge
        nodes = [ArgumentNode.model_validate(n) if isinstance(n, dict) else n for n in nodes_data]
        edges = [ArgumentEdge.model_validate(e) if isinstance(e, dict) else e for e in edges_data]
        graph = engine.build_argument_graph(nodes, edges, gid, node_code)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "graph": graph.model_dump(mode="json"),
                "mermaid": engine.argument_graph_engine.to_mermaid(graph),
                "dot": engine.argument_graph_engine.to_dot(graph),
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill17RhetoricalDiscoursePlanning(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-17",
            name="rhetorical_discourse_planning",
            category="DISCOURSE",
            description="Generates non-rigid rhetorical discourse sequence plans matching 10 diverse argument patterns.",
            inputs=["roadmap_node", "preferred_pattern"],
            outputs=["discourse_plan"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        node = payload.get("roadmap_node", "CH1.SEC1")
        pat = payload.get("preferred_pattern")
        plan = engine.plan_discourse(node, pat)
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={"discourse_plan": plan.model_dump(mode="json")},
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )


class Skill18ArgumentBundlePackaging(BaseResearchSkill):
    def __init__(self):
        super().__init__(SkillMetadata(
            skill_id="SKILL-18",
            name="argument_bundle_packaging_and_readiness_gate",
            category="PACKAGING",
            description="Packages full ArgumentBundle and executes readiness gate (DRAFT -> READY).",
            inputs=["roadmap_node", "objective", "claims", "evidence", "assumptions", "counterarguments"],
            outputs=["argument_bundle", "readiness_state"],
        ))

    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        t0 = time.perf_counter()
        bundle = engine.build_argument_bundle(
            roadmap_node=payload.get("roadmap_node", "CH1.SEC1"),
            objective=payload.get("objective", "Objective"),
            claims=payload.get("claims", []),
            evidence=payload.get("evidence", []),
            contradicting_evidence=payload.get("contradicting_evidence", []),
            assumptions=payload.get("assumptions", []),
            counterarguments=payload.get("counterarguments", []),
            candidate_inferences=payload.get("candidate_inferences", []),
            falsification_plans=payload.get("falsification_plans", []),
            ownership_summary=payload.get("ownership_summary", {}),
            open_questions=payload.get("open_questions", []),
            issues=payload.get("issues", []),
            verification_requests=payload.get("verification_requests", []),
        )
        return SkillResult(
            skill_id=self.metadata.skill_id,
            success=True,
            data={
                "argument_bundle": bundle.model_dump(mode="json"),
                "readiness_state": bundle.readiness_state.value,
            },
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )

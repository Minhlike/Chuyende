"""
Unified Scientific Reasoning & Argumentation Engine (Prompt 5)
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.manager import MemoryManager
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    ReasoningMode,
    EvidenceAlignmentStatus,
    ContradictionType,
    ArgumentReadinessState,
    ReasoningIssueType,
    DiscourseFunction,
    ArgumentNodeType,
    ArgumentEdgeType,
    RQStatus,
    NoveltyReasoningState,
    VerificationRequestType,
    VerificationRequestStatus,
    ResearchPriorityLevel,
    ArgumentPatternType,
)
from research_agent.schemas.claim import Claim
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.source import Source
from research_agent.schemas.roadmap import Hypothesis, ResearchQuestion
from research_agent.schemas.ownership import CandidateContribution
from research_agent.schemas.reasoning import (
    ClaimScope,
    AtomicClaimCandidate,
    EvidenceGap,
    AssumptionRecord,
    AlternativeExplanation,
    CounterargumentRecord,
    FalsificationPlan,
    InferenceRecord,
    CompetingHypothesis,
    ReasoningIssue,
    ArgumentNode,
    ArgumentEdge,
    ArgumentGraph,
    DiscoursePlan,
    StructuredSynthesis,
    VerificationRequest,
    ResearchActionPriority,
    ArgumentBundle,
)

from research_agent.reasoning.claim_extractor import ClaimExtractor
from research_agent.reasoning.evidence_alignment import EvidenceAlignmentEngine
from research_agent.reasoning.synthesis import LiteratureSynthesisEngine
from research_agent.reasoning.contradiction import ContradictionAnalyzer, ContradictionAnalysisResult
from research_agent.reasoning.assumptions import AssumptionAuditor
from research_agent.reasoning.alternatives import AlternativeExplanationsEngine
from research_agent.reasoning.counterarguments import CounterargumentBuilder
from research_agent.reasoning.falsification import FalsificationPlanner
from research_agent.reasoning.inference import InferenceEngine
from research_agent.reasoning.causality import CausalityAuditor
from research_agent.reasoning.auditors import (
    LeakageAuditor,
    ShortcutAuditor,
    ValidityAuditor,
    SecurityGuards,
    BaselineFairnessAuditor,
)
from research_agent.reasoning.hypothesis_evaluator import HypothesisEvaluator, HypothesisEvaluationResult
from research_agent.reasoning.contributions import ContributionDifferentiator
from research_agent.reasoning.argument_graph import ArgumentGraphEngine
from research_agent.reasoning.discourse import DiscoursePlanner
from research_agent.reasoning.priorities import ResearchActionPrioritizer
from research_agent.reasoning.bundle_builder import ArgumentBundleBuilder


class ScientificReasoningEngine:
    """
    Unified entry point and coordinator for scientific reasoning, methodological auditing,
    argument graph assembly, and verification request generation.
    """

    def __init__(
        self,
        repo: Optional[ResearchRepository] = None,
        memory_mgr: Optional[MemoryManager] = None,
    ):
        self.repo = repo or ResearchRepository()
        self.memory_mgr = memory_mgr or MemoryManager(self.repo)

        # Core Engines
        self.claim_extractor = ClaimExtractor()
        self.evidence_aligner = EvidenceAlignmentEngine()
        self.synthesis_engine = LiteratureSynthesisEngine()
        self.contradiction_analyzer = ContradictionAnalyzer()
        self.assumption_auditor = AssumptionAuditor()
        self.alternatives_engine = AlternativeExplanationsEngine()
        self.counterargument_builder = CounterargumentBuilder()
        self.falsification_planner = FalsificationPlanner()
        self.inference_engine = InferenceEngine()
        self.causality_auditor = CausalityAuditor()
        
        # Auditors
        self.leakage_auditor = LeakageAuditor()
        self.shortcut_auditor = ShortcutAuditor()
        self.validity_auditor = ValidityAuditor()
        self.security_guards = SecurityGuards()
        self.fairness_auditor = BaselineFairnessAuditor()
        
        # Evaluators & Bundlers
        self.hypothesis_evaluator = HypothesisEvaluator()
        self.contribution_differentiator = ContributionDifferentiator()
        self.argument_graph_engine = ArgumentGraphEngine()
        self.discourse_planner = DiscoursePlanner()
        self.prioritizer = ResearchActionPrioritizer()
        self.bundle_builder = ArgumentBundleBuilder()

    # -------------------------------------------------------------
    # High-Level Reasoning Workflows
    # -------------------------------------------------------------
    def extract_atomic_claims(
        self,
        text: str,
        source_id: Optional[str] = None,
        locator: Optional[str] = None,
        claim_type: ClaimType = ClaimType.SOURCE_CLAIM,
        ownership: IntellectualOwnership = IntellectualOwnership.SOURCE,
    ) -> List[AtomicClaimCandidate]:
        return self.claim_extractor.extract_atomic_claims(
            text=text,
            source_id=source_id,
            locator=locator,
            claim_type=claim_type,
            ownership=ownership,
        )

    def align_evidence(self, evidence: Evidence, claim: Claim) -> Tuple[EvidenceAlignmentStatus, str]:
        return self.evidence_aligner.align(evidence, claim)

    def detect_evidence_gap(self, claim: Claim, evidences: List[Evidence], node_code: Optional[str] = None) -> Optional[EvidenceGap]:
        gap = self.evidence_aligner.detect_gap(claim, evidences, node_code)
        if gap:
            self.repo.save_evidence_gap(gap)
        return gap

    def synthesize_literature(
        self,
        topic: str,
        claims: List[Claim],
        sources: List[Source],
        roadmap_node: Optional[str] = None,
    ) -> StructuredSynthesis:
        return self.synthesis_engine.synthesize(
            topic=topic,
            claims=claims,
            sources=sources,
            roadmap_node=roadmap_node,
        )

    def analyze_contradiction(
        self,
        claim_a: Claim,
        claim_b: Claim,
        context_notes: Optional[str] = None,
    ) -> ContradictionAnalysisResult:
        return self.contradiction_analyzer.analyze(claim_a, claim_b, context_notes)

    def audit_assumptions(self, entity_id: str, text: str) -> List[AssumptionRecord]:
        assumptions = self.assumption_auditor.audit_assumptions(entity_id, text)
        for a in assumptions:
            self.repo.save_assumption(a)
        return assumptions

    def generate_alternatives(self, claim_id: str, claim_statement: str) -> List[AlternativeExplanation]:
        return self.alternatives_engine.generate_alternatives(claim_id, claim_statement)

    def build_counterargument(self, claim_id: str, claim_statement: str) -> CounterargumentRecord:
        return self.counterargument_builder.build_counterargument(claim_id, claim_statement)

    def plan_falsification(self, hypothesis_id: str, hypothesis_statement: str) -> FalsificationPlan:
        return self.falsification_planner.plan_falsification(hypothesis_id, hypothesis_statement)

    def construct_inference(
        self,
        premises: List[str],
        evidence_ids: List[str],
        assumption_ids: List[str],
        candidate_conclusion: str,
        reasoning_type: ReasoningMode = ReasoningMode.INDUCTIVE,
        justified_scope: Optional[ClaimScope] = None,
    ) -> Tuple[InferenceRecord, List[ReasoningIssue]]:
        inf, issues = self.inference_engine.construct_inference(
            premises=premises,
            evidence_ids=evidence_ids,
            assumption_ids=assumption_ids,
            candidate_conclusion=candidate_conclusion,
            reasoning_type=reasoning_type,
            justified_scope=justified_scope,
        )
        for iss in issues:
            self.repo.save_reasoning_issue(iss)
        return inf, issues

    def audit_methodology(
        self,
        entity_id: str,
        statement_or_setup: str,
        experimental_setup: Optional[Dict[str, Any]] = None,
    ) -> List[ReasoningIssue]:
        """
        Executes complete methodological check across causality, security guards, leakage, and shortcuts.
        """
        issues: List[ReasoningIssue] = []
        issues.extend(self.causality_auditor.audit_text_causality(entity_id, statement_or_setup))
        issues.extend(self.security_guards.audit_security_guards(entity_id, statement_or_setup))
        issues.extend(self.shortcut_auditor.audit_shortcuts(entity_id, statement_or_setup))
        if experimental_setup:
            issues.extend(self.leakage_auditor.audit_leakage(entity_id, experimental_setup))
            issues.extend(self.validity_auditor.audit_validity(entity_id, experimental_setup))

        for iss in issues:
            self.repo.save_reasoning_issue(iss)
        return issues

    def evaluate_hypothesis(
        self,
        hypothesis: Hypothesis,
        linked_evidence_ids: Optional[List[str]] = None,
        contradiction_ids: Optional[List[str]] = None,
    ) -> HypothesisEvaluationResult:
        episodes = self.repo.list_episodes()
        return self.hypothesis_evaluator.evaluate_hypothesis(
            hypothesis=hypothesis,
            episodes=episodes,
            linked_evidence_ids=linked_evidence_ids or [],
            contradiction_ids=contradiction_ids or [],
        )

    def differentiate_contribution(
        self,
        contribution: CandidateContribution,
        prior_sources: Optional[List[Source]] = None,
    ) -> Tuple[NoveltyReasoningState, Dict[str, Any], List[ReasoningIssue]]:
        sources = prior_sources or self.repo.list_sources()
        return self.contribution_differentiator.differentiate(contribution, sources)

    def build_argument_graph(
        self,
        nodes: List[ArgumentNode],
        edges: List[ArgumentEdge],
        graph_id: str = "MAIN_ARGUMENT_GRAPH",
        roadmap_node: Optional[str] = None,
    ) -> ArgumentGraph:
        for n in nodes:
            self.repo.save_argument_node(n)
        for e in edges:
            self.repo.save_argument_edge(e)
        return self.argument_graph_engine.build_graph(nodes, edges, graph_id, roadmap_node)

    def plan_discourse(
        self,
        roadmap_node: str,
        preferred_pattern: Optional[ArgumentPatternType] = None,
    ) -> DiscoursePlan:
        return self.discourse_planner.plan_discourse(roadmap_node, preferred_pattern)

    def prioritize_research_actions(self) -> List[ResearchActionPriority]:
        gaps = self.repo.list_evidence_gaps(status="OPEN")
        assumptions = self.repo.list_assumptions()
        verifs = self.repo.list_verification_requests(status=VerificationRequestStatus.PENDING)
        
        # Check contested hypotheses
        hyps = self.repo.list_hypotheses()
        contested = []
        for h in hyps:
            res = self.evaluate_hypothesis(h)
            if res.status == EpistemicStatus.CONTESTED:
                contested.append(h.code)

        return self.prioritizer.prioritize_actions(
            gaps=gaps,
            assumptions=assumptions,
            verification_requests=verifs,
            contested_hypotheses=contested,
        )

    def create_verification_request(
        self,
        request_type: VerificationRequestType,
        description: str,
        input_payload: Dict[str, Any],
        target_claim_id: Optional[str] = None,
        target_equation_id: Optional[str] = None,
        target_table_or_figure_id: Optional[str] = None,
    ) -> VerificationRequest:
        """
        Creates and stores a formal VerificationRequest for the Prompt 6 toolchain.
        """
        seq = abs(hash(str(request_type) + description)) % 1000000
        req = VerificationRequest(
            request_id=f"VRQ-{seq:06d}",
            request_type=request_type,
            target_claim_id=target_claim_id,
            target_equation_id=target_equation_id,
            target_table_or_figure_id=target_table_or_figure_id,
            description=description,
            input_payload=input_payload,
            status=VerificationRequestStatus.PENDING,
            requested_at=datetime.now(timezone.utc),
        )
        return self.repo.save_verification_request(req)

    def build_argument_bundle(
        self,
        roadmap_node: str,
        objective: str,
        research_questions: Optional[List[str]] = None,
        hypotheses: Optional[List[str]] = None,
        claims: Optional[List[Dict[str, Any]]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        contradicting_evidence: Optional[List[Dict[str, Any]]] = None,
        assumptions: Optional[List[AssumptionRecord]] = None,
        counterarguments: Optional[List[CounterargumentRecord]] = None,
        candidate_inferences: Optional[List[InferenceRecord]] = None,
        falsification_plans: Optional[List[FalsificationPlan]] = None,
        ownership_summary: Optional[Dict[str, str]] = None,
        open_questions: Optional[List[str]] = None,
        discourse_plan: Optional[DiscoursePlan] = None,
        issues: Optional[List[ReasoningIssue]] = None,
        verification_requests: Optional[List[VerificationRequest]] = None,
    ) -> ArgumentBundle:
        """
        Builds, audits, and persists an ArgumentBundle.
        """
        bundle = self.bundle_builder.build_bundle(
            roadmap_node=roadmap_node,
            objective=objective,
            research_questions=research_questions or [],
            hypotheses=hypotheses or [],
            claims=claims or [],
            evidence=evidence or [],
            contradicting_evidence=contradicting_evidence or [],
            assumptions=assumptions or [],
            counterarguments=counterarguments or [],
            candidate_inferences=candidate_inferences or [],
            falsification_plans=falsification_plans or [],
            ownership_summary=ownership_summary or {},
            open_questions=open_questions or [],
            discourse_plan=discourse_plan,
            issues=issues or [],
            verification_requests=verification_requests or [],
        )
        return self.repo.save_argument_bundle(bundle)

    def execute_verification_request(self, request_or_id: Any) -> Any:
        """
        Executes a VerificationRequest through the ScientificVerificationPipeline.
        """
        from research_agent.verification.pipeline import ScientificVerificationPipeline
        pipeline = ScientificVerificationPipeline(self.repo)

        if isinstance(request_or_id, str):
            req = self.repo.get_verification_request(request_or_id)
            if not req:
                raise ValueError(f"VerificationRequest '{request_or_id}' not found.")
        else:
            req = request_or_id

        return pipeline.execute_request(req)


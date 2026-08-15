"""
Skills Registry & Execution Manager (Prompt 5 Sections 75..92)
"""

from typing import Dict, Any, List, Optional
from research_agent.skills.base import BaseResearchSkill, SkillMetadata, SkillResult
from research_agent.skills.implementations import (
    Skill01ClaimExtraction,
    Skill02EvidenceAlignment,
    Skill03StructuredSynthesis,
    Skill04ContradictionAnalysis,
    Skill05AssumptionAudit,
    Skill06AlternativeExplanations,
    Skill07FalsificationPlanning,
    Skill08CounterargumentGeneration,
    Skill09StructuredInference,
    Skill10CausalityGuard,
    Skill11LeakageAudit,
    Skill12ShortcutAudit,
    Skill13ValidityAudit,
    Skill14HypothesisEvaluation,
    Skill15ContributionDifferentiation,
    Skill16ArgumentGraphConstruction,
    Skill17RhetoricalDiscoursePlanning,
    Skill18ArgumentBundlePackaging,
    Skill19SymbolicEquationVerification,
    Skill20DatasetValidationAndProfiling,
    Skill21DeterministicMetricRecomputation,
    Skill22HypothesisTestingAndEffectSize,
    Skill23MultiSeedAggregation,
    Skill24ScientificTableConstruction,
    Skill25ScientificFigureGeneration,
    Skill26ReproducibilityVerification,
    Skill27AcademicSectionPlanner,
    Skill28LiteratureSynthesisWriter,
    Skill29MethodologyWriter,
    Skill30ExperimentProtocolWriter,
    Skill31ResultsWriter,
    Skill32DiscussionWriter,
    Skill33LimitationWriter,
    Skill34ContributionWriter,
    Skill35AbstractBuilder,
    Skill36ConclusionBuilder,
    Skill37CitationAuditor,
    Skill38ThesisAuditor,
)


class ResearchSkillRegistry:
    """
    Central registry and execution manager for canonical research skills.
    """

    def __init__(self):
        self._skills: Dict[str, BaseResearchSkill] = {}
        self._register_default_skills()

    def _register_default_skills(self):
        skills = [
            Skill01ClaimExtraction(),
            Skill02EvidenceAlignment(),
            Skill03StructuredSynthesis(),
            Skill04ContradictionAnalysis(),
            Skill05AssumptionAudit(),
            Skill06AlternativeExplanations(),
            Skill07FalsificationPlanning(),
            Skill08CounterargumentGeneration(),
            Skill09StructuredInference(),
            Skill10CausalityGuard(),
            Skill11LeakageAudit(),
            Skill12ShortcutAudit(),
            Skill13ValidityAudit(),
            Skill14HypothesisEvaluation(),
            Skill15ContributionDifferentiation(),
            Skill16ArgumentGraphConstruction(),
            Skill17RhetoricalDiscoursePlanning(),
            Skill18ArgumentBundlePackaging(),
            Skill19SymbolicEquationVerification(),
            Skill20DatasetValidationAndProfiling(),
            Skill21DeterministicMetricRecomputation(),
            Skill22HypothesisTestingAndEffectSize(),
            Skill23MultiSeedAggregation(),
            Skill24ScientificTableConstruction(),
            Skill25ScientificFigureGeneration(),
            Skill26ReproducibilityVerification(),
            Skill27AcademicSectionPlanner(),
            Skill28LiteratureSynthesisWriter(),
            Skill29MethodologyWriter(),
            Skill30ExperimentProtocolWriter(),
            Skill31ResultsWriter(),
            Skill32DiscussionWriter(),
            Skill33LimitationWriter(),
            Skill34ContributionWriter(),
            Skill35AbstractBuilder(),
            Skill36ConclusionBuilder(),
            Skill37CitationAuditor(),
            Skill38ThesisAuditor(),
        ]
        for s in skills:
            self._skills[s.metadata.skill_id] = s
            # Also register by canonical name
            self._skills[s.metadata.name] = s

    def get_skill(self, skill_id_or_name: str) -> Optional[BaseResearchSkill]:
        return self._skills.get(skill_id_or_name)

    def list_skills(self) -> List[SkillMetadata]:
        # Return unique skills ordered by SKILL-01..SKILL-18
        unique = {s.metadata.skill_id: s.metadata for s in self._skills.values()}
        return [unique[k] for k in sorted(unique.keys())]

    def run_skill(self, skill_id_or_name: str, payload: Dict[str, Any], engine: Any) -> SkillResult:
        skill = self.get_skill(skill_id_or_name)
        if not skill:
            return SkillResult(
                skill_id=skill_id_or_name,
                success=False,
                issues=[f"Skill '{skill_id_or_name}' not found in registry."],
            )
        return skill.execute(payload, engine)

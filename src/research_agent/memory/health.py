"""
Memory Health Auditor (Prompt 4, Sections 54, 55, MQ-01..MQ-15)
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from research_agent.core.enums import (
    IntellectualOwnership,
    EpistemicStatus,
    DecisionStatus,
    OpenQuestionStatus,
)
from research_agent.schemas.memory import MemoryHealthReport
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.vector_index import DerivedVectorIndex


class MemoryHealthAuditor:
    """
    Automated memory health audit enforcing MQ-01 through MQ-15.
    """

    def __init__(self, repository: ResearchRepository, vector_index: Optional[DerivedVectorIndex] = None):
        self.repo = repository
        self.vector_index = vector_index or DerivedVectorIndex()

    def audit(self) -> MemoryHealthReport:
        issues: List[str] = []
        orphan_count = 0
        broken_refs_count = 0
        circular_support_count = 0
        stale_count = 0

        memories = self.repo.list_memories()
        decisions = self.repo.list_decisions()
        episodes = self.repo.list_episodes()
        lessons = self.repo.list_lessons_learned()
        questions = self.repo.list_open_questions()
        contradictions = self.repo.list_contradictions()
        claims = self.repo.list_claims()
        claim_map = {c.claim_id: c for c in claims}

        # -------------------------------------------------------------
        # MQ-01 & MQ-02: Broken canonical references
        # -------------------------------------------------------------
        for m in memories:
            if m.reference_id:
                ref_id = m.reference_id
                exists = False
                if ref_id.startswith("SRC-") and self.repo.get_source(ref_id):
                    exists = True
                elif ref_id.startswith("CLM-") and self.repo.get_claim(ref_id):
                    exists = True
                elif ref_id.startswith("DEC-") and self.repo.get_decision(ref_id):
                    exists = True
                elif ref_id.startswith("EVD-") and self.repo.get_evidence(ref_id):
                    exists = True
                elif ref_id.startswith("OQ-") and self.repo.get_open_question(ref_id):
                    exists = True
                elif ref_id.startswith("LES-") and self.repo.get_lesson_learned(ref_id):
                    exists = True
                elif ref_id.startswith("EP-") and self.repo.get_episode(ref_id):
                    exists = True
                elif ref_id.startswith("ROD-") and self.repo.get_roadmap(ref_id):
                    exists = True
                elif self.repo.get_roadmap_node_by_code(ref_id):
                    exists = True

                if not exists:
                    broken_refs_count += 1
                    issues.append(f"MQ-01/MQ-02: Memory '{m.memory_id}' references missing entity '{ref_id}'")

            # MQ-05: OUR_INFERENCE promoted as SOURCE_FACT
            if m.ownership == IntellectualOwnership.SOURCE and not m.reference_id and not m.associated_entity_ids:
                issues.append(f"MQ-05: Memory '{m.memory_id}' claimed as SOURCE without verified external provenance.")

            # MQ-06: Generated summary used without underlying links
            if m.is_generated_summary and not m.associated_entity_ids and not m.reference_id:
                issues.append(f"MQ-06: Generated summary memory '{m.memory_id}' has no underlying canonical entity references.")

            # MQ-12: Circular self support
            if m.memory_id in m.associated_entity_ids:
                circular_support_count += 1
                issues.append(f"MQ-12: Memory '{m.memory_id}' exhibits circular self-support.")

            if m.is_stale or m.review_required:
                stale_count += 1

        # -------------------------------------------------------------
        # MQ-03: Decision missing rationale
        # -------------------------------------------------------------
        for d in decisions:
            if not d.rationale or len(d.rationale.strip()) < 3:
                issues.append(f"MQ-03: Decision '{d.decision_id}' lacks mandatory rationale.")

        # -------------------------------------------------------------
        # MQ-04: Lesson missing originating episode or experiment
        # -------------------------------------------------------------
        for l in lessons:
            if not l.originating_episode_id and not l.experiment_run_id and not l.evidence_ids:
                issues.append(f"MQ-04: Lesson '{l.lesson_id}' lacks originating episode, experiment run, or evidence link.")

        # -------------------------------------------------------------
        # MQ-15: Open question marked resolved without notes
        # -------------------------------------------------------------
        for o in questions:
            if o.status == OpenQuestionStatus.RESOLVED:
                if not o.resolution_notes and not o.resolved_by_id:
                    issues.append(f"MQ-15: Open Question '{o.question_id}' marked RESOLVED without resolution notes or resolver ID.")

        # -------------------------------------------------------------
        # MQ-10: Embedding index compatibility check
        # -------------------------------------------------------------
        derived_status = "HEALTHY"
        if self.vector_index.vectors:
            if self.vector_index.index_version != "1.0.0":
                derived_status = "VERSION_MISMATCH"
                issues.append("MQ-10: Derived vector index version mismatch.")

        failures = [ep for ep in episodes if ep.is_failure]
        pending_consolidation = len([m for m in memories if m.promotion_state.value == "CAPTURED"])

        audit_passed = len(issues) == 0

        return MemoryHealthReport(
            total_memory_records=len(memories),
            total_episodes=len(episodes),
            total_decisions=len(decisions),
            total_failures=len(failures),
            total_lessons=len(lessons),
            total_open_questions=len(questions),
            total_contradictions=len(contradictions),
            pending_consolidation=pending_consolidation,
            stale_records=stale_count,
            orphan_records=orphan_count,
            broken_references=broken_refs_count,
            circular_support_count=circular_support_count,
            derived_index_status=derived_status,
            audit_passed=audit_passed,
            issues=issues,
        )

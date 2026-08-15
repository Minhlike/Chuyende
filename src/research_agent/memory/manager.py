"""
High-Level Memory Manager & Research Continuation Engine (Prompt 4, Sections 36..38, 43, 73, 74, ADR-0008)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.core.enums import (
    MemoryTier,
    MemoryRecordType,
    MemoryPromotionState,
    IntellectualOwnership,
    EpistemicStatus,
    DecisionStatus,
    OpenQuestionStatus,
    EpisodeStatus,
)
from research_agent.core.identifiers import format_stable_id
from research_agent.schemas.memory import (
    MemoryRecord,
    SessionRecord,
    EpisodeRecord,
    OpenQuestion,
    LessonLearned,
    StatusTransitionRecord,
    ContextBundle,
    MemoryHealthReport,
)
from research_agent.schemas.decision import DecisionRecord
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.embeddings import EmbeddingProvider, LocalBM25TFIDFEmbeddingProvider
from research_agent.memory.vector_index import DerivedVectorIndex
from research_agent.memory.retrieval import HybridRetrievalEngine
from research_agent.memory.consolidation import MemoryConsolidationService, ConsolidationResult
from research_agent.memory.health import MemoryHealthAuditor


class MemoryManager:
    """
    Unified high-level facade for Research Memory, Hybrid Retrieval,
    Consolidation, Continuation Bootstrap, and State Snapshots.
    """

    def __init__(
        self,
        repository: ResearchRepository,
        memory_root: Path | str = "memory",
        index_path: Path | str = "runtime/indexes/derived_vectors.json",
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        self.repo = repository
        self.memory_root = Path(memory_root)
        self.memory_root.mkdir(parents=True, exist_ok=True)
        (self.memory_root / "sessions").mkdir(parents=True, exist_ok=True)
        (self.memory_root / "snapshots").mkdir(parents=True, exist_ok=True)
        (self.memory_root / "procedural").mkdir(parents=True, exist_ok=True)
        (self.memory_root / "exports").mkdir(parents=True, exist_ok=True)

        self.embedding_provider = embedding_provider or LocalBM25TFIDFEmbeddingProvider()
        self.vector_index = DerivedVectorIndex(index_path=index_path, provider=self.embedding_provider)
        self.retrieval_engine = HybridRetrievalEngine(repository=self.repo, vector_index=self.vector_index)
        self.consolidation_service = MemoryConsolidationService(repository=self.repo, memory_root=self.memory_root)
        self.health_auditor = MemoryHealthAuditor(repository=self.repo, vector_index=self.vector_index)

    # -------------------------------------------------------------
    # Typed Write APIs (Section 36)
    # -------------------------------------------------------------
    def remember_decision(
        self,
        title: str,
        decision: str,
        rationale: str,
        context: str = "",
        alternatives_considered: Optional[List[str]] = None,
        evidence_ids: Optional[List[str]] = None,
        consequences: str = "Preserves research rigor.",
        related_nodes: Optional[List[str]] = None,
        related_claims: Optional[List[str]] = None,
        related_experiments: Optional[List[str]] = None,
        supersedes_id: Optional[str] = None,
        actor: str = "HUMAN_ARCHITECT_OR_AGENT",
        status: DecisionStatus = DecisionStatus.ACCEPTED,
    ) -> DecisionRecord:
        """Register a first-class Architecture/Research Decision (RC-15, Section 31)."""
        all_decs = self.repo.list_decisions()
        seq = len(all_decs) + 1
        dec_id = f"DEC-{seq:06d}"

        # If superseding an older decision, mark older decision as SUPERSEDED
        if supersedes_id:
            old_dec = self.repo.get_decision(supersedes_id)
            if old_dec:
                old_dec.status = DecisionStatus.SUPERSEDED
                old_dec.superseded_by_id = dec_id
                self.repo.save_decision(old_dec)
                # Record status transition event
                self.record_status_transition(
                    entity_type="DECISION",
                    entity_id=supersedes_id,
                    from_status="ACCEPTED",
                    to_status="SUPERSEDED",
                    cause=f"Superseded by {dec_id}: {title}",
                    decision_id=dec_id,
                    actor=actor,
                )

        record = DecisionRecord(
            decision_id=dec_id,
            title=title,
            status=status,
            context=context or title,
            decision=decision,
            rationale=rationale,
            alternatives_considered=alternatives_considered or [],
            evidence_ids=evidence_ids or [],
            consequences=consequences,
            target_affected_entities=related_nodes or [],
            related_nodes=related_nodes or [],
            related_claims=related_claims or [],
            related_experiments=related_experiments or [],
            supersedes_id=supersedes_id,
            actor=actor,
        )
        saved = self.repo.save_decision(record)
        self.vector_index.add_or_update(saved.decision_id, "DECISION", f"{saved.title} {saved.decision} {saved.rationale}")
        self.vector_index.save()
        return saved

    def record_episode(
        self,
        action: str,
        outcome: str,
        status: EpisodeStatus = EpisodeStatus.COMPLETED,
        object_reference: Optional[str] = None,
        related_node_code: Optional[str] = None,
        related_rq_id: Optional[str] = None,
        related_hyp_id: Optional[str] = None,
        related_artifact_ids: Optional[List[str]] = None,
        provenance_details: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        is_failure: bool = False,
        failure_reason: Optional[str] = None,
        session_id: Optional[str] = None,
        actor: str = "RESEARCH_AGENT",
    ) -> EpisodeRecord:
        """Record an episodic execution event (M3 Episodic Memory)."""
        episodes = self.repo.list_episodes()
        seq = len(episodes) + 1
        ep_id = f"EP-{seq:06d}"

        ep = EpisodeRecord(
            episode_id=ep_id,
            session_id=session_id,
            actor=actor,
            action=action,
            object_reference=object_reference,
            outcome=outcome,
            status=status,
            related_node_code=related_node_code,
            related_rq_id=related_rq_id,
            related_hyp_id=related_hyp_id,
            related_artifact_ids=related_artifact_ids or [],
            provenance_details=provenance_details or {},
            tags=tags or [],
            is_failure=is_failure,
            failure_reason=failure_reason,
        )
        saved = self.repo.save_episode(ep)
        self.vector_index.add_or_update(saved.episode_id, "EPISODE", f"{saved.action} {saved.outcome} {saved.failure_reason or ''}")
        self.vector_index.save()
        return saved

    def record_failure(
        self,
        action: str,
        failure_reason: str,
        object_reference: Optional[str] = None,
        related_node_code: Optional[str] = None,
        related_rq_id: Optional[str] = None,
        related_hyp_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> EpisodeRecord:
        """Explicitly record a research failure so negative results are never lost (RC-14, Section 33)."""
        return self.record_episode(
            action=action,
            outcome=f"FAILED: {failure_reason}",
            status=EpisodeStatus.FAILED,
            object_reference=object_reference,
            related_node_code=related_node_code,
            related_rq_id=related_rq_id,
            related_hyp_id=related_hyp_id,
            is_failure=True,
            failure_reason=failure_reason,
            session_id=session_id,
        )

    def record_lesson(
        self,
        title: str,
        statement: str,
        originating_episode_id: Optional[str] = None,
        experiment_run_id: Optional[str] = None,
        evidence_ids: Optional[List[str]] = None,
        scope: Optional[str] = None,
        actionable_recommendations: Optional[List[str]] = None,
    ) -> LessonLearned:
        """Record an actionable lesson learned from research experiments (Section 33)."""
        all_lessons = self.repo.list_lessons_learned()
        seq = len(all_lessons) + 1
        les_id = f"LES-{seq:06d}"

        les = LessonLearned(
            lesson_id=les_id,
            title=title,
            statement=statement,
            originating_episode_id=originating_episode_id,
            experiment_run_id=experiment_run_id,
            evidence_ids=evidence_ids or [],
            scope=scope,
            actionable_recommendations=actionable_recommendations or [],
        )
        saved = self.repo.save_lesson_learned(les)
        self.vector_index.add_or_update(saved.lesson_id, "LESSON", f"{saved.title} {saved.statement}")
        self.vector_index.save()
        return saved

    def create_open_question(
        self,
        question: str,
        why_open: str,
        required_evidence: str,
        related_rq_id: Optional[str] = None,
        related_hyp_id: Optional[str] = None,
        related_node_code: Optional[str] = None,
        proposed_experiment: Optional[str] = None,
        priority: str = "HIGH",
    ) -> OpenQuestion:
        """Create a first-class Open Research Question (Section 32)."""
        all_oqs = self.repo.list_open_questions()
        seq = len(all_oqs) + 1
        oq_id = f"OQ-{seq:06d}"

        oq = OpenQuestion(
            question_id=oq_id,
            question=question,
            related_rq_id=related_rq_id,
            related_hyp_id=related_hyp_id,
            related_node_code=related_node_code,
            why_open=why_open,
            required_evidence=required_evidence,
            proposed_experiment=proposed_experiment,
            priority=priority,
            status=OpenQuestionStatus.OPEN,
        )
        saved = self.repo.save_open_question(oq)
        self.vector_index.add_or_update(saved.question_id, "OPEN_QUESTION", f"{saved.question} {saved.why_open}")
        self.vector_index.save()
        return saved

    def record_status_transition(
        self,
        entity_type: str,
        entity_id: str,
        from_status: str,
        to_status: str,
        cause: str,
        evidence_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        actor: str = "RESEARCH_AGENT",
    ) -> StatusTransitionRecord:
        """Record an immutable status transition event (Section 8)."""
        transitions = self.repo.list_status_transitions()
        seq = len(transitions) + 1
        trans_id = f"STR-{seq:06d}"

        record = StatusTransitionRecord(
            transition_id=trans_id,
            entity_type=entity_type,
            entity_id=entity_id,
            from_status=from_status,
            to_status=to_status,
            cause=cause,
            evidence_id=evidence_id,
            decision_id=decision_id,
            actor=actor,
        )
        return self.repo.save_status_transition(record)

    # -------------------------------------------------------------
    # Query & Retrieval APIs (Section 37)
    # -------------------------------------------------------------
    def retrieve(self, query: str, max_items: int = 15, token_budget: int = 4000) -> ContextBundle:
        """Execute hybrid retrieval across all memory and knowledge tiers."""
        return self.retrieval_engine.retrieve(query=query, max_items=max_items, token_budget=token_budget)

    def consolidate_session(
        self,
        session: SessionRecord,
        candidate_memories: Optional[List[MemoryRecord]] = None,
        candidate_decisions: Optional[List[DecisionRecord]] = None,
        candidate_episodes: Optional[List[EpisodeRecord]] = None,
        candidate_lessons: Optional[List[LessonLearned]] = None,
        candidate_questions: Optional[List[OpenQuestion]] = None,
    ) -> ConsolidationResult:
        """Execute session memory consolidation."""
        return self.consolidation_service.consolidate_session(
            session=session,
            candidate_memories=candidate_memories,
            candidate_decisions=candidate_decisions,
            candidate_episodes=candidate_episodes,
            candidate_lessons=candidate_lessons,
            candidate_questions=candidate_questions,
        )

    def audit_health(self) -> MemoryHealthReport:
        """Perform comprehensive memory health check."""
        return self.health_auditor.audit()

    def rebuild_indexes(self) -> Tuple[int, int]:
        """Rebuild FTS5 and Derived Vector indexes from canonical database."""
        fts_count = self.repo.rebuild_fts_index()
        vec_count = self.vector_index.rebuild_from_repository(self.repo)
        return fts_count, vec_count

    # -------------------------------------------------------------
    # Continuation Bootstrap & State Snapshot (Sections 43, 73, 74)
    # -------------------------------------------------------------
    def get_research_state(self) -> Dict[str, Any]:
        """Get canonical state summary for Roadmap, Reference Map, RQ, Hypotheses, Decisions, and Open Questions."""
        roadmap = self.repo.get_roadmap()
        roadmap_ver = roadmap.version if roadmap else "1.0.0"
        central_obj = roadmap.central_object if roadmap else "feature representation z"

        sources = self.repo.list_sources()
        claims = self.repo.list_claims()
        decisions = self.repo.list_decisions(status=DecisionStatus.ACCEPTED)
        episodes = self.repo.list_episodes(only_failures=True)
        questions = self.repo.list_open_questions(status=OpenQuestionStatus.OPEN)
        lessons = self.repo.list_lessons_learned()
        contributions = self.repo.list_candidate_contributions()
        rqs = self.repo.list_research_questions()
        hypotheses = self.repo.list_hypotheses()

        return {
            "roadmap_version": roadmap_ver,
            "reference_map_version": "1.0.0",
            "central_object": central_obj,
            "research_questions": [f"{q.code}: {q.title}" for q in rqs],
            "hypotheses": [f"{h.code}: {h.title}" for h in hypotheses],
            "active_contributions": [f"{c.contribution_id} ({c.novelty_status.value}): {c.name}" for c in contributions],
            "open_questions": [f"{o.question_id} [{o.priority}]: {o.question}" for o in questions],
            "active_decisions": [f"{d.decision_id}: {d.title}" for d in decisions],
            "recent_failures": [f"{ep.episode_id}: {ep.action} -> {ep.failure_reason}" for ep in episodes[:5]],
            "total_verified_sources": len(sources),
            "total_canonical_claims": len(claims),
            "total_lessons_learned": len(lessons),
        }

    def generate_resume_bundle(self) -> ContextBundle:
        """Create lean bootstrap ContextBundle for resuming agent work (Section 74)."""
        state = self.get_research_state()
        return self.retrieve(
            query="resume current research state and open questions",
            max_items=10,
            token_budget=2000,
        )

    def create_snapshot(self) -> Path:
        """Persist a point-in-time JSON snapshot of research state into memory/snapshots/."""
        state = self.get_research_state()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_path = self.memory_root / "snapshots" / f"snapshot_{timestamp}.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return snapshot_path

    def export_human_readable_memory(self) -> Path:
        """Export human-readable research memory status to memory/memory-export.md."""
        state = self.get_research_state()
        export_path = self.memory_root / "memory-export.md"

        content = f"""<!-- GENERATED — NOT CANONICAL -->
# Current Research Memory & State Export

- **Exported At:** {datetime.now(timezone.utc).isoformat()}
- **Roadmap Version:** `{state['roadmap_version']}`
- **Reference Map Version:** `{state['reference_map_version']}`
- **Central Research Object:** `{state['central_object']}`

---

## 1. Research Questions & Hypotheses
"""
        for rq in state["research_questions"]:
            content += f"- **{rq}**\n"
        content += "\n"
        for h in state["hypotheses"]:
            content += f"- **{h}**\n"

        content += f"\n---\n\n## 2. Active Candidate Contributions ({len(state['active_contributions'])})\n"
        for c in state["active_contributions"]:
            content += f"- {c}\n"

        content += f"\n---\n\n## 3. Active Architecture & Research Decisions ({len(state['active_decisions'])})\n"
        for d in state["active_decisions"]:
            content += f"- {d}\n"

        content += f"\n---\n\n## 4. Open Research Questions ({len(state['open_questions'])})\n"
        for o in state["open_questions"]:
            content += f"- {o}\n"

        content += f"\n---\n\n## 5. Recent Failures & Negative Controls ({len(state['recent_failures'])})\n"
        for f_item in state["recent_failures"]:
            content += f"- {f_item}\n"

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path

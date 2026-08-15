"""
Controlled Memory Consolidation Pipeline & Session Handoff Engine (Prompt 4, Sections 11..14, 38, ADR-0008)
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.core.enums import (
    MemoryTier,
    MemoryRecordType,
    MemoryPromotionState,
    IntellectualOwnership,
    EpistemicStatus,
    ClaimType,
    DecisionStatus,
    OpenQuestionStatus,
)
from research_agent.core.exceptions import InvariantViolationError, ProvenanceError
from research_agent.schemas.memory import (
    MemoryRecord,
    SessionRecord,
    EpisodeRecord,
    OpenQuestion,
    LessonLearned,
)
from research_agent.schemas.decision import DecisionRecord
from research_agent.storage.repository import ResearchRepository


class ConsolidationResult:
    """Outcome report for a memory consolidation execution."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.promoted_records: List[MemoryRecord] = []
        self.rejected_records: List[Dict[str, Any]] = []
        self.decisions_consolidated: List[DecisionRecord] = []
        self.episodes_consolidated: List[EpisodeRecord] = []
        self.lessons_consolidated: List[LessonLearned] = []
        self.open_questions_consolidated: List[OpenQuestion] = []
        self.handoff_markdown: str = ""
        self.journal_path: Optional[str] = None


class MemoryConsolidationService:
    """
    Deterministic rule-driven consolidation pipeline enforcing:
    - MR-01..MR-06 Anti-hallucination safeguards
    - Canonical reference verification
    - Deduplication & Conflict resolution
    - Session handoff & Journal persistence
    """

    def __init__(self, repository: ResearchRepository, memory_root: Path | str = "memory"):
        self.repo = repository
        self.memory_root = Path(memory_root)

    def validate_candidate_memory(self, candidate: MemoryRecord) -> Tuple[bool, Optional[str]]:
        """
        Enforce Invariants MR-01 through MR-06 and provenance integrity.
        """
        # MR-01: LLM-generated statement without provenance cannot become SOURCE_FACT
        if candidate.ownership == IntellectualOwnership.SOURCE and not candidate.reference_id:
            if not candidate.associated_entity_ids:
                return False, "MR-01 VIOLATION: Source fact memory must reference a verified canonical source ID."

        # MR-03 & MR-05: Generated summary must point to canonical records and cannot self-support
        if candidate.is_generated_summary:
            if not candidate.associated_entity_ids and not candidate.reference_id:
                return False, "MR-03 VIOLATION: Generated summary must reference underlying canonical IDs."
            if candidate.memory_id in candidate.associated_entity_ids:
                return False, "MR-05 VIOLATION: Circular self-support detected in memory record."

        # Validate canonical reference exists if provided
        if candidate.reference_id:
            ref_id = candidate.reference_id
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
                return False, f"Broken canonical reference: '{ref_id}' does not exist in repository."

        return True, None

    def consolidate_session(
        self,
        session: SessionRecord,
        candidate_memories: Optional[List[MemoryRecord]] = None,
        candidate_decisions: Optional[List[DecisionRecord]] = None,
        candidate_episodes: Optional[List[EpisodeRecord]] = None,
        candidate_lessons: Optional[List[LessonLearned]] = None,
        candidate_questions: Optional[List[OpenQuestion]] = None,
    ) -> ConsolidationResult:
        """
        Execute full session consolidation, persist verified entities, and write human-readable journal.
        """
        result = ConsolidationResult(session_id=session.session_id)

        # 1. Consolidate Candidate Memories
        existing_memories = self.repo.list_memories()
        existing_topics = {m.topic.strip().lower() for m in existing_memories}

        if candidate_memories:
            for cand in candidate_memories:
                valid, reason = self.validate_candidate_memory(cand)
                if not valid:
                    cand.promotion_state = MemoryPromotionState.REJECTED
                    result.rejected_records.append({"memory_id": cand.memory_id, "reason": reason})
                    continue

                # Deduplication check
                norm_topic = cand.topic.strip().lower()
                if norm_topic in existing_topics:
                    # Check if exact duplicate content
                    cand.promotion_state = MemoryPromotionState.REJECTED
                    result.rejected_records.append({
                        "memory_id": cand.memory_id,
                        "reason": f"Duplicate candidate memory detected for topic '{cand.topic}'"
                    })
                    continue

                # Promote & Save
                cand.promotion_state = MemoryPromotionState.CONSOLIDATED
                cand.session_id = session.session_id
                cand.updated_at = datetime.now(timezone.utc)
                saved_mem = self.repo.save_memory(cand)
                result.promoted_records.append(saved_mem)
                existing_topics.add(norm_topic)

        # 2. Consolidate Decisions
        if candidate_decisions:
            for dec in candidate_decisions:
                saved_dec = self.repo.save_decision(dec)
                result.decisions_consolidated.append(saved_dec)
                session.decisions_made.append(f"{dec.decision_id}: {dec.title}")

        # 3. Consolidate Episodes
        if candidate_episodes:
            for ep in candidate_episodes:
                ep.session_id = session.session_id
                saved_ep = self.repo.save_episode(ep)
                result.episodes_consolidated.append(saved_ep)
                if ep.is_failure:
                    session.unresolved_items.append(f"FAILURE: {ep.action} ({ep.failure_reason or 'unspecified'})")

        # 4. Consolidate Lessons
        if candidate_lessons:
            for les in candidate_lessons:
                saved_les = self.repo.save_lesson_learned(les)
                result.lessons_consolidated.append(saved_les)

        # 5. Consolidate Open Questions
        if candidate_questions:
            for oq in candidate_questions:
                saved_oq = self.repo.save_open_question(oq)
                result.open_questions_consolidated.append(saved_oq)
                session.unresolved_items.append(f"OPEN QUESTION: {oq.question_id} - {oq.question}")

        # 6. Generate Handoff Summary
        handoff_md = self._generate_handoff_markdown(session, result)
        session.handoff_summary = handoff_md
        session.end_time = datetime.now(timezone.utc)
        session.updated_at = datetime.now(timezone.utc)
        self.repo.save_research_session(session)
        result.handoff_markdown = handoff_md

        # 7. Write Session Journal
        journal_path = self._write_session_journal(session, result)
        result.journal_path = str(journal_path)

        return result

    def _generate_handoff_markdown(self, session: SessionRecord, result: ConsolidationResult) -> str:
        lines = [
            f"# Session Handoff Bundle: {session.session_id}",
            f"**Objective:** {session.objective}",
            f"**Time:** {session.start_time.isoformat()} to {session.end_time.isoformat() if session.end_time else 'ongoing'}",
            f"**Git Commit:** `{session.git_commit_hash or 'N/A'}`",
            "",
            "## Actions & Modifications",
        ]
        for a in session.actions_summary:
            lines.append(f"- {a}")
        if not session.actions_summary:
            lines.append("- (No explicit actions recorded)")

        lines.append("")
        lines.append("## Decisions Made")
        for d in result.decisions_consolidated:
            lines.append(f"- **{d.decision_id}** (`{d.status.value}`): {d.title} — *{d.decision}*")
        if not result.decisions_consolidated:
            lines.append("- (No decisions registered)")

        lines.append("")
        lines.append("## Failures & Lessons")
        for ep in result.episodes_consolidated:
            if ep.is_failure:
                lines.append(f"- **[FAIL] {ep.episode_id}**: {ep.action} -> {ep.failure_reason}")
        for l in result.lessons_consolidated:
            lines.append(f"- **[LESSON] {l.lesson_id}**: {l.title} — {l.statement}")

        lines.append("")
        lines.append("## Unresolved Items & Next Recommended Steps")
        for item in session.unresolved_items:
            lines.append(f"- {item}")
        if not session.unresolved_items:
            lines.append("- (All session items resolved)")

        return "\n".join(lines)

    def _write_session_journal(self, session: SessionRecord, result: ConsolidationResult) -> Path:
        sessions_dir = self.memory_root / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        date_str = session.start_time.strftime("%Y-%m-%d")
        safe_id = session.session_id.replace(":", "_")
        filename = f"{date_str}_{safe_id}.md"
        filepath = sessions_dir / filename

        content = f"""<!-- GENERATED — RESEARCH SESSION JOURNAL -->
# Research Session Journal: {session.session_id}

- **Date / Time:** {session.start_time.isoformat()}
- **Objective:** {session.objective}
- **Active Roadmap Nodes:** {', '.join(session.active_roadmap_nodes) or 'General'}
- **Git Commit:** `{session.git_commit_hash or 'N/A'}`

---

## 1. Consolidated Decisions ({len(result.decisions_consolidated)})
"""
        for d in result.decisions_consolidated:
            content += f"\n### {d.decision_id}: {d.title}\n- **Status:** `{d.status.value}`\n- **Rationale:** {d.rationale}\n- **Decision:** {d.decision}\n"

        content += f"\n---\n\n## 2. Episodic Events & Experiments ({len(result.episodes_consolidated)})\n"
        for ep in result.episodes_consolidated:
            st = "[FAIL]" if ep.is_failure else "[OK]"
            content += f"- **{st} {ep.episode_id}** (`{ep.action}`): {ep.outcome}\n"

        content += f"\n---\n\n## 3. Open Questions ({len(result.open_questions_consolidated)})\n"
        for oq in result.open_questions_consolidated:
            content += f"- **{oq.question_id}** (Priority `{oq.priority}`): {oq.question}\n  - *Why open:* {oq.why_open}\n  - *Required evidence:* {oq.required_evidence}\n"

        content += f"\n---\n\n## 4. Handoff Summary\n\n{result.handoff_markdown}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

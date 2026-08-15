"""
Hybrid Retrieval Engine & Context Bundle Assembler (Prompt 4, Sections 19..27, ADR-0008)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.core.enums import (
    QueryIntentType,
    IntellectualOwnership,
    EpistemicStatus,
    ClaimType,
    DecisionStatus,
    OpenQuestionStatus,
    ArgumentRelationType,
)
from research_agent.schemas.memory import ContextBundle, MemoryRecord
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.vector_index import DerivedVectorIndex


class HybridRetrievalEngine:
    """
    Multi-signal hybrid retrieval engine:
    1. Exact ID Resolution (Top Priority)
    2. Structured Filtering
    3. Lexical FTS5 Full-Text Search
    4. Semantic Cosine Vector Ranking
    5. Graph Relation Traversal & Contradiction Extraction
    6. Token Budgeting & Provenance Packaging
    """

    def __init__(self, repository: ResearchRepository, vector_index: Optional[DerivedVectorIndex] = None):
        self.repo = repository
        self.vector_index = vector_index or DerivedVectorIndex()

    def classify_intent(self, query: str) -> QueryIntentType:
        """Classify research query into canonical intent (Section 21)."""
        q_lower = query.lower()
        if re.search(r'\b(clm-\d+|claim)\b', q_lower):
            return QueryIntentType.CLAIM_LOOKUP
        if re.search(r'\b(src-\d+|source|paper|author|doi|bib)\b', q_lower):
            return QueryIntentType.SOURCE_LOOKUP
        if re.search(r'\b(evd-\d+|evidence|quote|locator)\b', q_lower):
            return QueryIntentType.EVIDENCE_LOOKUP
        if re.search(r'\b(rq\d+|h\d+|hyp-\d+|research question|hypothesis)\b', q_lower):
            return QueryIntentType.ROADMAP_LOOKUP
        if re.search(r'\b(dec-\d+|decision|adr|rdr|why did we|why was)\b', q_lower):
            return QueryIntentType.DECISION_LOOKUP
        if re.search(r'\b(contradict|conflict|contested|opposing|disagree)\b', q_lower):
            return QueryIntentType.CONTRADICTION_LOOKUP
        if re.search(r'\b(exp-\d+|experiment|failed|failure|run|benchmark)\b', q_lower):
            return QueryIntentType.EXPERIMENT_LOOKUP
        if re.search(r'\b(oq-\d+|open question|unresolved|missing)\b', q_lower):
            return QueryIntentType.OPEN_QUESTION_LOOKUP
        if re.search(r'\b(cand-\d+|contribution|novelty|ours)\b', q_lower):
            return QueryIntentType.CONTRIBUTION_LOOKUP
        if re.search(r'\b(history|status transition|timeline|superseded)\b', q_lower):
            return QueryIntentType.HISTORY_LOOKUP
        if re.search(r'\b(current state|research state|overview|status)\b', q_lower):
            return QueryIntentType.CURRENT_STATE
        if re.search(r'\b(skill|protocol|procedure|checklist)\b', q_lower):
            return QueryIntentType.PROCEDURE_LOOKUP
        return QueryIntentType.SEMANTIC_DISCOVERY

    def extract_stable_ids(self, query: str) -> List[str]:
        """Extract exact stable entity IDs from query text (Section 22)."""
        patterns = [
            r'CLM-\d+',
            r'SRC-\d+',
            r'EVD-\d+',
            r'DEC-\d+',
            r'EP-\d+',
            r'OQ-\d+',
            r'LES-\d+',
            r'NOD-\d+',
            r'ROD-\d+',
            r'CAND-\d+',
            r'SES-\d+',
            r'SKL-\d+',
            r'STR-\d+',
            r'CTR-\d+',
            r'\bRQ[1-5]\b',
            r'\bH[1-5]\b',
            r'\b\d+\.\d+(\.\d+)?\b',  # Roadmap node codes: 1.1, 1.1.1
        ]
        found = set()
        for p in patterns:
            matches = re.findall(p, query, re.IGNORECASE)
            for m in matches:
                found.add(m.upper() if not re.match(r'^\d+\.\d+', m) else m)
        return list(found)

    def retrieve(
        self,
        query: str,
        max_items: int = 15,
        token_budget: int = 4000,
    ) -> ContextBundle:
        """
        Execute full hybrid retrieval pipeline and return a structured ContextBundle.
        """
        intent = self.classify_intent(query)
        extracted_ids = self.extract_stable_ids(query)

        canonical_entities: List[Dict[str, Any]] = []
        verified_facts: List[Dict[str, Any]] = []
        supporting_evidence: List[Dict[str, Any]] = []
        contradictory_evidence: List[Dict[str, Any]] = []
        qualifications: List[Dict[str, Any]] = []
        our_inferences: List[Dict[str, Any]] = []
        decisions: List[Dict[str, Any]] = []
        experiment_results: List[Dict[str, Any]] = []
        open_questions: List[Dict[str, Any]] = []
        lessons: List[Dict[str, Any]] = []
        provenance_chain: List[Dict[str, Any]] = []
        retrieval_reasons: Dict[str, str] = {}

        seen_entity_ids = set()

        def add_entity_to_bundle(ent_id: str, ent_type: str, data: Dict[str, Any], reason: str):
            if ent_id in seen_entity_ids:
                return
            seen_entity_ids.add(ent_id)
            retrieval_reasons[ent_id] = reason

            if ent_type == "SOURCE":
                canonical_entities.append(data)
                provenance_chain.append({"id": ent_id, "type": "SOURCE", "provenance": data.get("canonical_url") or data.get("venue")})
            elif ent_type == "CLAIM":
                ownership = data.get("ownership")
                claim_type = data.get("claim_type")
                if claim_type == "OUR_INFERENCE":
                    our_inferences.append(data)
                elif ownership == "SOURCE":
                    verified_facts.append(data)
                else:
                    canonical_entities.append(data)
            elif ent_type == "EVIDENCE":
                supporting_evidence.append(data)
            elif ent_type == "DECISION":
                decisions.append(data)
            elif ent_type == "OPEN_QUESTION":
                open_questions.append(data)
            elif ent_type == "LESSON":
                lessons.append(data)
            elif ent_type == "EPISODE":
                experiment_results.append(data)
            else:
                canonical_entities.append(data)

        # -------------------------------------------------------------
        # Step 1: Exact Stable ID Lookup (Top Priority)
        # -------------------------------------------------------------
        for raw_id in extracted_ids:
            # Check Claim
            claim = self.repo.get_claim(raw_id)
            if claim:
                add_entity_to_bundle(claim.claim_id, "CLAIM", claim.model_dump(mode="json"), "EXACT_ID_MATCH")
                # Expand Graph for Claim
                self._expand_claim_graph(claim.claim_id, add_entity_to_bundle, contradictory_evidence)
                continue

            # Check Source
            src = self.repo.get_source(raw_id)
            if src:
                add_entity_to_bundle(src.source_id, "SOURCE", src.model_dump(mode="json"), "EXACT_ID_MATCH")
                continue

            # Check Decision
            dec = self.repo.get_decision(raw_id)
            if dec:
                add_entity_to_bundle(dec.decision_id, "DECISION", dec.model_dump(mode="json"), "EXACT_ID_MATCH")
                # Expand supersedes
                if dec.supersedes_id:
                    old_dec = self.repo.get_decision(dec.supersedes_id)
                    if old_dec:
                        add_entity_to_bundle(old_dec.decision_id, "DECISION", old_dec.model_dump(mode="json"), "SUPERSEDES_CHAIN")
                continue

            # Check Open Question
            oq = self.repo.get_open_question(raw_id)
            if oq:
                add_entity_to_bundle(oq.question_id, "OPEN_QUESTION", oq.model_dump(mode="json"), "EXACT_ID_MATCH")
                continue

            # Check Lesson
            les = self.repo.get_lesson_learned(raw_id)
            if les:
                add_entity_to_bundle(les.lesson_id, "LESSON", les.model_dump(mode="json"), "EXACT_ID_MATCH")
                continue

            # Check Episode
            ep = self.repo.get_episode(raw_id)
            if ep:
                add_entity_to_bundle(ep.episode_id, "EPISODE", ep.model_dump(mode="json"), "EXACT_ID_MATCH")
                continue

            # Check Roadmap Node Code
            node = self.repo.get_roadmap_node_by_code(raw_id)
            if node:
                add_entity_to_bundle(node.node_id, "ROADMAP_NODE", node.model_dump(mode="json"), "EXACT_NODE_CODE")
                self._expand_node_graph(node.code, add_entity_to_bundle, contradictory_evidence)
                continue

            # Check Research Question
            rq = self.repo.get_research_question(raw_id)
            if rq:
                add_entity_to_bundle(rq.rq_id, "RESEARCH_QUESTION", rq.model_dump(mode="json"), "EXACT_RQ_CODE")
                self._expand_rq_graph(rq.code, add_entity_to_bundle, open_questions)
                continue

            # Check Hypothesis
            hyp = self.repo.get_hypothesis(raw_id)
            if hyp:
                add_entity_to_bundle(hyp.hyp_id, "HYPOTHESIS", hyp.model_dump(mode="json"), "EXACT_HYP_CODE")
                self._expand_hyp_graph(hyp.code, add_entity_to_bundle)
                continue

        # -------------------------------------------------------------
        # Step 2: Lexical Full-Text Search (FTS5)
        # -------------------------------------------------------------
        fts_hits = self.repo.search_fts(query, limit=10)
        for hit in fts_hits:
            e_id = hit["entity_id"]
            e_type = hit["entity_type"]
            self._load_and_add_entity(e_id, e_type, add_entity_to_bundle, "FTS_LEXICAL_MATCH")

        # -------------------------------------------------------------
        # Step 3: Semantic Cosine Vector Search
        # -------------------------------------------------------------
        vector_hits = self.vector_index.search(query, top_k=8)
        for e_id, e_type, score in vector_hits:
            if score > 0.15:  # Relevance threshold
                self._load_and_add_entity(e_id, e_type, add_entity_to_bundle, f"SEMANTIC_SIMILARITY_{score:.2f}")

        # -------------------------------------------------------------
        # Step 4: Contradiction Sweep (Section 15)
        # -------------------------------------------------------------
        # If contradiction lookup or contested intent, pull all active contradictions
        if intent == QueryIntentType.CONTRADICTION_LOOKUP:
            for ctr in self.repo.list_contradictions():
                contradictory_evidence.append(ctr.model_dump(mode="json"))

        # Calculate estimated tokens (approx 4 chars per token)
        total_text_len = (
            len(str(canonical_entities)) + len(str(verified_facts)) +
            len(str(supporting_evidence)) + len(str(contradictory_evidence)) +
            len(str(decisions)) + len(str(open_questions)) + len(str(lessons))
        )
        token_estimate = max(1, total_text_len // 4)

        return ContextBundle(
            query=query,
            resolved_intent=intent,
            canonical_entities=canonical_entities[:max_items],
            verified_facts=verified_facts[:max_items],
            supporting_evidence=supporting_evidence[:max_items],
            contradictory_evidence=contradictory_evidence[:max_items],
            qualifications=qualifications[:max_items],
            our_inferences=our_inferences[:max_items],
            decisions=decisions[:max_items],
            experiment_results=experiment_results[:max_items],
            open_questions=open_questions[:max_items],
            lessons=lessons[:max_items],
            provenance_chain=provenance_chain[:max_items],
            retrieval_reasons=retrieval_reasons,
            token_estimate=token_estimate,
        )

    def _load_and_add_entity(self, entity_id: str, entity_type: str, add_fn: Any, reason: str):
        if entity_type == "SOURCE":
            src = self.repo.get_source(entity_id)
            if src:
                add_fn(src.source_id, "SOURCE", src.model_dump(mode="json"), reason)
        elif entity_type == "CLAIM":
            c = self.repo.get_claim(entity_id)
            if c:
                add_fn(c.claim_id, "CLAIM", c.model_dump(mode="json"), reason)
        elif entity_type == "DECISION":
            d = self.repo.get_decision(entity_id)
            if d:
                add_fn(d.decision_id, "DECISION", d.model_dump(mode="json"), reason)
        elif entity_type == "OPEN_QUESTION":
            o = self.repo.get_open_question(entity_id)
            if o:
                add_fn(o.question_id, "OPEN_QUESTION", o.model_dump(mode="json"), reason)
        elif entity_type == "LESSON":
            l = self.repo.get_lesson_learned(entity_id)
            if l:
                add_fn(l.lesson_id, "LESSON", l.model_dump(mode="json"), reason)
        elif entity_type == "EPISODE":
            e = self.repo.get_episode(entity_id)
            if e:
                add_fn(e.episode_id, "EPISODE", e.model_dump(mode="json"), reason)
        elif entity_type == "MEMORY":
            m = self.repo.get_memory(entity_id)
            if m:
                add_fn(m.memory_id, "MEMORY", m.model_dump(mode="json"), reason)

    def _expand_claim_graph(self, claim_id: str, add_fn: Any, contradiction_bucket: List[Dict[str, Any]]):
        """Expand Claim -> Evidence -> Source and fetch opposing claims."""
        claim = self.repo.get_claim(claim_id)
        if not claim:
            return
        # Link Evidences
        for evd_id in claim.evidence_ids:
            evd = self.repo.get_evidence(evd_id)
            if evd:
                add_fn(evd.evidence_id, "EVIDENCE", evd.model_dump(mode="json"), f"CLAIM_EVIDENCE_{claim_id}")
                src = self.repo.get_source(evd.source_id)
                if src:
                    add_fn(src.source_id, "SOURCE", src.model_dump(mode="json"), f"SOURCE_FOR_{evd_id}")

        # Check ClaimRelations for Contradictions
        relations = self.repo.list_claim_relations(claim_id)
        for rel in relations:
            if rel.relation_type == ArgumentRelationType.CONTRADICTS:
                opp_id = rel.target_claim_id if rel.source_claim_id == claim_id else rel.source_claim_id
                opp_claim = self.repo.get_claim(opp_id)
                if opp_claim:
                    contradiction_bucket.append({
                        "relation_id": rel.relation_id,
                        "contradicts_claim_id": claim_id,
                        "opposing_claim": opp_claim.model_dump(mode="json"),
                        "notes": rel.notes,
                    })

    def _expand_node_graph(self, node_code: str, add_fn: Any, contradiction_bucket: List[Dict[str, Any]]):
        """Expand Roadmap Node -> Ownership Mappings -> Sources -> Claims."""
        mappings = self.repo.list_ownership_mappings(node_code=node_code)
        for m in mappings:
            for s_id in m.primary_sources:
                src = self.repo.get_source(s_id)
                if src:
                    add_fn(src.source_id, "SOURCE", src.model_dump(mode="json"), f"NODE_{node_code}_SOURCE")

    def _expand_rq_graph(self, rq_code: str, add_fn: Any, oq_bucket: List[Dict[str, Any]]):
        """Expand RQ -> Hypotheses -> Linked Open Questions."""
        hypotheses = self.repo.list_hypotheses()
        for h in hypotheses:
            if h.rq_id == rq_code or h.code.startswith(rq_code.replace("RQ", "H")):
                add_fn(h.hyp_id, "HYPOTHESIS", h.model_dump(mode="json"), f"RQ_{rq_code}_HYPOTHESIS")

        # Open questions linked to RQ
        for oq in self.repo.list_open_questions():
            if oq.related_rq_id == rq_code:
                oq_bucket.append(oq.model_dump(mode="json"))

    def _expand_hyp_graph(self, hyp_code: str, add_fn: Any):
        """Expand Hypothesis -> Linked Episodes & Lessons."""
        for ep in self.repo.list_episodes():
            if ep.related_hyp_id == hyp_code:
                add_fn(ep.episode_id, "EPISODE", ep.model_dump(mode="json"), f"HYP_{hyp_code}_EPISODE")
        for les in self.repo.list_lessons_learned():
            if hyp_code in les.title or (les.scope and hyp_code in les.scope):
                add_fn(les.lesson_id, "LESSON", les.model_dump(mode="json"), f"HYP_{hyp_code}_LESSON")

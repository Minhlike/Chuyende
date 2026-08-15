"""
Reference Map Query and Audit Service (Section 33, Section 52)
"""

from typing import Any, Dict, List, Optional
from research_agent.core.enums import (
    IntellectualOwnership,
    NoveltyStatus,
    CitationFirewallStatus,
    ArgumentRelationType,
)
from research_agent.schemas.reference_map import ReferenceMapSpecification
from research_agent.schemas.source import Source
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.claim import Claim, ClaimRelation
from research_agent.schemas.ownership import OwnershipMapping, CandidateContribution
from research_agent.schemas.citation import CitationFirewallRule
from research_agent.storage.repository import ResearchRepository


class ReferenceMapQueryService:
    """Provides high-level programmatic and CLI queries against the Reference & Ownership Map."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def get_reference_map(self) -> Optional[ReferenceMapSpecification]:
        """Retrieve full reference map specification."""
        return self.repo.get_reference_map()

    def get_source(self, source_id_or_key: str) -> Optional[Source]:
        """Look up Source by SRC-ID or citation_key."""
        src = self.repo.get_source(source_id_or_key)
        if not src:
            src = self.repo.get_source_by_citation_key(source_id_or_key)
        return src

    def get_sources_for_node(self, node_code: str) -> List[Source]:
        """Retrieve all sources linked directly or via ownership to a roadmap node code."""
        mappings = self.repo.list_ownership_mappings(node_code=node_code)
        source_ids: Set[str] = set()
        for m in mappings:
            source_ids.update(m.source_ids)
            source_ids.update(m.motivation_source_ids)

        # Also search direct relevant_roadmap_nodes in Source
        all_sources = self.repo.list_sources()
        for s in all_sources:
            if node_code in s.relevant_roadmap_nodes or any(n.startswith(f"{node_code}.") for n in s.relevant_roadmap_nodes):
                source_ids.add(s.source_id)

        return [s for s in all_sources if s.source_id in source_ids]

    def get_ownership_mappings(
        self,
        node_code: Optional[str] = None,
        ownership: Optional[IntellectualOwnership] = None,
    ) -> List[OwnershipMapping]:
        """Query fine-grained ownership mappings."""
        return self.repo.list_ownership_mappings(node_code=node_code, ownership=ownership)

    def get_contributions(self, novelty_status: Optional[NoveltyStatus] = None) -> List[CandidateContribution]:
        """Query candidate contributions."""
        all_contribs = self.repo.list_candidate_contributions()
        if novelty_status:
            return [c for c in all_contribs if c.novelty_status == novelty_status]
        return all_contribs

    def get_citation_firewall_rules(self, status: Optional[CitationFirewallStatus] = None) -> List[CitationFirewallRule]:
        """Query Citation Firewall rules."""
        return self.repo.list_citation_firewall_rules(status=status)

    def get_contradictory_claims(self) -> List[Dict[str, Any]]:
        """Retrieve all pairs of claims with CONTRADICTS relation."""
        relations = self.repo.list_claim_relations()
        contradict_rels = [r for r in relations if r.relation_type == ArgumentRelationType.CONTRADICTS]
        results = []
        for rel in contradict_rels:
            clm_a = self.repo.get_claim(rel.source_claim_id)
            clm_b = self.repo.get_claim(rel.target_claim_id)
            results.append({
                "relation_id": rel.relation_id,
                "claim_a": clm_a.statement if clm_a else rel.source_claim_id,
                "claim_b": clm_b.statement if clm_b else rel.target_claim_id,
                "notes": rel.notes,
            })
        return results

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Calculate comprehensive reference, ownership, and citation coverage metrics."""
        nodes = self.repo.list_roadmap_nodes()
        sources = self.repo.list_sources()
        claims = self.repo.list_claims()
        evidences = self.repo.list_evidences()
        mappings = self.repo.list_ownership_mappings()
        contribs = self.repo.list_candidate_contributions()
        firewall = self.repo.list_citation_firewall_rules()

        peer_reviewed = [s for s in sources if s.source_type.value in ("PEER_REVIEWED_TOP_VENUE", "PEER_REVIEWED")]
        preprints = [s for s in sources if s.source_type.value == "PREPRINT"]
        datasets = [s for s in sources if s.source_type.value == "OFFICIAL_DATASET"]
        standards = [s for s in sources if s.source_type.value == "PRIMARY_STANDARD"]

        ours_mappings = [m for m in mappings if m.ownership == IntellectualOwnership.OURS]
        adapted_mappings = [m for m in mappings if m.ownership == IntellectualOwnership.ADAPTED]
        source_mappings = [m for m in mappings if m.ownership == IntellectualOwnership.SOURCE]
        baseline_mappings = [m for m in mappings if m.ownership == IntellectualOwnership.BASELINE]

        ready_citations = [f for f in firewall if f.status == CitationFirewallStatus.READY]
        blocked_citations = [f for f in firewall if f.status == CitationFirewallStatus.BLOCKED]

        return {
            "total_nodes": len(nodes),
            "total_sources": len(sources),
            "peer_reviewed_sources": len(peer_reviewed),
            "official_datasets": len(datasets),
            "official_standards": len(standards),
            "preprints": len(preprints),
            "total_claims": len(claims),
            "total_evidences": len(evidences),
            "total_ownership_mappings": len(mappings),
            "ours_mappings": len(ours_mappings),
            "adapted_mappings": len(adapted_mappings),
            "source_mappings": len(source_mappings),
            "baseline_mappings": len(baseline_mappings),
            "candidate_contributions": len(contribs),
            "citation_firewall_ready": len(ready_citations),
            "citation_firewall_blocked": len(blocked_citations),
        }

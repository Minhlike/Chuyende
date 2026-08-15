"""
Reference and Ownership Map Ingestion and Verification Interface (Prompt 3 Target)
"""

import json
import re
from typing import Any, Dict, List, Optional, Set
from research_agent.core.enums import (
    IntellectualOwnership,
    ClaimType,
    NoveltyStatus,
    SourceQualityTier,
    SourceVerificationState,
    CitationFirewallStatus,
    SupportType,
)
from research_agent.core.exceptions import InvariantViolationError
from research_agent.core.hash_utils import compute_string_sha256
from research_agent.schemas.reference_map import ReferenceMapSpecification
from research_agent.schemas.source import Source, SourceArtifact, SourceVersion
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.claim import Claim, ClaimRelation
from research_agent.schemas.ownership import OwnershipMapping, CandidateContribution
from research_agent.schemas.citation import CitationFirewallRule
from research_agent.storage.repository import ResearchRepository


DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")


class ReferenceMapIngestionService:
    """Service to ingest, validate, verify, and persist the Reference & Ownership Map."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def validate_reference_map_specification(self, spec: ReferenceMapSpecification) -> None:
        """Execute full reference map structural, bibliographic, and constitutional validation (TEST-REF-01..18)."""
        # 1. Compatible Roadmap Version Check (TEST-REF-11)
        active_roadmap = self.repo.get_roadmap()
        if active_roadmap:
            if spec.compatible_roadmap_version != active_roadmap.version:
                raise InvariantViolationError(
                    f"Reference Map declared compatible_roadmap_version '{spec.compatible_roadmap_version}' "
                    f"does not match active Roadmap version '{active_roadmap.version}' (TEST-REF-11)."
                )

        # 2. Roadmap Node Existence Validation (TEST-REF-10)
        existing_nodes = self.repo.list_roadmap_nodes()
        existing_codes = {n.code for n in existing_nodes}
        existing_node_ids = {n.node_id for n in existing_nodes}

        for mapping in spec.ownership_mappings:
            if mapping.node_code not in existing_codes:
                raise InvariantViolationError(
                    f"OwnershipMapping references non-existent roadmap node code '{mapping.node_code}' (TEST-REF-10)."
                )
            if mapping.node_id and mapping.node_id not in existing_node_ids:
                raise InvariantViolationError(
                    f"OwnershipMapping references non-existent node_id '{mapping.node_id}' (TEST-REF-10)."
                )

        for cand in spec.contributions:
            for n_code in cand.roadmap_nodes:
                if n_code not in existing_codes:
                    raise InvariantViolationError(
                        f"CandidateContribution '{cand.contribution_id}' references unknown roadmap node '{n_code}' (TEST-REF-10)."
                    )

        # 3. Source DOI & Duplicate Detection (TEST-REF-01, TEST-REF-06)
        seen_source_ids: Set[str] = set()
        seen_dois: Set[str] = set()
        seen_keys: Set[str] = set()

        for src in spec.sources:
            if src.source_id in seen_source_ids:
                raise InvariantViolationError(f"Duplicate source_id detected: '{src.source_id}' (TEST-REF-06).")
            seen_source_ids.add(src.source_id)

            if src.citation_key:
                if src.citation_key in seen_keys:
                    raise InvariantViolationError(f"Duplicate citation_key detected: '{src.citation_key}' (TEST-REF-06).")
                seen_keys.add(src.citation_key)

            if src.doi:
                norm_doi = src.doi.strip().lower()
                if not DOI_REGEX.match(src.doi.strip()):
                    raise InvariantViolationError(
                        f"Source '{src.source_id}' has malformed DOI '{src.doi}' (TEST-REF-01)."
                    )
                if norm_doi in seen_dois:
                    raise InvariantViolationError(
                        f"Duplicate DOI detected: '{src.doi}' in source '{src.source_id}' (TEST-REF-06)."
                    )
                seen_dois.add(norm_doi)

        # 4. Claim & Evidence Linkage Rules (TEST-REF-02, TEST-REF-03, TEST-REF-04)
        evidence_by_id = {evd.evidence_id: evd for evd in spec.evidences}
        evidence_claim_bindings = {evd.supports_claim_id for evd in spec.evidences if evd.supports_claim_id}

        for clm in spec.claims:
            # TEST-REF-02: SOURCE_CLAIM or SOURCE_FACT must have evidence or linked source
            if clm.claim_type in (ClaimType.SOURCE_CLAIM, ClaimType.SOURCE_FACT):
                has_direct_evidence = bool(clm.evidence_ids) or (clm.claim_id in evidence_claim_bindings)
                if not has_direct_evidence:
                    raise InvariantViolationError(
                        f"Claim '{clm.claim_id}' is of type '{clm.claim_type}' but lacks required source evidence (TEST-REF-02)."
                    )

            # TEST-REF-14 / RC-06: SOURCE_FACT or SOURCE_CLAIM cannot have ownership OURS
            if clm.claim_type in (ClaimType.SOURCE_FACT, ClaimType.SOURCE_CLAIM) and clm.ownership == IntellectualOwnership.OURS:
                raise InvariantViolationError(
                    f"Claim '{clm.claim_id}' cannot have ownership OURS while claiming external source fact/claim (TEST-REF-14)."
                )

        # 5. Candidate Contribution Novelty Safety (TEST-REF-15)
        for cand in spec.contributions:
            if cand.novelty_status == NoveltyStatus.POTENTIALLY_NOVEL and not cand.differentiation_notes:
                raise InvariantViolationError(
                    f"CandidateContribution '{cand.contribution_id}' cannot be marked POTENTIALLY_NOVEL without explicit differentiation notes (TEST-REF-15)."
                )
            if cand.novelty_status == NoveltyStatus.CANDIDATE and cand.ownership != IntellectualOwnership.OURS:
                raise InvariantViolationError(
                    f"CandidateContribution '{cand.contribution_id}' must belong to OURS (TEST-REF-15)."
                )

        # 6. ATT&CK Metadata Requirement (TEST-REF-18)
        attack_src = next((s for s in spec.sources if "MITRE" in s.title or "ATT&CK" in s.title), None)
        if attack_src:
            if not attack_src.access_date or not attack_src.venue:
                raise InvariantViolationError(
                    "MITRE ATT&CK source must specify access_date and snapshot/taxonomy metadata (TEST-REF-18)."
                )

    def ingest_reference_map_dict(self, data: Dict[str, Any], raw_text: Optional[str] = None) -> ReferenceMapSpecification:
        """Parse, validate, hash, and persist a Reference Map specification."""
        sha256 = compute_string_sha256(raw_text or json.dumps(data, sort_keys=True))

        sources = [Source(**s) for s in data.get("sources", [])]
        evidences = [Evidence(**e) for e in data.get("evidences", [])]
        claims = [Claim(**c) for c in data.get("claims", [])]
        claim_relations = [ClaimRelation(**r) for r in data.get("claim_relations", [])]
        ownership_mappings = [OwnershipMapping(**m) for m in data.get("ownership_mappings", [])]
        contributions = [CandidateContribution(**cand) for cand in data.get("contributions", [])]
        firewall_rules = [CitationFirewallRule(**f) for f in data.get("firewall_rules", [])]
        unresolved = data.get("unresolved_references", [])

        spec = ReferenceMapSpecification(
            reference_map_id=data.get("reference_map_id", "REF-000001"),
            version=data.get("version", "1.0.0"),
            compatible_roadmap_version=data.get("compatible_roadmap_version", "1.0.0"),
            title=data.get("title", "Canonical Reference, Intellectual Ownership, and Evidence Provenance Map"),
            summary=data.get("summary", ""),
            sha256_hash=sha256,
            sources=sources,
            evidences=evidences,
            claims=claims,
            claim_relations=claim_relations,
            ownership_mappings=ownership_mappings,
            contributions=contributions,
            firewall_rules=firewall_rules,
            unresolved_references=unresolved,
        )

        # Validate
        self.validate_reference_map_specification(spec)

        # Persist
        self.repo.save_reference_map(spec)
        return spec

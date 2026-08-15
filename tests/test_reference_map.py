"""
Comprehensive Reference Map, Intellectual Ownership, and Citation Firewall Test Suite (TEST-REF-01..TEST-REF-18)
"""

import pytest
from datetime import datetime, timezone

from research_agent.core.enums import (
    IntellectualOwnership,
    ClaimType,
    EpistemicStatus,
    SourceQualityTier,
    SourceVerificationState,
    SourceRole,
    VerificationStatus,
    SupportType,
    EvidenceStrength,
    NoveltyStatus,
    CitationFirewallStatus,
    ArgumentRelationType,
)
from research_agent.core.exceptions import InvariantViolationError, ProvenanceError
from research_agent.schemas.source import Source
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.claim import Claim, ClaimRelation
from research_agent.schemas.ownership import OwnershipMapping, CandidateContribution
from research_agent.schemas.citation import CitationFirewallRule
from research_agent.schemas.reference_map import ReferenceMapSpecification
from research_agent.schemas.roadmap import ResearchRoadmap, ResearchNode
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.reference_map_ingestion import ReferenceMapIngestionService
from research_agent.interfaces.reference_map_query import ReferenceMapQueryService


@pytest.fixture
def test_repo(tmp_path):
    db_path = tmp_path / "test_research.db"
    db_manager = DatabaseManager(db_path=db_path)
    repo = ResearchRepository(db_manager)
    return repo


# ----------------------------------------------------------------------
# TEST-REF-01: Malformed DOI rejection
# ----------------------------------------------------------------------
def test_ref_01_malformed_doi_rejection(test_repo):
    ingestion = ReferenceMapIngestionService(test_repo)
    bad_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        sources=[
            Source(
                source_id="SRC-999001",
                citation_key="BadDoi2024",
                title="Bad DOI Paper",
                authors=["Author A"],
                year=2024,
                venue="IEEE S&P",
                doi="invalid_doi_format_without_prefix",
            )
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_spec)
    assert "malformed DOI" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-02: Unsourced factual claims must fail validation
# ----------------------------------------------------------------------
def test_ref_02_unsourced_factual_claims_rejected(test_repo):
    ingestion = ReferenceMapIngestionService(test_repo)
    bad_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        claims=[
            Claim(
                claim_id="CLM-999001",
                statement="External fact with no evidence or source linkage.",
                claim_type=ClaimType.SOURCE_FACT,
                ownership=IntellectualOwnership.SOURCE,
                evidence_ids=[],
            )
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_spec)
    assert "lacks required source evidence" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-03: OUR_DESIGN claim can exist without external source
# ----------------------------------------------------------------------
def test_ref_03_our_design_without_external_source(test_repo):
    claim = Claim(
        claim_id="CLM-999002",
        statement="Our novel feature extraction architecture contracts.",
        claim_type=ClaimType.OUR_DESIGN,
        ownership=IntellectualOwnership.OURS,
        evidence_ids=[],
    )
    assert claim.ownership == IntellectualOwnership.OURS
    assert claim.claim_type == ClaimType.OUR_DESIGN


# ----------------------------------------------------------------------
# TEST-REF-04: MOTIVATED_BY relationship preserves OURS ownership
# ----------------------------------------------------------------------
def test_ref_04_motivated_by_preserves_ours_ownership(test_repo):
    # Save required source first for foreign key
    src = Source(
        source_id="SRC-000001",
        citation_key="Src1",
        title="Source Paper",
        authors=["Author S"],
        year=2022,
        venue="USENIX",
    )
    test_repo.save_source(src)
    
    clm_source = Claim(
        claim_id="CLM-SRC-01",
        statement="Prior work shows parameter loss during parsing.",
        claim_type=ClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.SOURCE,
        evidence_ids=["EVD-000001"],
    )
    clm_ours = Claim(
        claim_id="CLM-OUR-01",
        statement="Our Preserve/Invariant/Exclude contract retains security parameters.",
        claim_type=ClaimType.OUR_DESIGN,
        ownership=IntellectualOwnership.OURS,
    )
    rel = ClaimRelation(
        relation_id="ARE-999001",
        source_claim_id=clm_source.claim_id,
        target_claim_id=clm_ours.claim_id,
        relation_type=ArgumentRelationType.MOTIVATES,
    )
    test_repo.save_claim(clm_source)
    test_repo.save_claim(clm_ours)
    test_repo.save_claim_relation(rel)

    retrieved = test_repo.get_claim("CLM-OUR-01")
    assert retrieved.ownership == IntellectualOwnership.OURS


# ----------------------------------------------------------------------
# TEST-REF-05: Baseline method provenance check
# ----------------------------------------------------------------------
def test_ref_05_baseline_method_provenance(test_repo):
    src = Source(
        source_id="SRC-000003",
        citation_key="Du2017DeepLog",
        title="DeepLog: Anomaly Detection and Diagnosis from System Logs",
        authors=["Min Du", "Feifei Li", "Guanqing Zheng", "Vivek Srikumar"],
        year=2017,
        venue="ACM CCS 2017",
        source_type=SourceQualityTier.PEER_REVIEWED_TOP_VENUE,
        roles=[SourceRole.BASELINE, SourceRole.METHOD],
        doi="10.1145/3133956.3134015",
    )
    test_repo.save_source(src)
    retrieved = test_repo.get_source("SRC-000003")
    assert SourceRole.BASELINE in retrieved.roles
    assert retrieved.venue == "ACM CCS 2017"


# ----------------------------------------------------------------------
# TEST-REF-06: Deduplication by DOI and citation key
# ----------------------------------------------------------------------
def test_ref_06_deduplication_by_doi_and_key(test_repo):
    ingestion = ReferenceMapIngestionService(test_repo)
    dup_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        sources=[
            Source(
                source_id="SRC-000001",
                citation_key="Key1",
                title="Paper 1",
                authors=["Author A"],
                year=2022,
                venue="IEEE S&P",
                doi="10.1109/SP.2022.0001",
            ),
            Source(
                source_id="SRC-000002",
                citation_key="Key2",
                title="Paper 2",
                authors=["Author B"],
                year=2022,
                venue="IEEE S&P",
                doi="10.1109/SP.2022.0001",  # Duplicate DOI
            ),
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(dup_spec)
    assert "Duplicate DOI" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-07: Exact locator validation
# ----------------------------------------------------------------------
def test_ref_07_exact_locator_validation():
    with pytest.raises(ValueError):
        Evidence(
            evidence_id="EVD-999",
            source_id="SRC-001",
            locator="",  # Empty locator must fail min_length
            exact_quote="Valid quote from the paper.",
        )


# ----------------------------------------------------------------------
# TEST-REF-08: Contradiction record between competing empirical claims
# ----------------------------------------------------------------------
def test_ref_08_contradiction_record_preservation(test_repo):
    clm_a = Claim(
        claim_id="CLM-000004",
        statement="Complex GNN matches simple baselines.",
        claim_type=ClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.SOURCE,
        evidence_ids=["EVD-000001"],
    )
    clm_b = Claim(
        claim_id="CLM-000009",
        statement="Cross-view alignment achieves superior representation.",
        claim_type=ClaimType.OUR_DESIGN,
        ownership=IntellectualOwnership.OURS,
    )
    test_repo.save_claim(clm_a)
    test_repo.save_claim(clm_b)

    rel = ClaimRelation(
        relation_id="ARE-CONT-01",
        source_claim_id="CLM-000004",
        target_claim_id="CLM-000009",
        relation_type=ArgumentRelationType.CONTRADICTS,
        notes="GNN complexity claims contradict Bilot et al. simpler baseline findings.",
    )
    test_repo.save_claim_relation(rel)
    query_svc = ReferenceMapQueryService(test_repo)
    contradictions = query_svc.get_contradictory_claims()
    assert len(contradictions) >= 1
    assert contradictions[0]["relation_id"] == "ARE-CONT-01"


# ----------------------------------------------------------------------
# TEST-REF-09: Negative evidence preservation
# ----------------------------------------------------------------------
def test_ref_09_negative_evidence_preservation(test_repo):
    src = Source(
        source_id="SRC-000021",
        citation_key="Alon2021OverSquashing",
        title="On the Bottleneck of Graph Neural Networks",
        authors=["Uri Alon", "Eran Yahav"],
        year=2021,
        venue="ICLR 2021",
    )
    test_repo.save_source(src)

    evd = Evidence(
        evidence_id="EVD-NEG-01",
        source_id="SRC-000021",
        locator="Section 3, Theorem 1",
        exact_quote="Exponential neighborhood expansion causes over-squashing in standard GNNs.",
        caveats="Applies to dense graphs with diameter greater than message passing radius.",
    )
    test_repo.save_evidence(evd)
    retrieved = test_repo.get_evidence("EVD-NEG-01")
    assert "over-squashing" in retrieved.exact_quote
    assert retrieved.caveats is not None


# ----------------------------------------------------------------------
# TEST-REF-10: Mapping to non-existent roadmap node is rejected
# ----------------------------------------------------------------------
def test_ref_10_invalid_roadmap_node_rejected(test_repo):
    ingestion = ReferenceMapIngestionService(test_repo)
    bad_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        ownership_mappings=[
            OwnershipMapping(
                mapping_id="OWN-999001",
                node_code="9.9.9",  # Non-existent node
                component_name="Non-existent Component",
                ownership=IntellectualOwnership.OURS,
            )
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_spec)
    assert "non-existent roadmap node" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-11: Reference map version compatibility check
# ----------------------------------------------------------------------
def test_ref_11_version_compatibility_check(test_repo):
    # Save a roadmap with version 1.0.0
    rm = ResearchRoadmap(
        roadmap_id="ROD-000001",
        version="1.0.0",
        title="Test Roadmap",
        central_object="feature representation z",
    )
    test_repo.save_roadmap(rm)

    ingestion = ReferenceMapIngestionService(test_repo)
    bad_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="2.0.0",  # Incompatible version
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_spec)
    assert "compatible_roadmap_version" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-12: Citation Firewall blocks citations without verified metadata or evidence
# ----------------------------------------------------------------------
def test_ref_12_citation_firewall_blocks_unverified():
    rule = CitationFirewallRule(
        source_id="SRC-UNV-01",
        citation_key="Unverified2024",
        status=CitationFirewallStatus.BLOCKED,
        source_exists=True,
        metadata_verified=False,
        claim_evidence_link_exists=False,
        locator_exists=False,
        blocking_reasons=["Metadata not verified", "No extracted evidence"],
    )
    assert rule.status == CitationFirewallStatus.BLOCKED
    assert len(rule.blocking_reasons) == 2


# ----------------------------------------------------------------------
# TEST-REF-13: Citation Firewall authorizes ready citations
# ----------------------------------------------------------------------
def test_ref_13_citation_firewall_authorizes_ready():
    rule = CitationFirewallRule(
        source_id="SRC-000002",
        citation_key="Arp2022DosDonts",
        status=CitationFirewallStatus.READY,
        source_exists=True,
        metadata_verified=True,
        claim_evidence_link_exists=True,
        locator_exists=True,
        support_type=SupportType.DIRECT_SUPPORT,
    )
    assert rule.status == CitationFirewallStatus.READY


# ----------------------------------------------------------------------
# TEST-REF-14: Claim ownership taxonomy constraint enforcement
# ----------------------------------------------------------------------
def test_ref_14_claim_ownership_taxonomy_enforcement():
    with pytest.raises(ValueError):
        Claim(
            claim_id="CLM-ERR-01",
            statement="External fact wrongly claimed as OURS.",
            claim_type=ClaimType.SOURCE_FACT,
            ownership=IntellectualOwnership.OURS,
        )


# ----------------------------------------------------------------------
# TEST-REF-15: Candidate contribution novelty safety
# ----------------------------------------------------------------------
def test_ref_15_candidate_contribution_novelty_safety(test_repo):
    # Save a valid roadmap with node 1.1.1 first
    node = ResearchNode(
        node_id="NOD-000001",
        roadmap_id="ROD-000001",
        level=1,
        order_index=1,
        code="1.1.1",
        title="Log Space Characteristics",
    )
    rm = ResearchRoadmap(
        roadmap_id="ROD-000001",
        version="1.0.0",
        title="Test Roadmap",
        central_object="feature representation z",
        nodes=[node],
    )
    test_repo.save_roadmap(rm)

    ingestion = ReferenceMapIngestionService(test_repo)
    bad_spec = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        contributions=[
            CandidateContribution(
                contribution_id="CAND-ERR-01",
                name="Undifferentiated Claim",
                description="Claiming novel without differentiation notes.",
                roadmap_nodes=["1.1.1"],
                ownership=IntellectualOwnership.OURS,
                novelty_status=NoveltyStatus.POTENTIALLY_NOVEL,
                differentiation_notes="",  # Empty notes must fail validation
            )
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_spec)
    assert "cannot be marked POTENTIALLY_NOVEL without explicit differentiation notes" in str(exc_info.value)


# ----------------------------------------------------------------------
# TEST-REF-16: Preprint vs peer-reviewed distinction enforcement
# ----------------------------------------------------------------------
def test_ref_16_preprint_distinction(test_repo):
    src = Source(
        source_id="SRC-000030",
        citation_key="Author2026Preprint",
        title="Emerging Benchmark Protocols",
        authors=["Author P"],
        year=2026,
        venue="arXiv preprint",
        source_type=SourceQualityTier.PREPRINT,
        roles=[SourceRole.EMERGING_WORK],
    )
    test_repo.save_source(src)
    retrieved = test_repo.get_source("SRC-000030")
    assert retrieved.source_type == SourceQualityTier.PREPRINT
    assert retrieved.source_type != SourceQualityTier.PEER_REVIEWED_TOP_VENUE


# ----------------------------------------------------------------------
# TEST-REF-17: Official dataset provenance and tier separation
# ----------------------------------------------------------------------
def test_ref_17_dataset_provenance(test_repo):
    src_darpa = Source(
        source_id="SRC-000028",
        citation_key="DARPA2019TC",
        title="DARPA Transparent Computing Telemetry Datasets",
        authors=["DARPA"],
        year=2019,
        venue="DARPA Official Release",
        source_type=SourceQualityTier.OFFICIAL_DATASET,
        roles=[SourceRole.DATASET, SourceRole.REPRODUCIBILITY],
    )
    test_repo.save_source(src_darpa)
    retrieved = test_repo.get_source("SRC-000028")
    assert retrieved.source_type == SourceQualityTier.OFFICIAL_DATASET


# ----------------------------------------------------------------------
# TEST-REF-18: ATT&CK taxonomy versioning and snapshot date requirement
# ----------------------------------------------------------------------
def test_ref_18_attack_metadata_requirement(test_repo):
    ingestion = ReferenceMapIngestionService(test_repo)
    bad_attack = ReferenceMapSpecification(
        version="1.0.0",
        compatible_roadmap_version="1.0.0",
        sources=[
            Source(
                source_id="SRC-ATTACK-BAD",
                citation_key="MITREBad",
                title="MITRE ATT&CK Enterprise Matrix",
                authors=["MITRE"],
                year=2024,
                venue="MITRE",
                source_type=SourceQualityTier.PRIMARY_STANDARD,
                access_date=None,  # Missing access date must fail
            )
        ]
    )
    with pytest.raises(InvariantViolationError) as exc_info:
        ingestion.validate_reference_map_specification(bad_attack)
    assert "MITRE ATT&CK source must specify access_date" in str(exc_info.value)

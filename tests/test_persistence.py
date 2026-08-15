"""
Tests for Persistence Layer and Disposable Derived Indexes (TEST 9, ADR-0001, ADR-0004)
"""

from pathlib import Path
from research_agent.config import WorkspaceConfig
from research_agent.core.identifiers import EntityPrefix, validate_stable_id
from research_agent.core.enums import ClaimType, IntellectualOwnership, EpistemicStatus
from research_agent.schemas import Claim, Source, Evidence
from research_agent.storage.repository import ResearchRepository
from research_agent.storage.file_store import CanonicalFileStore
from research_agent.interfaces.roadmap_ingestion import RoadmapIngestionService


def test_invariant_9_derived_indexes_disposable(temp_workspace: WorkspaceConfig, repository: ResearchRepository, file_store: CanonicalFileStore):
    """TEST 9: Derived indexes and caches can be deleted while canonical database/artifacts remain intact (RC-17)."""
    # 1. Store canonical claim in DB
    claim = Claim(
        claim_id="CLM-000001",
        statement="Log sequences have non-stationary transition dynamics.",
        claim_type=ClaimType.OUR_INFERENCE,
        ownership=IntellectualOwnership.OURS,
        epistemic_status=EpistemicStatus.SUPPORTED,
    )
    repository.save_claim(claim)

    # 2. Write a canonical document
    _, doc_hash = file_store.write_text("sources/manifests/test_manifest.yaml", "sources: []")

    # 3. Simulate derived cache and vector index files
    cache_file, _ = file_store.write_text("runtime/cache/query_cache_001.json", '{"cached": true}')
    index_file, _ = file_store.write_text("runtime/indexes/bm25_chunk_index.bin", "BINARY_VECTOR_BLOB")

    assert cache_file.exists()
    assert index_file.exists()

    # 4. Purge all derived indexes and caches
    cache_purged, index_purged = file_store.purge_derived_indexes()
    assert cache_purged >= 1
    assert index_purged >= 1

    # 5. Verify derived files are gone
    assert not cache_file.exists()
    assert not index_file.exists()

    # 6. Verify CANONICAL DATA is 100% intact
    reloaded_claim = repository.get_claim("CLM-000001")
    assert reloaded_claim is not None
    assert reloaded_claim.statement == claim.statement

    manifest_content = file_store.read_text("sources/manifests/test_manifest.yaml")
    assert manifest_content == "sources: []"


def test_stable_id_sequential_allocation(repository: ResearchRepository):
    """Verify that stable IDs are generated monotonically with standard formatting."""
    src1 = repository.next_id(EntityPrefix.SOURCE)
    src2 = repository.next_id(EntityPrefix.SOURCE)
    clm1 = repository.next_id(EntityPrefix.CLAIM)

    assert src1 == "SRC-000001"
    assert src2 == "SRC-000002"
    assert clm1 == "CLM-000001"
    assert validate_stable_id(src1, EntityPrefix.SOURCE)
    assert validate_stable_id(clm1, EntityPrefix.CLAIM)


def test_roadmap_ingestion_preserves_hierarchy(repository: ResearchRepository):
    """Verify that Roadmap ingestion preserves hierarchy, RQ, and Hypotheses."""
    service = RoadmapIngestionService(repository)
    sample_roadmap = {
        "roadmap_id": "ROD-000001",
        "version": "1.0.0",
        "title": "Roadmap: Log Representation Under Evasion Constraints",
        "summary": "Formal study of feature representation z for log data.",
        "nodes": [
            {
                "node_id": "NOD-000001",
                "parent_node_id": None,
                "level": 1,
                "order_index": 1,
                "code": "1.0",
                "title": "Introduction and Representation Problem Statement",
                "expected_outputs": ["Representation boundary formal definition"],
                "rq_ids": ["RQ-000001"],
                "hyp_ids": ["HYP-000001"],
            }
        ],
        "questions": [
            {
                "rq_id": "RQ-000001",
                "code": "RQ1",
                "title": "How does template-free tokenization affect representation entropy under unseen log formats?",
                "description": "Evaluation of vocabulary shift resistance",
                "target_representation_aspect": "Vocabulary entropy & shift resistance",
            }
        ],
        "hypotheses": [
            {
                "hyp_id": "HYP-000001",
                "code": "H1",
                "rq_id": "RQ-000001",
                "statement": "Sub-character byte-pair representations maintain bounded representation error under zero-day formats.",
                "falsification_criteria": "Representation distance delta > 3.0 sigma relative to baseline.",
            }
        ]
    }

    roadmap = service.ingest_roadmap_dict(sample_roadmap)
    assert roadmap.roadmap_id == "ROD-000001"
    assert len(roadmap.nodes) == 1
    assert len(roadmap.questions) == 1
    assert len(roadmap.hypotheses) == 1
    assert roadmap.sha256_hash is not None

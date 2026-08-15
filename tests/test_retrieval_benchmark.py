"""
Hybrid Retrieval Deterministic Benchmark Test (Prompt 4, Section 58)
"""

import pytest
from pathlib import Path
from research_agent.config import get_default_config
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.memory.manager import MemoryManager


@pytest.fixture(scope="module")
def prod_memory_mgr():
    config = get_default_config()
    db_mgr = DatabaseManager(config=config)
    repo = ResearchRepository(db_mgr)
    mgr = MemoryManager(repository=repo)
    # Ensure indexes are freshly built
    mgr.rebuild_indexes()
    return mgr


# ----------------------------------------------------------------------
# BENCHMARK-01: Query "shortcut learning"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_shortcut_learning(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("shortcut learning in evaluation baselines")
    all_returned_ids = (
        [e.get("claim_id") or e.get("source_id") or e.get("node_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Must retrieve CLM-000008 (Representation Contract) or CLM-000004 (Bilot baseline finding)
    assert any(cid in ["CLM-000008", "CLM-000004", "SRC-000016"] for cid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-02: Query "privacy leakage"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_privacy_leakage(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("privacy leakage membership inference attacks")
    all_returned_ids = (
        [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Must retrieve Shokri (SRC-000025) or Fredrikson (SRC-000026)
    assert any(sid in ["SRC-000025", "SRC-000026"] for sid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-03: Query "over-squashing"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_oversquashing(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("over-squashing bottleneck in graph neural networks")
    all_returned_ids = [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities]
    # Must retrieve Alon & Yahav (SRC-000021)
    assert any(sid == "SRC-000021" for sid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-04: Query "simple baseline"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_simple_baselines(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("simple baseline outperforms complex detectors")
    all_returned_ids = (
        [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Must retrieve Bilot et al. (SRC-000016) or CLM-000004
    assert any(sid in ["SRC-000016", "CLM-000004"] for sid in all_returned_ids)

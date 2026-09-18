"""
Kiểm tra điểm chuẩn xác định truy xuất kết hợp (Dấu Prompt 4, Mục 58)
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
    # Đảm bảo các chỉ mục được xây dựng mới
    mgr.rebuild_indexes()
    return mgr


# ----------------------------------------------------------------------
# BENCHMARK-01: Truy vấn "học shortcut"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_shortcut_learning(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("shortcut learning in evaluation baselines")
    all_returned_ids = (
        [e.get("claim_id") or e.get("source_id") or e.get("node_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Phải truy xuất CLM-000008 (Hợp đồng đại diện) hoặc CLM-000004 (Phát hiện baseline Bilot)
    assert any(cid in ["CLM-000008", "CLM-000004", "SRC-000016"] for cid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-02: Truy vấn "rò rỉ quyền riêng tư"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_privacy_leakage(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("privacy leakage membership inference attacks")
    all_returned_ids = (
        [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Phải truy xuất Shokri (SRC-000025) hoặc Fredrikson (SRC-000026)
    assert any(sid in ["SRC-000025", "SRC-000026"] for sid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-03: Truy vấn "đè bẹp quá mức"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_oversquashing(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("over-squashing bottleneck in graph neural networks")
    all_returned_ids = [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities]
    # Phải truy xuất Alon & Yahav (SRC-000021)
    assert any(sid == "SRC-000021" for sid in all_returned_ids)


# ----------------------------------------------------------------------
# BENCHMARK-04: Truy vấn "baseline đơn giản"
# ----------------------------------------------------------------------
def test_retrieval_benchmark_simple_baselines(prod_memory_mgr):
    bundle = prod_memory_mgr.retrieve("simple baseline outperforms complex detectors")
    all_returned_ids = (
        [e.get("source_id") or e.get("claim_id") for e in bundle.canonical_entities] +
        [f.get("claim_id") for f in bundle.verified_facts]
    )
    # Phải truy xuất Bilot et al. (SRC-000016) hoặc CLM-000004
    assert any(sid in ["SRC-000016", "CLM-000004"] for sid in all_returned_ids)

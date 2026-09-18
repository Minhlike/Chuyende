"""
Đặc tả lộ trình nghiên cứu Canonical và các thử nghiệm bất biến (TEST-RM-01..16)
"""

import json
from pathlib import Path
import pytest
import yaml

from research_agent.config import get_default_config
from research_agent.core.exceptions import InvariantViolationError
from research_agent.schemas.roadmap import (
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
)
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.roadmap_ingestion import RoadmapIngestionService
from research_agent.interfaces.roadmap_query import RoadmapQueryService


@pytest.fixture
def repo():
    config = get_default_config()
    db_manager = DatabaseManager(config=config)
    return ResearchRepository(db_manager)


@pytest.fixture
def query_service(repo):
    return RoadmapQueryService(repo)


def test_rm_01_node_parent_validity(query_service):
    """TEST-RM-01: Mọi nút có parent_node_id đều tham chiếu đến một nút hợp lệ hiện có."""
    nodes = query_service.get_roadmap().nodes
    node_ids = {n.node_id for n in nodes}
    for node in nodes:
        if node.parent_node_id:
            assert node.parent_node_id in node_ids, f"Node {node.code} references unknown parent {node.parent_node_id}"


def test_rm_02_no_duplicate_codes(query_service):
    """TEST-RM-02: Mỗi mã nút và node_id là duy nhất trên toàn bộ cây."""
    nodes = query_service.get_roadmap().nodes
    node_ids = [n.node_id for n in nodes]
    node_codes = [n.code for n in nodes]
    assert len(node_ids) == len(set(node_ids)), "Duplicate node_id found"
    assert len(node_codes) == len(set(node_codes)), "Duplicate section code found"


def test_rm_03_unique_rqs(query_service):
    """TEST-RM-03: Chính xác 5 câu hỏi nghiên cứu chính tắc (RQ1..RQ5) đã được đăng ký."""
    rqs = query_service.repo.list_research_questions()
    codes = {q.code for q in rqs}
    assert codes == {"RQ1", "RQ2", "RQ3", "RQ4", "RQ5"}
    for q in rqs:
        assert q.canonical_wording_en
        assert q.canonical_wording_vi
        assert q.target_representation_aspect


def test_rm_04_unique_hypotheses(query_service):
    """TEST-RM-04: Chính xác 5 giả thuyết kinh điển (H1..H5) với tiêu chí giả mạo rõ ràng."""
    hyps = query_service.repo.list_hypotheses()
    codes = {h.code for h in hyps}
    assert codes == {"H1", "H2", "H3", "H4", "H5"}
    for h in hyps:
        assert h.statement
        assert h.falsification_criteria
        assert h.rq_id.startswith("RQ-")


def test_rm_05_rq_ch1_ch2_ch3_traceability(query_service):
    """TEST-RM-05: Mỗi RQ đều theo dõi ít ​​nhất một Khoảng trống trong Ch1, Cơ chế trong Ch2 và Đánh giá trong Ch3."""
    traceability = query_service.repo.get_traceability_matrix()
    assert len(traceability) == 5
    for tr in traceability:
        assert len(tr.chapter1_gap_nodes) >= 1, f"{tr.code} missing Chapter 1 gap nodes"
        assert len(tr.chapter2_mechanism_nodes) >= 1, f"{tr.code} missing Chapter 2 mechanism nodes"
        assert len(tr.chapter3_evaluation_nodes) >= 1, f"{tr.code} missing Chapter 3 evaluation nodes"
        assert len(tr.hypothesis_ids) >= 1, f"{tr.code} missing linked hypotheses"


def test_rm_06_hypothesis_test_relations(query_service):
    """TEST-RM-06: Mọi giả thuyết đều được kiểm tra trong phần đánh giá của Chương 3."""
    hyps = query_service.repo.list_hypotheses()
    for h in hyps:
        nodes = query_service.get_nodes_testing_hypothesis(h.hyp_id)
        assert len(nodes) >= 1, f"Hypothesis {h.code} has no associated evaluation nodes in roadmap"


def test_rm_07_representation_contract_categories(query_service):
    """TEST-RM-07: Hợp đồng đại diện bao gồm các danh mục PRESERVE, INVARIANT và EXCLUDE."""
    contract = query_service.repo.get_representation_contract()
    assert contract is not None
    assert len(contract.preserve) >= 3
    assert len(contract.invariant) >= 2
    assert len(contract.exclude) >= 3


def test_rm_08_central_object_representation_z(query_service):
    """TEST-RM-08: Đối tượng nghiên cứu trung tâm hoàn toàn là biểu diễn tính năng z, không phải máy dò/IDS."""
    roadmap = query_service.get_roadmap()
    assert "feature representation z" in roadmap.central_object
    b4 = query_service.get_boundary_constraints("Detector Score")
    assert len(b4) >= 1


def test_rm_09_att_ck_non_linear_evidence_space(query_service):
    """TEST-RM-09: MITRE ATT&CK được mô hình hóa dưới dạng bằng chứng hành vi phi tuyến tính, không phải trạng thái tuyến tính."""
    b2 = query_service.get_boundary_constraints("ATT&CK")
    assert len(b2) >= 1
    assert "linear" in b2[0].statement.lower() or "state" in b2[0].statement.lower()

    node_1121 = query_service.get_node("1.1.2.1")
    assert node_1121 is not None
    assert "tuyến tính" in node_1121.title or "linear" in str(node_1121.methodological_constraints).lower()


def test_rm_10_provenance_dependency_non_causal(query_service):
    """TEST-RM-10: Sự phụ thuộc vào xuất xứ rõ ràng không được coi là có quan hệ nhân quả."""
    b3 = query_service.get_boundary_constraints("Dependency")
    assert len(b3) >= 1
    assert "causal" in b3[0].statement.lower()

    node_1232 = query_service.get_node("1.2.3.2")
    assert node_1232 is not None
    assert any("causal" in c for c in node_1232.methodological_constraints)


def test_rm_11_idempotent_ingestion(repo):
    """TEST-RM-11: Nhập lộ trình nhiều lần sẽ tạo ra trạng thái ổn định không trùng lặp."""
    ingestion = RoadmapIngestionService(repo)
    config = get_default_config()
    with open(config.roadmap_specs_dir / "roadmap.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Nhập 1
    r1 = ingestion.ingest_roadmap_dict(data)
    # Nhập 2
    r2 = ingestion.ingest_roadmap_dict(data)

    assert r1.roadmap_id == r2.roadmap_id
    assert r1.sha256_hash == r2.sha256_hash
    assert len(repo.list_roadmap_nodes()) == len(r1.nodes)
    assert len(repo.list_research_questions()) == 5
    assert len(repo.list_hypotheses()) == 5


def test_rm_12_exact_canonical_wording_preserved(query_service):
    """TEST-RM-12: Tiêu đề và mã chuẩn khớp chính xác với thông số nhắc nhở."""
    node_ch1 = query_service.get_node("1.0")
    node_ch2 = query_service.get_node("2.0")
    node_ch3 = query_service.get_node("3.0")

    assert "TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG" in node_ch1.title
    assert "ĐỀ XUẤT PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG ĐA VIEW" in node_ch2.title
    assert "THỰC NGHIỆM, ĐÁNH GIÁ VÀ ỨNG DỤNG" in node_ch3.title


def test_rm_13_negative_results_pathways_enabled(query_service):
    """TEST-RM-13: Thất bại và kết quả tiêu cực được công nhận là kết quả khoa học hợp lệ."""
    b10 = query_service.get_boundary_constraints("Negative Results")
    assert len(b10) >= 1

    node_neg = query_service.get_node("3.4.3.5")
    assert node_neg is not None
    assert "Negative Results" in node_neg.title or "Failure" in node_neg.title


def test_rm_14_tier_a_vs_tier_b_distinction(query_service):
    """TEST-RM-14: Cấp A bị hạn chế là không đủ cho ngữ nghĩa tấn công mạng."""
    b1 = query_service.get_boundary_constraints("Tier A")
    assert len(b1) >= 1

    node_t_a = query_service.get_node("3.1.2.1")
    assert node_t_a is not None
    assert "TIER A" in node_t_a.title


def test_rm_15_intrinsic_probe_operational_order(query_service):
    """TEST-RM-15: Thứ tự đánh giá giữ nguyên Nội tại -> Thăm dò -> Vận hành."""
    node_eval = query_service.get_node("3.1.3.1")
    assert node_eval is not None
    assert "Intrinsic -> Probe -> Operational" in node_eval.title

    n_intrinsic = query_service.get_node("3.1.3.1.1")
    n_probe = query_service.get_node("3.1.3.1.2")
    n_op = query_service.get_node("3.1.3.1.3")
    assert n_intrinsic is not None
    assert n_probe is not None
    assert n_op is not None


def test_rm_16_no_fabricated_source_references(repo):
    """TEST-RM-16: Không có thực thể Nguồn giả mạo nào; tất cả các nguồn được xác minh."""
    sources = repo.list_sources()
    # All ingested sources must have verified status and valid non-empty venue/title
    for s in sources:
        assert s.verification_status.value == "VERIFIED"
        assert len(s.title) > 3
        assert len(s.authors) >= 1
        assert len(s.venue) >= 1


def test_rm_cli_validation_exit_code_zero(repo):
    """TEST-RM-17: Xác thực CLI trả về mã thoát 0 trên lộ trình chuẩn hợp lệ."""
    from research_agent.cli import validate_roadmap_command
    exit_code = validate_roadmap_command(repo)
    assert exit_code == 0


def test_rm_query_axes_and_controls(query_service):
    """TEST-RM-18: Dịch vụ truy vấn truy xuất chính xác các câu hỏi về trục, điều khiển và khả năng phòng thủ."""
    a1_nodes = query_service.get_nodes_by_axis("A1")
    assert len(a1_nodes) >= 3

    leak_controls = query_service.get_controls_by_category("LEAKAGE")
    assert len(leak_controls) >= 1
    assert leak_controls[0].control_id == "CTRL-LEAK-001"

    dqs = query_service.repo.list_defensibility_questions()
    assert len(dqs) == 10

    boundaries = query_service.repo.list_research_boundaries()
    assert len(boundaries) == 10

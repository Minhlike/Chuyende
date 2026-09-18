"""
Các thử nghiệm về Bất biến Hiến pháp Nghiên cứu Cốt lõi (RC-01..RC-18)
"""

import pytest
from pydantic import ValidationError
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    EquationType,
    ExperimentStatus,
    VerificationStatus,
)
from research_agent.core.exceptions import ProvenanceError, InvariantViolationError
from research_agent.schemas import (
    Claim,
    Equation,
    SymbolDefinition,
    FigureArtifact,
    TableArtifact,
    Experiment,
    ExperimentRun,
    Source,
    Evidence,
)
from research_agent.storage.repository import ResearchRepository


def test_invariant_1_invalid_claim_type_rejected():
    """TEST 1: Khiếu nại không có claim_type hợp lệ sẽ bị từ chối nghiêm ngặt."""
    with pytest.raises(ValidationError):
        Claim(
            claim_id="CLM-000001",
            statement="Log templates exhibit power-law frequency distributions.",
            claim_type="INVALID_TYPE",  # Giá trị enum không hợp lệ
            ownership=IntellectualOwnership.SOURCE,
        )


def test_invariant_2_invalid_ownership_rejected():
    """TEST 2: Khiếu nại không có quyền sở hữu hợp lệ sẽ bị từ chối nghiêm ngặt."""
    with pytest.raises(ValidationError):
        Claim(
            claim_id="CLM-000002",
            statement="Our novel representation achieves lower perplexity.",
            claim_type=ClaimType.OUR_DESIGN,
            ownership="INVALID_OWNERSHIP",  # Giá trị enum không hợp lệ
        )


def test_invariant_3_source_equation_without_provenance_rejected():
    """TEST 3: SOURCE_EQUATION không có nguồn gốc (provenance) (source_id) bị từ chối nghiêm ngặt (RC-08)."""
    with pytest.raises((ProvenanceError, ValidationError)):
        Equation(
            equation_id="EQ-000001",
            latex=r"P(w_t | w_{t-1}, \dots) = \mathrm{softmax}(W h_t)",
            equation_type=EquationType.SOURCE_EQUATION,
            source_id=None,  # Thiếu source_id cho SOURCE_EQUATION
        )


def test_invariant_4_experiment_result_without_run_id_rejected():
    """TEST 4: Xác nhận quyền sở hữu EXPERIMENT_RESULT không có ID ExperimentRun bị từ chối nghiêm ngặt (RC-02)."""
    with pytest.raises((ProvenanceError, ValidationError)):
        Claim(
            claim_id="CLM-000003",
            statement="The proposed BiLSTM representation achieved an F1-score of 0.962 on BGL.",
            claim_type=ClaimType.EXPERIMENT_RESULT,
            ownership=IntellectualOwnership.OURS,
            experiment_run_id=None,  # Thiếu yêu cầu experiment_run_id
        )


def test_invariant_5_figure_without_provenance_rejected():
    """TEST 5: Hình có đầu ra thử nghiệm số không có dữ liệu/xuất xứ lần chạy bị từ chối (RC-09)."""
    with pytest.raises((ProvenanceError, ValidationError)):
        FigureArtifact(
            figure_id="FIG-000001",
            title="t-SNE Projection of Latent Vectors",
            caption="Comparison of normal and anomalous representations",
            file_rel_path="artifacts/figures/tsne.svg",
            is_numerical_result=True,
            dataset_id=None,  # Thiếu dataset_id
            experiment_run_ids=[],  # Thiếu lượt chạy
            output_sha256="abc123def456",
        )


def test_invariant_5b_table_without_provenance_rejected():
    """TEST 5b: Bảng chứa kết quả thử nghiệm số không có dữ liệu/xuất xứ lần chạy bị từ chối (RC-09)."""
    with pytest.raises((ProvenanceError, ValidationError)):
        TableArtifact(
            table_id="TBL-000001",
            title="Benchmark Evaluation on BGL and Thunderbird",
            caption="Detection performance metrics",
            content="| Model | F1 | AUC |\n|---|---|---|\n| Ours | 0.98 | 0.99 |",
            is_numerical_result=True,
            dataset_id="DATA-000001",
            experiment_run_ids=[],  # Thiếu lượt chạy
            output_sha256="tablehash123",
        )


def test_invariant_6_invalid_epistemic_state_rejected():
    """TEST 6: Các chuyển đổi/giá trị trạng thái nhận thức không hợp lệ bị từ chối (RC-07)."""
    with pytest.raises(ValidationError):
        Claim(
            claim_id="CLM-000004",
            statement="Log parser errors can be mitigated by sub-word tokenization.",
            claim_type=ClaimType.OUR_INFERENCE,
            ownership=IntellectualOwnership.OURS,
            epistemic_status="UNKNOWN_STATUS",  # Trạng thái không hợp lệ
        )


def test_invariant_7_contradictory_evidence_preserved_concurrently(repository: ResearchRepository):
    """TEST 7: Bằng chứng mâu thuẫn và tuyên bố có thể được lưu trữ đồng thời mà không cần ghi đè (RC-13)."""
    from research_agent.interfaces.claim_ledger import ClaimLedger

    ledger = ClaimLedger(repository)

    # Đăng ký yêu cầu A
    claim_a = ledger.register_claim(
        statement="Template-based log parsers preserve critical anomaly signals.",
        claim_type=ClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.SOURCE,
        epistemic_status=EpistemicStatus.SUPPORTED,
    )

    # Đăng ký Khiếu nại B (Phát hiện mâu thuẫn)
    claim_b = ledger.register_claim(
        statement="Template extraction creates out-of-vocabulary blind spots that obscure zero-day attacks.",
        claim_type=ClaimType.OUR_INFERENCE,
        ownership=IntellectualOwnership.OURS,
        epistemic_status=EpistemicStatus.SUPPORTED,
    )

    # Đăng ký hồ sơ mâu thuẫn
    ctr = ledger.register_contradiction(
        claim_a_id=claim_a.claim_id,
        claim_b_id=claim_b.claim_id,
        description="Template parsing introduces informational loss under shifting log formats.",
    )

    assert ctr.contradiction_id.startswith("CTR-")
    # Xác minh cả hai xác nhận quyền sở hữu vẫn tồn tại và trạng thái của chúng được chuyển sang CONTESTED
    reloaded_a = repository.get_claim(claim_a.claim_id)
    reloaded_b = repository.get_claim(claim_b.claim_id)
    assert reloaded_a is not None and reloaded_b is not None
    assert reloaded_a.epistemic_status == EpistemicStatus.CONTESTED
    assert reloaded_b.epistemic_status == EpistemicStatus.CONTESTED


def test_invariant_8_failed_experiment_run_persisted(repository: ResearchRepository):
    """TEST 8: ExperimentRun không thành công vẫn được duy trì thành công với trạng thái lỗi được giữ nguyên (RC-14)."""
    # Tạo thử nghiệm gốc
    exp = Experiment(
        experiment_id="EXP-000001",
        rq_id="RQ-000001",
        hyp_id="HYP-000001",
        title="BiLSTM Baseline with Static Tokenizer",
        description="Evaluation under extreme out-of-vocabulary rate",
        target_representation_aspect="OOV robustness",
    )
    repository.save_experiment(exp)

    # Tạo một lần chạy không thành công
    failed_run = ExperimentRun(
        run_id="RUN-000001",
        experiment_id="EXP-000001",
        dataset_id="DATA-000001",
        dataset_version_id="DSV-000001",
        split_hash="splithash789",
        random_seed=42,
        git_commit_hash="commit_abcdef",
        command="python -m research_agent.train --config oof.yaml",
        status=ExperimentStatus.FAILED,
        error_message="CUDA Out Of Memory on batch 1024 with sequence length 4096",
        metrics={},
    )
    repository.save_experiment_run(failed_run)

    # Xác minh truy xuất
    loaded_run = repository.get_experiment_run("RUN-000001")
    assert loaded_run is not None
    assert loaded_run.status == ExperimentStatus.FAILED
    assert "CUDA Out Of Memory" in (loaded_run.error_message or "")

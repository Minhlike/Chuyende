"""
Unit & Integration Tests for Academic Composition & Anti-Hallucination Compiler (Prompt 7)
"""

import pytest
from research_agent.core.enums import (
    CompositionMode,
    IntellectualOwnership,
    SentenceClaimType,
    SentenceCompilationState,
    VerificationStatus,
    WritingReadiness,
)
from research_agent.schemas.composition import SentenceRecord
from research_agent.schemas.verification import NumericalClaim
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.composition.anti_hallucination import AntiHallucinationCompiler
from research_agent.composition.gates import WritingGate
from research_agent.composition.composer import AcademicComposer


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_composition.db"
    db = DatabaseManager(f"sqlite:///{db_file}")
    db.init_schema()
    return db


@pytest.fixture
def repo(test_db):
    return ResearchRepository(test_db)


@pytest.fixture
def compiler(repo):
    return AntiHallucinationCompiler(repo)


@pytest.fixture
def gate(repo):
    return WritingGate(repo)


@pytest.fixture
def composer(repo):
    return AcademicComposer(repo)


# ======================================================================
# TEST-COMP-01..10: Anti-Hallucination & Writing Gate Test Cases
# ======================================================================

def test_comp_01_external_claim_without_citation_flagged(compiler):
    """External factual claim without citation must fail compilation with NEEDS_CITATION."""
    sent = SentenceRecord(
        sentence_id="S-01",
        paragraph_id="P-01",
        sentence_index=0,
        text="Mô hình DeepLog sử dụng kiến trúc LSTM để phân tích chuỗi khóa nhật ký hệ thống.",
        claim_type=SentenceClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.SOURCE,
        citation_source_ids=[],
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.NEEDS_CITATION
    assert any("requires verified citation" in iss for iss in res.issues)


def test_comp_02_citation_with_nonexistent_source_rejected(compiler):
    """Citation with nonexistent source ID must be REJECTED."""
    sent = SentenceRecord(
        sentence_id="S-02",
        paragraph_id="P-01",
        sentence_index=0,
        text="Theo nghiên cứu trước [SRC-999999], độ chính xác đạt 99%.",
        claim_type=SentenceClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.SOURCE,
        citation_source_ids=["SRC-999999"],
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.REJECTED


def test_comp_03_ownership_theft_detected(compiler):
    """Prior art claim labeled as OURS must be flagged as OWNERSHIP_CONFLICT."""
    sent = SentenceRecord(
        sentence_id="S-03",
        paragraph_id="P-01",
        sentence_index=0,
        text="Chúng tôi đề xuất phương pháp biểu diễn từ bài báo trước.",
        claim_type=SentenceClaimType.SOURCE_CLAIM,
        ownership=IntellectualOwnership.OURS,
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.OWNERSHIP_CONFLICT


def test_comp_04_unbacked_novelty_buzzwords_flagged(compiler):
    """Unjustified buzzwords (first-ever, state-of-the-art) must be flagged OVERGENERALIZED."""
    sent = SentenceRecord(
        sentence_id="S-04",
        paragraph_id="P-01",
        sentence_index=0,
        text="Đây là mô hình first-ever đạt hiệu năng tối ưu trên không gian biểu diễn đa chiều.",
        claim_type=SentenceClaimType.OUR_DESIGN,
        ownership=IntellectualOwnership.OURS,
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.OVERGENERALIZED


def test_comp_05_causal_inflation_flagged(compiler):
    """Causal assertions on correlational evidence must be flagged OVERGENERALIZED."""
    from research_agent.schemas.verification import VerifiedClaimBundle
    from research_agent.core.enums import AllowedWordingStrength

    sent = SentenceRecord(
        sentence_id="S-05",
        paragraph_id="P-01",
        sentence_index=0,
        text="Biểu diễn đồ thị causes sự suy giảm đáng kể của tỷ lệ dương tính giả.",
        claim_type=SentenceClaimType.INTERPRETATION,
        ownership=IntellectualOwnership.OURS,
    )
    bundle = VerifiedClaimBundle(
        claim_id="CLM-01",
        statement="Graph representation correlates with FPR reduction",
        allowed_wording_strength=AllowedWordingStrength.ASSOCIATIONAL,
    )
    res = compiler.compile_sentence(sent, verified_bundle=bundle)
    assert res.compilation_state == SentenceCompilationState.OVERGENERALIZED


def test_comp_06_unverified_numerical_claim_flagged(compiler):
    """Sentence referencing unverified numerical claim ID must be flagged NUMERICALLY_UNVERIFIED."""
    sent = SentenceRecord(
        sentence_id="S-06",
        paragraph_id="P-01",
        sentence_index=0,
        text="Độ trễ xử lý đạt 1.2ms trên tập dữ liệu kiểm thử.",
        claim_type=SentenceClaimType.EXPERIMENT_RESULT,
        ownership=IntellectualOwnership.OURS,
        numerical_claim_ids=["NUM-MISSING-01"],
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.NUMERICALLY_UNVERIFIED


def test_comp_07_verified_numerical_claim_passes(compiler, repo):
    """Sentence referencing verified numerical claim must PASS compilation."""
    num_c = NumericalClaim(
        numerical_claim_id="NUM-TEST-01",
        statement="Inference latency is 1.2ms",
        quantity_name="Latency",
        raw_value=1.2,
        display_value="1.2ms",
        unit="ms",
        source_type="EXPERIMENT_RESULT",
        verification_status=VerificationStatus.VERIFIED,
    )
    repo.save_numerical_claim(num_c)

    sent = SentenceRecord(
        sentence_id="S-07",
        paragraph_id="P-01",
        sentence_index=0,
        text="Độ trễ xử lý thực nghiệm đạt 1.2ms theo số đo chuẩn hóa.",
        claim_type=SentenceClaimType.EXPERIMENT_RESULT,
        ownership=IntellectualOwnership.OURS,
        numerical_claim_ids=["NUM-TEST-01"],
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.PASS


def test_comp_08_anomaly_attack_conflation_flagged(compiler):
    """Conflating HDFS log anomalies with cyberattack detection must be flagged SCOPE_MISMATCH."""
    sent = SentenceRecord(
        sentence_id="S-08",
        paragraph_id="P-01",
        sentence_index=0,
        text="Hệ thống phát hiện các cuộc cyberattack trên bộ dữ liệu HDFS chuẩn.",
        claim_type=SentenceClaimType.EXPERIMENT_RESULT,
        ownership=IntellectualOwnership.OURS,
    )
    res = compiler.compile_sentence(sent)
    assert res.compilation_state == SentenceCompilationState.SCOPE_MISMATCH


def test_comp_09_writing_gate_unknown_node_not_ready(gate):
    """Unknown roadmap node code must evaluate to NOT_READY and is_blocked=True."""
    st = gate.evaluate_node_readiness("9.9.9")
    assert st.readiness == WritingReadiness.NOT_READY
    assert st.is_blocked is True


def test_comp_10_academic_composer_builds_abstract_and_conclusion(composer):
    """Composer must build valid abstract and conclusion strings."""
    abstract = composer.build_abstract()
    assert len(abstract) > 50
    assert "nhật ký" in abstract.lower() or "biểu diễn" in abstract.lower()

    conclusion = composer.build_conclusion()
    assert len(conclusion) > 50
    assert "rq" in conclusion.lower() or "giả thuyết" in conclusion.lower()

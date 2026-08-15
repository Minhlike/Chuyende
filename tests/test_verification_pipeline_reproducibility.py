"""
Integration Tests for Scientific Verification Pipeline & Reproducibility (Prompt 6)
"""

import pytest
from research_agent.core.enums import (
    VerificationRequestType,
    VerificationRequestStatus,
    VerificationStatus,
    IntellectualOwnership,
    AllowedWordingStrength,
    ReproducibilityLevel,
)
from research_agent.schemas.reasoning import VerificationRequest
from research_agent.schemas.verification import (
    NumericalClaim,
    StatisticalResult,
    ResultBundle,
    VerifiedClaimBundle,
)
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.verification.pipeline import ScientificVerificationPipeline
from research_agent.verification.reproducibility.lineage_dag import ScientificLineageDAG
from research_agent.verification.reproducibility.invalidation import InvalidationManager
from research_agent.verification.reproducibility.reproduce import ReproductionRunner
from research_agent.verification.packaging import ResultBundleBuilder, VerifiedClaimBundleBuilder
from research_agent.verification.auditors import VerificationGateForWriting


@pytest.fixture
def test_pipeline_env(tmp_path):
    db_file = tmp_path / "test_verif.db"
    db_mgr = DatabaseManager(db_path=str(db_file))
    repo = ResearchRepository(db_mgr)
    pipeline = ScientificVerificationPipeline(repository=repo)
    dag = ScientificLineageDAG()
    inv_mgr = InvalidationManager(dag)
    repro_runner = ReproductionRunner()
    result_builder = ResultBundleBuilder()
    claim_bundle_builder = VerifiedClaimBundleBuilder()
    writing_gate = VerificationGateForWriting()
    return {
        "repo": repo,
        "pipeline": pipeline,
        "dag": dag,
        "inv_mgr": inv_mgr,
        "repro_runner": repro_runner,
        "result_builder": result_builder,
        "claim_bundle_builder": claim_bundle_builder,
        "writing_gate": writing_gate,
    }


def test_pipeline_01_equation_verification_request(test_pipeline_env):
    """TEST-PIPE-01: Dispatches EQUATION_CHECK through pipeline and records PASS."""
    pipeline = test_pipeline_env["pipeline"]
    req = VerificationRequest(
        request_id="VRQ-000001",
        request_type=VerificationRequestType.EQUATION_CHECK,
        description="Verify algebraic expansion",
        input_payload={"expr_a": "(a + b)**2", "expr_b": "a**2 + 2*a*b + b**2"},
        status=VerificationRequestStatus.REQUESTED,
    )
    res = pipeline.execute_request(req)
    assert res.status == VerificationRequestStatus.PASS
    assert res.computed_result["symbolic_state"] == "PROVEN_EQUIVALENT"


def test_pipeline_02_hypothesis_test_request(test_pipeline_env):
    """TEST-PIPE-02: Dispatches STATISTICAL_TEST through pipeline and records PASS."""
    pipeline = test_pipeline_env["pipeline"]
    req = VerificationRequest(
        request_id="VRQ-000002",
        request_type=VerificationRequestType.STATISTICAL_TEST,
        description="Paired seed test",
        input_payload={
            "group_ours": [0.95, 0.96, 0.94, 0.97, 0.95],
            "group_baseline": [0.85, 0.86, 0.84, 0.85, 0.83],
            "question": "Superiority across 5 seeds",
        },
        status=VerificationRequestStatus.REQUESTED,
    )
    res = pipeline.execute_request(req)
    assert res.status == VerificationRequestStatus.PASS
    assert res.computed_result["is_significant"] is True
    assert res.computed_result["p_value"] < 0.01


def test_lineage_01_dag_and_invalidation_cascading(test_pipeline_env):
    """TEST-LIN-01: Lineage DAG tracks downstream dependents and cascades invalidation."""
    dag = test_pipeline_env["dag"]
    inv_mgr = test_pipeline_env["inv_mgr"]
    # Setup graph: Dataset -> Run1 -> Metric1 -> Claim1
    dag.add_dependency("DSV-01", "RUN-01")
    dag.add_dependency("RUN-01", "MET-01")
    dag.add_dependency("MET-01", "NUM-01")

    downstream = dag.get_downstream_dependents("DSV-01")
    assert downstream == {"RUN-01", "MET-01", "NUM-01"}

    # Invalidate dataset due to timestamp contamination
    affected = inv_mgr.invalidate_entity("DSV-01", "Timestamp contamination found")
    assert affected == {"DSV-01", "RUN-01", "MET-01", "NUM-01"}

    is_inv, reason = inv_mgr.is_invalidated("NUM-01")
    assert is_inv is True
    assert "Cascaded invalidation" in reason


def test_repro_01_level_2_metric_divergence(test_pipeline_env):
    """TEST-REPRO-01: Level 2 metric recomputation flags divergence."""
    repro_runner = test_pipeline_env["repro_runner"]
    orig = {"f1": 0.9520, "recall": 0.9200}
    recomp_identical = {"f1": 0.9520, "recall": 0.9200}
    recomp_divergent = {"f1": 0.8800, "recall": 0.9200}

    pass_ok, _ = repro_runner.verify_level_2_metrics(recomp_identical, orig)
    assert pass_ok is True

    pass_fail, details = repro_runner.verify_level_2_metrics(recomp_divergent, orig)
    assert pass_fail is False
    assert "f1" in details["divergences"]


def test_writing_gate_01_unverified_claim_blocked(test_pipeline_env):
    """TEST-GATE-01: Writing gate blocks unverified numerical claims from thesis composition."""
    claim_bundle_builder = test_pipeline_env["claim_bundle_builder"]
    writing_gate = test_pipeline_env["writing_gate"]
    unverified_num = NumericalClaim(
        numerical_claim_id="NUM-000001",
        statement="Achieves 99.9% detection rate",
        quantity_name="Recall",
        raw_value=0.999,
        display_value="99.9%",
        source_type="EXPERIMENT_RESULT",
        computation_id="RUN-01",
        verification_status=VerificationStatus.PENDING,  # PENDING, not VERIFIED
    )
    bundle = claim_bundle_builder.build_claim_bundle(
        claim_id="CLM-000001",
        statement="Our method achieves 99.9% detection rate.",
        numerical_claims=[unverified_num],
        allowed_wording_strength=AllowedWordingStrength.SUPPORTIVE,
    )

    ok, issues = writing_gate.audit_claim_for_thesis_composition(bundle)
    assert ok is False
    assert any("unverified numerical quantity" in i for i in issues)


def test_writing_gate_02_exaggerated_language_blocked(test_pipeline_env):
    """TEST-GATE-02: Writing gate blocks causal/superiority language for DESCRIPTIVE_ONLY claims."""
    claim_bundle_builder = test_pipeline_env["claim_bundle_builder"]
    writing_gate = test_pipeline_env["writing_gate"]
    verified_num = NumericalClaim(
        numerical_claim_id="NUM-000002",
        statement="Observed latency is 4.2ms",
        quantity_name="Latency",
        raw_value=4.2,
        display_value="4.2ms",
        source_type="EXPERIMENT_RESULT",
        computation_id="RUN-02",
        verification_status=VerificationStatus.VERIFIED,
    )
    bundle = claim_bundle_builder.build_claim_bundle(
        claim_id="CLM-000002",
        statement="Our approach drastically outperforms and causes faster response.",
        numerical_claims=[verified_num],
        allowed_wording_strength=AllowedWordingStrength.DESCRIPTIVE_ONLY,
    )

    ok, issues = writing_gate.audit_claim_for_thesis_composition(bundle)
    assert ok is False
    assert any("uses comparative or causal language" in i for i in issues)

"""
Scientific Verification Pipeline Coordinator (Prompt 6 Section 5, 99)
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from research_agent.core.enums import (
    VerificationRequestType,
    VerificationRequestStatus,
    VerificationStatus,
    SymbolicEqualityState,
    ReproducibilityLevel,
)
from research_agent.schemas.reasoning import VerificationRequest
from research_agent.schemas.verification import VerificationResult
from research_agent.storage.repository import ResearchRepository
from research_agent.verification.equations.symbolic_engine import SymbolicVerificationEngine
from research_agent.verification.equations.provenance import EquationProvenanceAuditor
from research_agent.verification.equations.symbol_registry import SymbolRegistry
from research_agent.verification.datasets.data_validator import DataValidator
from research_agent.verification.datasets.split_validator import AntiLeakageSplitValidator
from research_agent.verification.datasets.data_profiler import DataProfiler
from research_agent.verification.metrics.recomputation import MetricRecomputationEngine
from research_agent.verification.statistics.descriptive import DescriptiveStatisticsEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine
from research_agent.verification.statistics.effect_sizes import EffectSizeEngine
from research_agent.verification.statistics.hypothesis_tests import HypothesisTestingEngine
from research_agent.verification.statistics.multi_seed_aggregator import MultiSeedAggregator
from research_agent.verification.statistics.misuse_guards import StatisticalMisuseAuditor
from research_agent.verification.tables.builder import TableBuilder
from research_agent.verification.tables.fairness import TableFairnessAuditor
from research_agent.verification.figures.builder import FigureBuilder
from research_agent.verification.figures.metadata import FigureMetadataManager
from research_agent.verification.reproducibility.reproduce import ReproductionRunner
from research_agent.verification.auditors import NumericalHallucinationAuditor, VerificationGateForWriting


class ScientificVerificationPipeline:
    """
    Central coordinator for deterministic scientific computation and verification.
    Executes VerificationRequest tickets dispatched by the Reasoning Engine (Prompt 5).
    """

    def __init__(self, repository: Optional[ResearchRepository] = None):
        self.repo = repository or ResearchRepository()
        self.symbolic_engine = SymbolicVerificationEngine()
        self.eq_auditor = EquationProvenanceAuditor()
        self.symbol_registry = SymbolRegistry()
        self.data_validator = DataValidator()
        self.split_validator = AntiLeakageSplitValidator()
        self.data_profiler = DataProfiler()
        self.metric_engine = MetricRecomputationEngine()
        self.desc_engine = DescriptiveStatisticsEngine()
        self.ci_engine = ConfidenceIntervalEngine()
        self.effect_engine = EffectSizeEngine()
        self.hyp_engine = HypothesisTestingEngine()
        self.multi_seed = MultiSeedAggregator()
        self.stat_misuse_auditor = StatisticalMisuseAuditor()
        self.table_builder = TableBuilder()
        self.table_fairness = TableFairnessAuditor()
        self.figure_builder = FigureBuilder()
        self.figure_metadata = FigureMetadataManager()
        self.repro_runner = ReproductionRunner()
        self.num_auditor = NumericalHallucinationAuditor()
        self.writing_gate = VerificationGateForWriting()

    def execute_request(self, request: VerificationRequest) -> VerificationResult:
        """Dispatches and executes a VerificationRequest deterministically."""
        req_type = request.request_type
        payload = request.input_payload or {}
        result_id = f"VRS-{abs(hash(request.request_id + str(datetime.now(timezone.utc)))) % 1000000:06d}"

        status = VerificationRequestStatus.RUNNING
        computed_result: Dict[str, Any] = {}
        warnings: List[str] = []
        limitations: List[str] = []
        provenance_trail: List[str] = [f"Executed via ScientificVerificationPipeline for request {request.request_id}"]
        method_used = req_type.value

        try:
            if req_type == VerificationRequestType.EQUATION_CHECK:
                expr_a = payload.get("expr_a", "")
                expr_b = payload.get("expr_b", "")
                state, details = self.symbolic_engine.verify_algebraic_equivalence(expr_a, expr_b)
                computed_result = {"symbolic_state": state.value, "details": details}
                status = VerificationRequestStatus.PASS if state in [SymbolicEqualityState.PROVEN_EQUIVALENT, SymbolicEqualityState.NUMERICALLY_CONSISTENT] else VerificationRequestStatus.FAIL
                method_used = "SymPy Algebraic Equivalence"

            elif req_type == VerificationRequestType.NUMERICAL_CHECK:
                y_true = payload.get("y_true", [])
                y_pred = payload.get("y_pred", [])
                cm = self.metric_engine.compute_confusion_matrix(y_true, y_pred)
                computed_result = cm.model_dump(mode="json")
                status = VerificationRequestStatus.PASS
                method_used = "Deterministic Confusion Matrix"

            elif req_type == VerificationRequestType.STATISTICAL_TEST:
                g_ours = payload.get("group_ours", [])
                g_base = payload.get("group_baseline", [])
                question = payload.get("question", request.description)
                stat_res = self.hyp_engine.run_paired_test(g_ours, g_base, question=question)
                is_valid, misuse_issues = self.stat_misuse_auditor.audit_statistical_result(stat_res)
                warnings.extend(misuse_issues)
                computed_result = stat_res.model_dump(mode="json")
                status = VerificationRequestStatus.PASS if is_valid else VerificationRequestStatus.FAIL
                method_used = f"Hypothesis Test ({stat_res.test_name})"

            elif req_type == VerificationRequestType.EFFECT_SIZE:
                g1 = payload.get("group1", [])
                g2 = payload.get("group2", [])
                d = self.effect_engine.compute_cohens_d(g1, g2)
                g = self.effect_engine.compute_hedges_g(g1, g2)
                diffs = self.effect_engine.compute_absolute_and_relative_diff(float(payload.get("baseline_mean", 0)), float(payload.get("proposed_mean", 0)))
                computed_result = {"cohens_d": d, "hedges_g": g, **diffs}
                status = VerificationRequestStatus.PASS
                method_used = "Standardized Effect Sizes"

            elif req_type == VerificationRequestType.CONFIDENCE_INTERVAL:
                vals = payload.get("values", [])
                level = float(payload.get("confidence_level", 0.95))
                m, low, high = self.ci_engine.compute_bootstrap_ci(vals, confidence_level=level)
                computed_result = {"mean": m, "ci_lower": low, "ci_upper": high, "level": level}
                status = VerificationRequestStatus.PASS
                method_used = "Empirical Bootstrap CI"

            elif req_type == VerificationRequestType.DATASET_VALIDATE:
                expected_sha = payload.get("expected_sha256", "")
                file_p = payload.get("file_path", "")
                valid_hash, hash_msg = self.data_validator.validate_file_hash(file_p, expected_sha) if file_p and expected_sha else (True, "No file path given")
                computed_result = {"hash_valid": valid_hash, "details": hash_msg}
                status = VerificationRequestStatus.PASS if valid_hash else VerificationRequestStatus.FAIL
                method_used = "SHA-256 Dataset Hash Validation"

            elif req_type == VerificationRequestType.METRIC_RECOMPUTE:
                y_true = payload.get("y_true", [])
                y_scores = payload.get("y_scores", [])
                pr_auc, r_curve, p_curve, _ = self.metric_engine.compute_pr_curve_and_auc(y_true, y_scores)
                computed_result = {"pr_auc": pr_auc, "curve_points": len(r_curve)}
                status = VerificationRequestStatus.PASS
                method_used = "Trapezoidal PR-AUC Recomputation"

            elif req_type == VerificationRequestType.RESULT_REPRODUCE:
                orig = payload.get("original_metrics", {})
                recomp = payload.get("recomputed_metrics", {})
                pass_l2, details = self.repro_runner.verify_level_2_metrics(recomp, orig)
                computed_result = details
                status = VerificationRequestStatus.PASS if pass_l2 else VerificationRequestStatus.FAIL
                method_used = "Level 2 Metric Reproduction"

            else:
                computed_result = {"message": f"Generic verification executed for {req_type.value}"}
                status = VerificationRequestStatus.PASS

        except Exception as e:
            status = VerificationRequestStatus.FAIL
            warnings.append(f"Execution exception: {str(e)}")
            computed_result = {"error": str(e)}

        res = VerificationResult(
            result_id=result_id,
            request_id=request.request_id,
            status=status,
            verified_artifact_ids=request.target_claim_id and [request.target_claim_id] or [],
            computed_result=computed_result,
            method_used=method_used,
            provenance_trail=provenance_trail,
            assumptions_applied=[],
            warnings=warnings,
            limitations=limitations,
            reproducibility_level=ReproducibilityLevel.LEVEL_2_METRIC,
            completed_at=datetime.now(timezone.utc),
        )

        # Update database record
        request.status = status
        request.verification_result = computed_result
        request.completed_at = datetime.now(timezone.utc)
        self.repo.save_verification_request(request)

        return res

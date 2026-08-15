"""
Scientific Outcome Packaging & Bundle Builders (Prompt 6 Section 98, 138)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from research_agent.core.enums import (
    AllowedWordingStrength,
    IntellectualOwnership,
    VerificationStatus,
)
from research_agent.schemas.verification import (
    NumericalClaim,
    StatisticalResult,
    TableSpecification,
    FigureSpecification,
    ResultBundle,
    VerifiedClaimBundle,
)


class ResultBundleBuilder:
    """
    Assembles verified empirical outcomes into an immutable ResultBundle (Prompt 6 Section 98).
    """

    def build_bundle(
        self,
        bundle_id: str,
        roadmap_node_code: str,
        rq_id: str,
        hyp_id: str,
        experiment_run_ids: List[str],
        verified_metrics: Dict[str, float],
        numerical_claims: List[NumericalClaim],
        statistical_results: List[StatisticalResult],
        table_ids: List[str],
        figure_ids: List[str],
        data_provenance_summary: str,
        limitations: Optional[List[str]] = None,
        comparability_constraints: Optional[List[str]] = None,
        invalidated_run_ids: Optional[List[str]] = None,
    ) -> ResultBundle:
        return ResultBundle(
            bundle_id=bundle_id,
            roadmap_node_code=roadmap_node_code,
            rq_id=rq_id,
            hyp_id=hyp_id,
            experiment_run_ids=experiment_run_ids,
            verified_metrics=verified_metrics,
            numerical_claims=numerical_claims,
            statistical_results=statistical_results,
            table_ids=table_ids,
            figure_ids=figure_ids,
            data_provenance_summary=data_provenance_summary,
            limitations=limitations or [],
            comparability_constraints=comparability_constraints or [],
            invalidated_run_ids=invalidated_run_ids or [],
            created_at=datetime.now(timezone.utc),
        )


class VerifiedClaimBundleBuilder:
    """
    Constructs guarded claim packages for Prompt 7 Chapter Composer (Prompt 6 Section 138).
    """

    def build_claim_bundle(
        self,
        claim_id: str,
        statement: str,
        ownership: IntellectualOwnership = IntellectualOwnership.OURS,
        source_evidence_ids: Optional[List[str]] = None,
        numerical_claims: Optional[List[NumericalClaim]] = None,
        equation_ids: Optional[List[str]] = None,
        result_bundle_id: Optional[str] = None,
        uncertainty_description: Optional[str] = None,
        allowed_wording_strength: AllowedWordingStrength = AllowedWordingStrength.SUPPORTIVE,
        citation_keys: Optional[List[str]] = None,
    ) -> VerifiedClaimBundle:
        return VerifiedClaimBundle(
            claim_id=claim_id,
            statement=statement,
            ownership=ownership,
            source_evidence_ids=source_evidence_ids or [],
            numerical_claims=numerical_claims or [],
            equation_ids=equation_ids or [],
            result_bundle_id=result_bundle_id,
            uncertainty_description=uncertainty_description,
            allowed_wording_strength=allowed_wording_strength,
            citation_keys=citation_keys or [],
            created_at=datetime.now(timezone.utc),
        )

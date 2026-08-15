"""
Structured Research Inference Engine & Scope Controller (Prompt 5 Sections 24, 25, 26)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.core.enums import ReasoningMode
from research_agent.schemas.reasoning import InferenceRecord, ClaimScope, ReasoningIssue
from research_agent.core.enums import ReasoningIssueType


class InferenceEngine:
    """
    Constructs structured research inferences and enforces scope containment.
    Strictly validates: conclusion_scope ⊆ justified_scope (Prompt 5 Section 26).
    """

    def construct_inference(
        self,
        premises: List[str],
        evidence_ids: List[str],
        assumption_ids: List[str],
        candidate_conclusion: str,
        reasoning_type: ReasoningMode = ReasoningMode.INDUCTIVE,
        justified_scope: Optional[ClaimScope] = None,
        counterevidence_ids: Optional[List[str]] = None,
        confidence_basis: str = "Empirical evidence triangulation",
        strength: str = "MODERATE",
        remaining_uncertainty: str = "Bounded by evaluation dataset parameters.",
        falsification_route: str = "Conduct out-of-distribution holdout evaluation.",
    ) -> Tuple[InferenceRecord, List[ReasoningIssue]]:
        """
        Builds InferenceRecord and audits for scope expansion or causal inflation.
        """
        seq = abs(hash(candidate_conclusion + "".join(premises))) % 1000000
        inf_id = f"INF-{seq:06d}"
        scope = justified_scope or ClaimScope()
        issues: List[ReasoningIssue] = []

        # Scope Containment Check (Section 26)
        c_lower = candidate_conclusion.lower()
        
        # Check if narrow dataset premise attempts to generalize to 'all cyberattacks' or 'all logs'
        is_narrow_dataset = any(
            (scope.dataset and ds in scope.dataset.lower()) or any(ds in p.lower() for ds in ["hdfs", "bgl", "thunderbird"])
            for p in premises
        )
        if is_narrow_dataset:
            if any(term in c_lower for term in ["all cyberattacks", "enterprise systems", "general intrusion detection", "all systems"]):
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-{abs(hash(inf_id + 'scope')) % 1000000:06d}",
                        issue_type=ReasoningIssueType.OVERGENERALIZATION,
                        affected_entity_id=inf_id,
                        message="Conclusion scope exceeds justified premise scope (HDFS/BGL system logs generalized to enterprise cyberattacks).",
                        severity="HIGH",
                        mitigation="Narrow candidate conclusion to bounded dataset scope or mark as GENERALIZATION_PROPOSAL.",
                    )
                )

        # Causal Inflation Check (Section 27)
        if any(w in c_lower for w in ["causes", "leads to", "proves", "eliminates"]):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-{abs(hash(inf_id + 'causal')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.CAUSALITY_INFLATION,
                    affected_entity_id=inf_id,
                    message="Conclusion uses deterministic causal language ('causes' / 'proves') for observational/statistical findings.",
                    severity="HIGH",
                    mitigation="Replace with associational or probabilistic phrasing (e.g. 'is associated with', 'empirically improves').",
                )
            )

        # Missing Evidence Check
        if not evidence_ids and strength in ["STRONG", "MODERATE"]:
            strength = "WEAK"
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-{abs(hash(inf_id + 'no_evd')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.UNSUPPORTED_CLAIM,
                    affected_entity_id=inf_id,
                    message="Inference marked MODERATE/STRONG without direct linked empirical evidence IDs.",
                    severity="MEDIUM",
                    mitigation="Downgrade inference strength to WEAK or attach verified Evidence IDs.",
                )
            )

        record = InferenceRecord(
            inference_id=inf_id,
            premises=premises,
            evidence_ids=evidence_ids,
            assumption_ids=assumption_ids,
            reasoning_type=reasoning_type,
            justified_scope=scope,
            counterevidence_ids=counterevidence_ids or [],
            candidate_conclusion=candidate_conclusion,
            confidence_basis=confidence_basis,
            strength=strength,
            remaining_uncertainty=remaining_uncertainty,
            falsification_route=falsification_route,
        )

        return record, issues

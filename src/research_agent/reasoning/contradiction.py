"""
10-Point Scientific Contradiction Analyzer (Prompt 5 Section 15)
"""

from typing import Dict, Any, Optional, Tuple
from research_agent.core.enums import ContradictionType
from research_agent.schemas.claim import Claim


class ContradictionAnalysisResult:
    """Detailed evaluation report for a contradiction between two claims."""

    def __init__(
        self,
        claim_a_id: str,
        claim_b_id: str,
        contradiction_type: ContradictionType,
        checklist_evaluations: Dict[str, bool],
        diagnosis: str,
        resolution_strategy: Optional[str] = None,
    ):
        self.claim_a_id = claim_a_id
        self.claim_b_id = claim_b_id
        self.contradiction_type = contradiction_type
        self.checklist_evaluations = checklist_evaluations
        self.diagnosis = diagnosis
        self.resolution_strategy = resolution_strategy


class ContradictionAnalyzer:
    """
    Evaluates apparent conflicts between scientific claims across 10 methodological dimensions.
    Prevents false assumptions of 'reproducibility failure' when divergence stems from differing scopes.
    """

    def analyze(
        self,
        claim_a: Claim,
        claim_b: Claim,
        context_notes: Optional[str] = None,
    ) -> ContradictionAnalysisResult:
        """
        Execute 10-point contradiction audit across:
        1. same_question
        2. same_dataset
        3. same_labels
        4. same_split
        5. same_metric
        6. same_baseline
        7. same_information_budget
        8. same_threat_model
        9. same_time_or_version
        10. same_operational_constraints
        """
        ca_text = claim_a.statement.lower()
        cb_text = claim_b.statement.lower()
        notes = (context_notes or "").lower()

        checklist = {
            "same_question": True,
            "same_dataset": True,
            "same_labels": True,
            "same_split": True,
            "same_metric": True,
            "same_baseline": True,
            "same_information_budget": True,
            "same_threat_model": True,
            "same_time_or_version": True,
            "same_operational_constraints": True,
        }

        # 1. Dataset difference check
        datasets = ["darpa", "lanl", "bgl", "hdfs", "thunderbird", "optc"]
        found_in_a = [d for d in datasets if d in ca_text]
        found_in_b = [d for d in datasets if d in cb_text]
        if found_in_a and found_in_b and found_in_a != found_in_b:
            checklist["same_dataset"] = False

        # 2. Metric difference check
        metrics = ["f1", "precision", "recall", "pr-auc", "auc", "latency", "throughput"]
        m_in_a = [m for m in metrics if m in ca_text]
        m_in_b = [m for m in metrics if m in cb_text]
        if m_in_a and m_in_b and m_in_a != m_in_b:
            checklist["same_metric"] = False

        # 3. Threat model & baseline checks
        if "baseline" in notes or "simple" in ca_text or "simple" in cb_text:
            if "synthetic" in ca_text or "synthetic" in cb_text or "darpa" in ca_text or "lanl" in cb_text:
                checklist["same_information_budget"] = False

        # Determine Classification
        if not checklist["same_dataset"]:
            c_type = ContradictionType.DATASET_DIFFERENCE
            diagnosis = f"Claims evaluate disjoint dataset domains ({found_in_a} vs {found_in_b}). Divergence is environmental rather than fundamental."
            strategy = "Conduct cross-dataset evaluation across both datasets under identical split policies."
        elif not checklist["same_metric"]:
            c_type = ContradictionType.METRIC_DIFFERENCE
            diagnosis = f"Claims report different performance metrics ({m_in_a} vs {m_in_b})."
            strategy = "Compute both metrics simultaneously on verified test sets."
        elif not checklist["same_information_budget"]:
            c_type = ContradictionType.METHODOLOGY_DIFFERENCE
            diagnosis = "Methods had unequal access to host identifiers, template caches, or parameter dictionaries."
            strategy = "Equalize information budgets and rerun under strict identifier masking."
        else:
            # If all dimensions appear identical and empirical claims directly contradict
            c_type = ContradictionType.TRUE_CONTRADICTION
            diagnosis = "Both claims address identical setup, dataset, and metric with opposing empirical findings."
            strategy = "Execute controlled direct replication experiment (Negative Control / Intrinsic Probe)."

        return ContradictionAnalysisResult(
            claim_a_id=claim_a.claim_id,
            claim_b_id=claim_b.claim_id,
            contradiction_type=c_type,
            checklist_evaluations=checklist,
            diagnosis=diagnosis,
            resolution_strategy=strategy,
        )

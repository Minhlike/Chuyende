"""
Threshold Provenance & Anti-Tuning Auditor (Prompt 6 Section 30)
"""

from typing import Any, Dict, List, Optional, Tuple


class ThresholdAuditor:
    """
    Guarantees decision threshold selection provenance.
    Enforces that thresholds are chosen on Validation split or pre-set criteria,
    never tuned post-hoc on Test split.
    """

    def audit_threshold_selection(
        self,
        threshold_value: float,
        split_used_for_selection: str,
        selection_criterion: str,
    ) -> Tuple[bool, Optional[str]]:
        """Audits if threshold was legitimately chosen on validation partition."""
        split_clean = split_used_for_selection.strip().upper()
        if split_clean in ["TEST", "TEST_SET", "EVAL_TEST"]:
            return False, f"TEST_SET_TUNING_LEAKAGE: Threshold {threshold_value} was tuned directly on '{split_used_for_selection}'."

        if not selection_criterion or len(selection_criterion.strip()) < 3:
            return False, "Threshold lacks an explicit optimization criterion (e.g. 'Max F1 on Validation', 'FPR <= 0.1%')."

        return True, None

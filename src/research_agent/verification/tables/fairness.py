"""
Table Fairness & Comparability Auditor (Prompt 6 Section 56)
"""

from typing import Any, Dict, List, Optional, Tuple


class TableFairnessAuditor:
    """
    Audits comparison tables to prevent misleading cross-paper comparisons:
    - Differing dataset splits (e.g. 80/20 vs 60/40)
    - Differing evaluation granularities (e.g. event vs entity vs host)
    - Differing metric interpolation methods
    """

    def audit_comparison_fairness(
        self,
        method_metadata: List[Dict[str, Any]],
    ) -> Tuple[bool, Optional[str]]:
        """
        Audits a list of {method_name, dataset_version, split_strategy, granularity, source_type}.
        Returns (is_directly_comparable, incomparability_reason).
        """
        if len(method_metadata) <= 1:
            return True, None

        first = method_metadata[0]
        dataset_ver = first.get("dataset_version")
        split_strat = first.get("split_strategy")
        granularity = first.get("granularity")

        for m in method_metadata[1:]:
            if m.get("dataset_version") != dataset_ver:
                return False, (
                    f"DATASET_VERSION_MISMATCH: '{first.get('method_name')}' evaluated on {dataset_ver} "
                    f"while '{m.get('method_name')}' evaluated on {m.get('dataset_version')}."
                )
            if m.get("split_strategy") != split_strat:
                return False, (
                    f"SPLIT_STRATEGY_MISMATCH: '{first.get('method_name')}' evaluated on {split_strat} "
                    f"while '{m.get('method_name')}' evaluated on {m.get('split_strategy')}."
                )
            if m.get("granularity") != granularity:
                return False, (
                    f"GRANULARITY_MISMATCH: '{first.get('method_name')}' computed at {granularity} "
                    f"while '{m.get('method_name')}' computed at {m.get('granularity')}."
                )

        return True, None

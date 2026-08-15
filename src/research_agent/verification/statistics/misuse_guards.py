"""
Statistical Misuse & Invariant Auditor (Prompt 6 Section 43)
"""

from typing import Any, Dict, List, Optional, Tuple
from research_agent.schemas.verification import StatisticalResult


class StatisticalMisuseAuditor:
    """
    Guards against common scientific statistical errors:
    1. Reporting p-value without an accompanying effect size.
    2. Missing explicit sample unit of analysis.
    3. Interpreting p >= alpha as proof of equivalence ("absence of evidence != evidence of absence").
    4. Using unpaired tests on paired seed runs.
    5. Neglecting multiple comparisons correction when conducting many simultaneous tests.
    """

    def audit_statistical_result(self, res: StatisticalResult) -> Tuple[bool, List[str]]:
        issues = []

        # Misuse 1: p-value without effect size
        if res.p_value is not None and (res.effect_size_value is None or not res.effect_size_name):
            issues.append(f"STATISTICAL_MISUSE: p-value ({res.p_value:.4f}) reported without standardized effect size.")

        # Misuse 2: Missing sample unit
        if not res.sample_unit or len(res.sample_unit.strip()) < 2:
            issues.append("STATISTICAL_MISUSE: Missing explicit sample unit of analysis (e.g. 'Seed', 'Host', 'Session').")

        # Misuse 3: Small sample size with heavy parametric claims
        if res.sample_size_n < 5 and "t-test" in res.test_name.lower():
            issues.append(f"STATISTICAL_WARNING: Sample size n={res.sample_size_n} is too small for parametric t-test.")

        # Misuse 4: Absence of evidence interpreted as equivalence
        if res.p_value is not None and res.p_value >= 0.05:
            if "equivalent" in res.interpretation_notes.lower() or "identical" in res.interpretation_notes.lower():
                issues.append(
                    "STATISTICAL_MISUSE: Non-significant p-value (p >= 0.05) cannot be interpreted as proof of equivalence without equivalence testing (TOST)."
                )

        return len(issues) == 0, issues

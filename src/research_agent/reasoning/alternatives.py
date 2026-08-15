"""
Alternative Explanations & Competing Hypotheses Generator (Prompt 5 Sections 18, 19)
"""

from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import AlternativeExplanation, CompetingHypothesis
from research_agent.core.enums import EpistemicStatus


class AlternativeExplanationsEngine:
    """
    Generates competing explanations and confounders for observed performance gains.
    Links every alternative explanation to an explicit negative control or discriminating test.
    """

    # 8 Standard Methodological Confounders (Section 18)
    CANONICAL_CONFOUNDERS = [
        ("A1_CAPACITY", "CAPACITY", "Observed gain is due to higher model parameter count rather than representation architecture.", "Train equal-parameter baseline with standard MLP/CNN."),
        ("A2_LEAKAGE", "LEAKAGE", "Test dataset statistics or vocabulary leaked into preprocessing/normalization.", "Rerun pipeline with strict train-only fit and split isolation."),
        ("A3_SHORTCUT", "SHORTCUT", "Model learned hostnames, timestamps, or campaign IDs as shortcuts.", "Apply identifier masking (CTRL-01) and campaign holdout split (CTRL-03)."),
        ("A4_PRETRAINING", "PRETRAINING", "Performance advantage arises from broader pretraining data rather than model design.", "Ablate pretrained weights with random initialization baseline."),
        ("A5_TUNING", "TUNING", "Proposed method received extensive hyperparameter tuning while baselines used default configs.", "Run identical random search / Bayesian optimization budget across all baselines."),
        ("A6_DETECTOR_CONFOUND", "DETECTOR_CONFOUND", "Downstream detector complexity compensates for feature representation weaknesses.", "Evaluate representation using a frozen, linear probe (Probe Operational Order)."),
        ("A7_ARTIFACT", "ARTIFACT", "Performance boost is an artifact of synthetic benchmark generation anomalies.", "Evaluate across heterogeneous real enterprise telemetry (LANL, BGL)."),
        ("A8_STOCHASTIC", "STOCHASTIC", "Metric improvement falls within stochastic seed variation margins.", "Run 5-fold cross-validation across 10 random seeds with bootstrap confidence intervals."),
    ]

    def generate_alternatives(self, claim_id: str, claim_statement: str) -> List[AlternativeExplanation]:
        """
        Generate explicit alternative explanations for a performance claim.
        """
        results: List[AlternativeExplanation] = []
        for code, c_type, explanation, test in self.CANONICAL_CONFOUNDERS:
            alt_id = f"ALT-{abs(hash(claim_id + code)) % 1000000:06d}"
            results.append(
                AlternativeExplanation(
                    alt_id=alt_id,
                    explanation=f"[{code}] {explanation}",
                    confounder_type=c_type,
                    affected_claim_id=claim_id,
                    test_or_control=test,
                    likelihood="PLAUSIBLE",
                    is_tested=False,
                )
            )
        return results

    def create_competing_hypothesis(
        self,
        canonical_hyp_id: str,
        statement: str,
        why_competing: str,
        discriminating_test: str,
    ) -> CompetingHypothesis:
        """
        Creates an auxiliary competing hypothesis without modifying canonical H1..H5 (Section 19).
        """
        seq = abs(hash(canonical_hyp_id + statement)) % 1000000
        return CompetingHypothesis(
            ch_id=f"CH-{canonical_hyp_id}-{seq:04d}",
            canonical_hyp_id=canonical_hyp_id,
            statement=statement,
            why_competing=why_competing,
            discriminating_test=discriminating_test,
            status=EpistemicStatus.UNVERIFIED,
        )

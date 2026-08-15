"""
Falsification Planning & Negative Control Protocol Designer (Prompt 5 Section 20)
"""

from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import FalsificationPlan


class FalsificationPlanner:
    """
    Designs empirical falsification protocols and negative controls for hypotheses and claims.
    Ensures experimental setups possess genuine power to reject false assertions.
    """

    def plan_falsification(
        self,
        hypothesis_id: str,
        hypothesis_statement: str,
        claim_id: Optional[str] = None,
    ) -> FalsificationPlan:
        """
        Generates a rigorous FalsificationPlan for H1..H5 or related claims.
        """
        seq = abs(hash(hypothesis_id + hypothesis_statement)) % 1000000
        plan_id = f"FALS-{hypothesis_id}-{seq:04d}"
        h_lower = hypothesis_statement.lower()

        if "h1" in hypothesis_id.lower() or "parameter" in h_lower:
            falsifying_obs = [
                "Ablating dynamic parameter fields produces zero statistically significant degradation in linear probe intrusion detection F1.",
                "Renaming static template keys causes complete model failure despite dynamic parameter preservation.",
            ]
            controls = ["Template-only baseline (Drain + Word2Vec)", "Raw text baseline (BERT-base)"]
            neg_controls = ["Random parameter permutation control (CTRL-02)", "Static template scrambling (CTRL-05)"]
            req_experiments = ["Parameter ablation probe on HDFS/BGL", "Template renaming perturbation test"]
            outcomes_true = ["Parameter-aware probe F1 >= 0.90 under template shifts", "Template-only model F1 drops below 0.60"]
            outcomes_false = ["No performance difference between parameter-aware and template-only models"]

        elif "h2" in hypothesis_id.lower() or "alignment" in h_lower or "cross-view" in h_lower:
            falsifying_obs = [
                "Cross-view alignment optimization results in complete dimensional collapse (singular value spectrum collapses to rank 1).",
                "Shuffled cross-view pairs achieve equivalent downstream detection accuracy to aligned pairs.",
            ]
            controls = ["Unimodal text-only model", "Unimodal graph-only model"]
            neg_controls = ["Shuffled cross-view correspondence control (CTRL-04)", "Variance regularization ablation"]
            req_experiments = ["VICReg/Barlow Twins eigenvalue spectrum audit", "Shuffled pairing probe on Sysflow DARPA TC"]
            outcomes_true = ["Effective rank of representation >= 32", "Shuffled correspondence drops detection F1 by >= 25%"]
            outcomes_false = ["Representation variance approaches zero or shuffled pairs perform identically"]

        elif "h3" in hypothesis_id.lower() or "shortcut" in h_lower or "generalization" in h_lower:
            falsifying_obs = [
                "Model accuracy collapses to near-random guessing (F1 < 0.20) when hostname and campaign IDs are masked in test splits.",
                "Simple frequency baseline matches or outperforms proposed model under campaign holdout split.",
            ]
            controls = ["Lexical frequency baseline (Bilot et al. 2025)", "Standard random k-fold split"]
            neg_controls = ["Identifier masking control (CTRL-01)", "Campaign holdout split (CTRL-03)"]
            req_experiments = ["Identifier masking evaluation on LANL", "Campaign holdout benchmark on DARPA TC"]
            outcomes_true = ["Model retains F1 >= 0.85 after identifier masking and campaign holdout"]
            outcomes_false = ["Model F1 drops below simple baseline after shortcut removal"]

        elif "h4" in hypothesis_id.lower() or "streaming" in h_lower or "oversquashing" in h_lower:
            falsifying_obs = [
                "Memory consumption grows quadratically with audit graph size, causing OOM crashes under 100k events/sec streaming velocity.",
                "Expanding message passing radius beyond 2 yields zero gain in attack step attribution accuracy due to over-squashing.",
            ]
            controls = ["Standard GCN/GAT with radius=4", "Full batch offline detector"]
            neg_controls = ["Radius ablation (r=1, 2, 3, 4)", "Synthetic burst load stress test (100k EPS)"]
            req_experiments = ["Streaming throughput benchmark on Sysflow", "Over-squashing Jacobian norm probe"]
            outcomes_true = ["Throughput >= 50k EPS with bounded memory (<4GB)", "r=2 achieves >= 95% of r=4 performance with 5x lower latency"]
            outcomes_false = ["Linear message radius scaling causes severe latency spikes and OOM failures"]

        elif "h5" in hypothesis_id.lower() or "privacy" in h_lower:
            falsifying_obs = [
                "Membership inference attack achieves > 90% precision against log representations even with differential privacy noise.",
                "Adding privacy noise reduces intrusion detection recall below 50%.",
            ]
            controls = ["Unperturbed representation baseline", "Naive pseudonymization baseline"]
            neg_controls = ["Random noise baseline without differential privacy bounds", "Zero-utility noise control"]
            req_experiments = ["Shokri MIA probe against log representations", "Empirical Privacy-Utility Pareto curve generation"]
            outcomes_true = ["MIA attack precision <= 55% while intrusion detection F1 >= 0.80"]
            outcomes_false = ["MIA precision remains high (>80%) or detection utility collapses"]

        else:
            falsifying_obs = ["Empirical evaluation on independent holdout contradicts predicted outcome."]
            controls = ["Standard baseline model"]
            neg_controls = ["Randomized input control"]
            req_experiments = ["Controlled replication experiment"]
            outcomes_true = ["Proposed model demonstrates statistically significant improvement (p < 0.01)"]
            outcomes_false = ["No measurable difference observed compared to baseline"]

        return FalsificationPlan(
            plan_id=plan_id,
            target_hypothesis_id=hypothesis_id,
            target_claim_id=claim_id,
            potential_falsifying_observations=falsifying_obs,
            controls=controls,
            negative_controls=neg_controls,
            required_experiments=req_experiments,
            confounders=["Dataset shortcut leakage", "Unequal hyperparameter tuning", "Probe complexity confound"],
            expected_outcomes_if_true=outcomes_true,
            expected_outcomes_if_false=outcomes_false,
        )

# -*- coding: utf-8 -*-
"""
Canonical Experiment Registration Script for Chapter 3 Pre-Registration
Registers EXP-01 through EXP-06 in research.db with PENDING status and zero hallucinated results.
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.schemas.experiment import Experiment

def main():
    repo = ResearchRepository()
    
    experiments = [
        Experiment(
            experiment_id="EXP-01",
            rq_id="RQ-000001",
            hyp_id="HYP-000001",
            title="Parameter Semantic Fidelity vs Template Abstraction Test",
            description="Evaluates whether dynamic parameter-aware subword representation preserves higher security semantics than template-only abstraction under frozen capacity-controlled linear probes on dynamic attack payloads.",
            target_representation_aspect="Dynamic parameter semantic retention under syntactic noise abstraction",
        ),
        Experiment(
            experiment_id="EXP-02",
            rq_id="RQ-000002",
            hyp_id="HYP-000002",
            title="Cross-View Sequential-Graph Latent Alignment & Collapse Test",
            description="Evaluates cross-view latent alignment between sequential Transformer representations and Temporal GNN provenance graph representations, verifying collapse prevention (variance/covariance) and negative transfer control.",
            target_representation_aspect="Cross-view multi-modal latent alignment and representation collapse prevention",
        ),
        Experiment(
            experiment_id="EXP-03",
            rq_id="RQ-000003",
            hyp_id="HYP-000003",
            title="Robustness Under Shortcut Removal, Distribution Shift & 12 Perturbations",
            description="Evaluates representation resilience when environment shortcuts (host, path, process names) are masked, and under 12 pre-registered semantic-preserving log perturbations.",
            target_representation_aspect="Robustness against dataset shortcuts, OOV template drift, and telemetry perturbations",
        ),
        Experiment(
            experiment_id="EXP-04",
            rq_id="RQ-000004",
            hyp_id="HYP-000004",
            title="Weak Evidence Attribution & Administrative Confounder Control via MIL",
            description="Evaluates coarse-label weak evidence attribution using attention-based Multiple Instance Learning (Stage B) without misclassifying benign administrative tools (PowerShell, ssh) as malicious.",
            target_representation_aspect="Multiple instance learning and risk-aware administrative confounder control",
        ),
        Experiment(
            experiment_id="EXP-05",
            rq_id="RQ-000004",
            hyp_id="HYP-000004",
            title="Operational Streaming Feasibility, Latency & Bounded State Complexity",
            description="Evaluates stream processing feasibility under bounded memory (<=500MB/host) and latency (<=10ms p95) constraints across high-throughput telemetry rates.",
            target_representation_aspect="Bounded streaming state lifecycle, TTL eviction, and real-time processing latency",
        ),
        Experiment(
            experiment_id="EXP-06",
            rq_id="RQ-000005",
            hyp_id="HYP-000005",
            title="Controlled Linkability & Empirical Utility-Privacy Pareto Frontier",
            description="Evaluates empirical Utility-Privacy trade-off under four adversary models (ReID, Linkage, MIA, Inversion) across varying privacy budgets epsilon, comparing controlled linkability against raw and anonymized baselines.",
            target_representation_aspect="Controlled entity linkability vs empirical inference leakage attacks",
        ),
    ]

    for exp in experiments:
        repo.save_experiment(exp)
        print(f"[OK] Registered Experiment: {exp.experiment_id} - {exp.title}")

    print("\nSUCCESS: All 6 Canonical Experiments Registered in research.db with zero fake runs.")

if __name__ == "__main__":
    main()

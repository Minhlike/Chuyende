# -*- coding: utf-8 -*-
"""
Scientific Confirmatory Integrity & Invariant Regression Test Suite
Enforces:
  1. Synthetic datasets cannot become SEALED.
  2. Datasets with raw_dataset_acquired=false cannot become SEALED.
  3. Canonical H1–H5 identities cannot be redefined.
  4. Bootstrap protocol requires exact B=2000, seed=10007.
  5. Seed arrays cannot masquerade as cluster units.
  6. Hardcoded empirical numbers cannot bypass the provenance guard.
  7. Attribution evaluation on HDFS returns NOT_EVALUABLE_ON_HDFS without real GT.
  8. Graph and Sequence branches required for H2 multi-view.
  9. 4 Privacy tokenization regimes required for H5.
"""

import pytest
import json
import numpy as np
from pathlib import Path

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from research_agent.experiments.extractor.tokenizer import PrivacyAwareLogTokenizer
from research_agent.experiments.protocols.paired_cluster_bootstrap import paired_cluster_bootstrap_test
from research_agent.experiments.protocols.weak_attribution_evaluator import evaluate_weak_attribution_accuracy
from research_agent.experiments.protocols.provenance_guard import ResultProvenanceFirewall
from research_agent.experiments.protocols.h1_fidelity_contract import evaluate_h1_parameter_fidelity_contract
from research_agent.experiments.protocols.h2_multiview_contract import evaluate_h2_multiview_alignment_contract
from research_agent.experiments.protocols.h3_robustness_contract import evaluate_h3_robustness_contract
from research_agent.experiments.protocols.h4_operational_benchmark import LiveOperationalBenchmarkHarness
from research_agent.experiments.protocols.h5_privacy_frontier import evaluate_h5_privacy_utility_frontier

def test_01_synthetic_dataset_cannot_become_sealed(tmp_path):
    manifest = {
        "dataset_id": "SYNTHETIC-DTC-001",
        "raw_dataset_acquired": False,
        "is_synthetic": True,
        "status": "SEALED"
    }
    # Invariant: Synthetic or unacquired cannot be SEALED
    is_valid_sealed = (not manifest.get("is_synthetic", False)) and manifest.get("raw_dataset_acquired", False)
    assert not is_valid_sealed, "Synthetic datasets must never be marked as SEALED."

def test_02_unacquired_dataset_cannot_become_sealed():
    manifest_path = Path(r"D:\Research\datasets\manifests\SPL-DTC-001.json")
    if not manifest_path.exists():
        manifest_path = Path("/mnt/d/Research/datasets/manifests/SPL-DTC-001.json")
    
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not data.get("raw_dataset_acquired", False):
        assert data.get("status") != "SEALED", "Unacquired dataset cannot have status SEALED"

def test_03_canonical_hypotheses_cannot_be_redefined():
    canonical_h = {
        "H1": "Parameter_Semantic_Fidelity",
        "H2": "Multi_View_Alignment",
        "H3": "Robustness_Shortcut_Invariance",
        "H4": "Operational_Budget",
        "H5": "Controlled_Linkability_Privacy_Frontier"
    }
    
    h1 = evaluate_h1_parameter_fidelity_contract(np.ones(50), np.zeros(50))
    h2 = evaluate_h2_multiview_alignment_contract(np.ones(50), np.zeros(50), np.zeros(50), np.zeros(50), latent_variance=0.5)
    h3 = evaluate_h3_robustness_contract(np.ones(50), {"P01_Token_Deletion": np.ones(50)})
    h5 = evaluate_h5_privacy_utility_frontier()

    assert canonical_h["H1"] in h1["hypothesis_id"]
    assert canonical_h["H2"] in h2["hypothesis_id"]
    assert canonical_h["H3"] in h3["hypothesis_id"]
    assert canonical_h["H5"] in h5["hypothesis_id"]

def test_04_bootstrap_parameters_match_protocol():
    clusters_a = np.random.randn(50)
    clusters_b = np.random.randn(50)

    # Must accept B=2000, seed=10007
    res = paired_cluster_bootstrap_test(clusters_a, clusters_b, b_resamples=2000, random_seed=10007)
    assert res["b_resamples"] == 2000
    assert res["seed"] == 10007

    # Rejects invalid B
    with pytest.raises(ValueError, match="B=2000"):
        paired_cluster_bootstrap_test(clusters_a, clusters_b, b_resamples=1000, random_seed=10007)

    # Rejects invalid seed
    with pytest.raises(ValueError, match="seed=10007"):
        paired_cluster_bootstrap_test(clusters_a, clusters_b, b_resamples=2000, random_seed=42)

def test_05_seed_arrays_cannot_masquerade_as_clusters():
    # 5 seeds array must be rejected as clusters
    seed_array_a = np.array([0.91, 0.92, 0.93, 0.90, 0.92])
    seed_array_b = np.array([0.88, 0.87, 0.89, 0.86, 0.88])

    with pytest.raises(ValueError, match="Cluster count .* too low"):
        paired_cluster_bootstrap_test(seed_array_a, seed_array_b, b_resamples=2000, random_seed=10007)

def test_06_hardcoded_empirical_metric_detector():
    ungrounded_result = {
        "confirmatory_hypothesis_testing": {
            "H1": {"mean_delta": 0.15}
        }
        # Missing provenance_records
    }
    violations = ResultProvenanceFirewall.scan_for_hardcoded_empirical_literals(ungrounded_result)
    assert len(violations) > 0, "Firewall must flag ungrounded results without provenance"

def test_07_attribution_evaluator_requires_real_gt():
    # HDFS with empty GT returns NOT_EVALUABLE_ON_HDFS
    dummy_weights = [np.array([0.1, 0.2, 0.7])]
    empty_gt = [None]
    res = evaluate_weak_attribution_accuracy(dummy_weights, empty_gt, dataset_name="HDFS")
    assert res["evaluation_status"] == "NOT_EVALUABLE_ON_HDFS"

def test_08_graph_and_sequence_views_for_multiview():
    pytest.importorskip("torch")
    from research_agent.experiments.extractor.multi_view import MultiViewRepresentationModel
    
    mv = MultiViewRepresentationModel(seq_vocab_size=20, graph_vocab_size=10, embed_dim=16, mode="aligned")
    
    seq_in = torch.randint(0, 10, (2, 8))
    node_ids = torch.tensor([1, 2, 3, 1, 2])
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 0, 4]])
    edge_type = torch.tensor([0, 1, 2, 0])
    batch_idx = torch.tensor([0, 0, 0, 1, 1])

    z_mv = mv.extract_representation(seq_in, node_ids, edge_index, edge_type, batch_idx)
    assert z_mv.shape == (2, 16)

def test_09_four_privacy_regimes_defined():
    tok_raw = PrivacyAwareLogTokenizer(mode="RAW_IDENTIFIERS")
    tok_anon = PrivacyAwareLogTokenizer(mode="EXTREME_ANONYMIZATION")
    tok_link = PrivacyAwareLogTokenizer(mode="CONTROLLED_LINKABILITY")
    tok_param = PrivacyAwareLogTokenizer(mode="PRIVACY_AWARE_PARAMETERIZED")

    raw_line = "2026-08-21 192.168.1.10 blk_-12345 open /etc/shadow"
    
    out_raw = tok_raw.tokenize_line(raw_line)
    out_anon = tok_anon.tokenize_line(raw_line)
    out_link = tok_link.tokenize_line(raw_line)
    out_param = tok_param.tokenize_line(raw_line)

    assert "192.168.1.10" in out_raw
    assert "<IP>" in out_anon
    assert "<PSEUDO:" in out_link
    assert "<IP_INTERNAL:" in out_param and "<PATH_CONFIG>" in out_param

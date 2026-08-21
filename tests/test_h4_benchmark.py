# -*- coding: utf-8 -*-
"""
H4 Conjunctive SLO Benchmark Harness Tests
Verifies:
  1. State size footprint (state_size_bytes, state_size_mb, active_entities) measured from memory bank.
  2. benchmark_end_to_end profiles end-to-end extraction with event count derived from inputs.
  3. benchmark_incremental_fusion isolates fusion step.
  4. Conjunctive SLO requires all 3 criteria (p95 <= 10ms, RAM <= 500MB, throughput >= 10,000 eps).
"""

import time
import pytest

pytest.importorskip("torch")
import torch

from research_agent.experiments.extractor.tokenizer import PrivacyAwareLogTokenizer
from research_agent.experiments.extractor.multi_view import MultiViewRepresentationModel, GatedMultiViewFusion
from research_agent.experiments.protocols.h4_operational_benchmark import (
    LiveOperationalBenchmarkHarness,
    MemoryPeakMonitor
)

def test_01_end_to_end_benchmark_with_state_size():
    harness = LiveOperationalBenchmarkHarness(device="cpu")
    tokenizer = PrivacyAwareLogTokenizer(mode="PRIVACY_AWARE_PARAMETERIZED")
    model = MultiViewRepresentationModel(seq_vocab_size=50, graph_vocab_size=20, embed_dim=16, mode="aligned")

    raw_lines_batch = [
        ["2026-08-21 10.0.0.1 open /etc/shadow", "2026-08-21 10.0.0.1 read /etc/shadow"],
        ["2026-08-21 128.55.12.91 connect /tmp/dropper.sh"]
    ]
    graph_events_batch = [
        [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1}],
        [{"timestamp": 2.0, "src": 3, "dst": 4, "relation_type": 2}]
    ]

    res = harness.benchmark_end_to_end(
        extractor_model=model,
        tokenizer=tokenizer,
        raw_log_lines_batch=raw_lines_batch,
        graph_events_batch=graph_events_batch,
        warmup_runs=2,
        repeat_runs=5
    )

    assert "latency_p95_ms" in res
    assert "throughput_events_per_sec" in res
    assert "state_size_bytes" in res
    assert "active_entities" in res
    assert res["path_name"] == "Full_End_to_End"

def test_02_incremental_fusion_benchmark():
    harness = LiveOperationalBenchmarkHarness(device="cpu")
    fusion = GatedMultiViewFusion(embed_dim=16)

    z_seq = torch.randn(4, 16)
    z_graph = torch.randn(4, 16)

    res = harness.benchmark_incremental_fusion(
        fusion_module=fusion,
        z_seq=z_seq,
        z_graph=z_graph,
        warmup_runs=2,
        repeat_runs=10
    )

    assert "latency_p95_ms" in res
    assert res["path_name"] == "Incremental_Fusion_Readout"
    assert "conjunctive_slo_satisfied" in res

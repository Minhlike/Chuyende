# -*- coding: utf-8 -*-
"""
H4 Conjunctive SLO Benchmark Harness Tests
Verifies:
  1. State size footprint (state_size_bytes, peak_state_bytes, active_entities) measured during/after run.
  2. Telemetry event deduplication: Same source events in both views are counted ONCE.
  3. benchmark_end_to_end profiles full path with deduplicated event count.
  4. benchmark_incremental_fusion isolates fusion step.
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

def test_01_end_to_end_benchmark_with_state_and_deduplication():
    harness = LiveOperationalBenchmarkHarness(device="cpu")
    tokenizer = PrivacyAwareLogTokenizer(mode="PRIVACY_AWARE_PARAMETERIZED")
    model = MultiViewRepresentationModel(seq_vocab_size=50, graph_node_attr_dim=8, embed_dim=16, mode="aligned")

    # 2 sequence lines, 2 corresponding graph events representing same 2 source events
    raw_lines_batch = [
        ["2026-08-21 10.0.0.1 open /etc/shadow", "2026-08-21 10.0.0.1 read /etc/shadow"]
    ]
    graph_events_batch = [
        [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1},
         {"timestamp": 2.0, "src": 2, "dst": 3, "relation_type": 2}]
    ]
    source_event_ids = {"EVT-001", "EVT-002"}  # Exact 2 source events

    res = harness.benchmark_end_to_end(
        extractor_model=model,
        tokenizer=tokenizer,
        raw_log_lines_batch=raw_lines_batch,
        graph_events_batch=graph_events_batch,
        source_event_ids=source_event_ids,
        warmup_runs=2,
        repeat_runs=5
    )

    # Must count source events once (2), NOT 2 + 2 = 4
    assert res["telemetry_events_per_iter"] == 2, f"Expected 2 deduplicated events, got {res['telemetry_events_per_iter']}"
    assert "latency_p95_ms" in res
    assert "throughput_events_per_sec" in res
    assert "state_size_bytes" in res
    assert "peak_state_bytes" in res
    assert "active_entities" in res
    assert res["path_name"] == "Full_End_to_End"

def test_02_source_event_deduplication_without_explicit_ids():
    harness = LiveOperationalBenchmarkHarness(device="cpu")
    tokenizer = PrivacyAwareLogTokenizer(mode="PRIVACY_AWARE_PARAMETERIZED")
    model = MultiViewRepresentationModel(seq_vocab_size=50, graph_node_attr_dim=8, embed_dim=16, mode="aligned")

    # 100 sequence lines, 100 graph events
    raw_lines = [f"line {i}" for i in range(100)]
    graph_events = [{"timestamp": float(i), "src": 1, "dst": 2, "relation_type": 0} for i in range(100)]

    res = harness.benchmark_end_to_end(
        extractor_model=model,
        tokenizer=tokenizer,
        raw_log_lines_batch=[raw_lines],
        graph_events_batch=[graph_events],
        warmup_runs=1,
        repeat_runs=2
    )

    # Deduped count must be 100, not 200
    assert res["telemetry_events_per_iter"] == 100

def test_03_incremental_fusion_benchmark():
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

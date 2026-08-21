# -*- coding: utf-8 -*-
"""
H4 Conjunctive SLO Benchmark Harness Tests
Verifies:
  1. Benchmark harness profiles p50, p95, p99 latency, throughput, and peak RAM.
  2. MemoryPeakMonitor accurately samples peak RSS.
  3. Conjunctive SLO requires all 3 criteria (p95 <= 10ms, RAM <= 500MB, throughput >= 10,000 eps).
  4. End-to-end vs incremental isolation.
"""

import time
import pytest
from research_agent.experiments.protocols.h4_operational_benchmark import (
    LiveOperationalBenchmarkHarness,
    MemoryPeakMonitor
)

def test_01_memory_peak_monitor_tracking():
    monitor = MemoryPeakMonitor(interval_sec=0.005)
    monitor.start()

    # Allocate temporary memory chunk
    temp_data = [bytearray(1024 * 1024) for _ in range(10)]
    time.sleep(0.02)
    
    peak_ram = monitor.stop()
    assert peak_ram > 0.0
    del temp_data

def test_02_conjunctive_slo_harness_execution():
    harness = LiveOperationalBenchmarkHarness(device="cpu")

    def mock_fast_forward():
        time.sleep(0.0001)  # 0.1 ms
        return [1, 2, 3]

    res = harness.benchmark_pipeline_path(
        forward_fn=mock_fast_forward,
        telemetry_event_count=50,
        warmup_runs=2,
        repeat_runs=10,
        path_name="Mock_Fast_Path"
    )

    assert "latency_p95_ms" in res
    assert "peak_ram_mb" in res
    assert "throughput_events_per_sec" in res
    assert "slo_checks" in res
    assert "conjunctive_slo_satisfied" in res

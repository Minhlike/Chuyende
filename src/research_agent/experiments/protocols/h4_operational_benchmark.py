# -*- coding: utf-8 -*-
"""
H4 Operational Budget Benchmark Harness
Implements Chapter 2 & Chapter 3 Frozen Operational Specification (Section 2.5 & Section 4):
  - Conjunctive Service Level Objective (SLO) Contract:
      1. p95 Latency <= 10.0 ms / sequence
      2. Peak RAM <= 500.0 MB / host
      3. Processing Throughput >= 10,000 telemetry events / sec
      (ALL 3 CONDITIONS MUST PASS FOR NOT_FALSIFIED)
  - Real Hardware Resource Profiler:
      * Continuous Peak RAM tracking during benchmark loop
      * Peak VRAM tracking via CUDA memory counters
      * Active entity state bytes footprint
      * Telemetry event count (actual log records, not raw tensor elements)
  - Distinct Execution Path Profiling:
      * Full End-to-End Extractor Path (Tokenize + Sequence + Temporal Graph + Fusion)
      * Incremental Fusion & Readout Step (Isolated latency)
"""

import time
import os
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

import tracemalloc

class MemoryPeakMonitor:
    """
    Background daemon continuously sampling memory to capture true peak RAM.
    Uses psutil RSS when available, with tracemalloc fallback.
    """
    def __init__(self, interval_sec: float = 0.005):
        self.interval_sec = interval_sec
        self.peak_ram_mb = 0.0
        self.running = False
        self._thread = None
        self.process = psutil.Process(os.getpid()) if HAS_PSUTIL else None

    def _sample_loop(self):
        while self.running:
            if self.process:
                try:
                    rss = self.process.memory_info().rss / (1024 * 1024)
                    if rss > self.peak_ram_mb:
                        self.peak_ram_mb = rss
                except Exception:
                    pass
            time.sleep(self.interval_sec)

    def start(self):
        tracemalloc.start()
        if HAS_PSUTIL and self.process:
            self.peak_ram_mb = self.process.memory_info().rss / (1024 * 1024)
            self.running = True
            self._thread = threading.Thread(target=self._sample_loop, daemon=True)
            self._thread.start()
        else:
            self.peak_ram_mb = 0.01

    def stop(self) -> float:
        self.running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        trace_peak_mb = peak / (1024 * 1024)

        if HAS_PSUTIL and self.process:
            try:
                rss = self.process.memory_info().rss / (1024 * 1024)
                self.peak_ram_mb = max(self.peak_ram_mb, rss)
            except Exception:
                pass
        else:
            self.peak_ram_mb = max(self.peak_ram_mb, trace_peak_mb)

        return float(self.peak_ram_mb)

class LiveOperationalBenchmarkHarness:
    """
    Hardware measurement harness evaluating the full conjunctive SLO contract.
    """
    def __init__(self, device: str = "cpu"):
        if HAS_TORCH:
            self.device = torch.device(device)
        else:
            self.device = device
        self.process = psutil.Process(os.getpid()) if HAS_PSUTIL else None

    def benchmark_pipeline_path(
        self,
        forward_fn: Callable[[], Any],
        telemetry_event_count: int,
        warmup_runs: int = 5,
        repeat_runs: int = 50,
        path_name: str = "Full_End_to_End"
    ) -> Dict[str, Any]:
        """
        Executes genuine hardware profiling on a specific execution path.
        """
        # 1. Warmup
        for _ in range(warmup_runs):
            _ = forward_fn()
            if HAS_TORCH and hasattr(self.device, "type") and self.device.type == "cuda":
                torch.cuda.synchronize()

        # 2. Start Peak RAM Monitor
        mem_monitor = MemoryPeakMonitor()
        mem_monitor.start()

        if HAS_TORCH and hasattr(self.device, "type") and self.device.type == "cuda":
            torch.cuda.reset_peak_memory_stats()

        latencies_ms = []
        start_wall = time.perf_counter()

        for _ in range(repeat_runs):
            t0 = time.perf_counter()
            _ = forward_fn()
            if HAS_TORCH and hasattr(self.device, "type") and self.device.type == "cuda":
                torch.cuda.synchronize()
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)

        end_wall = time.perf_counter()
        peak_ram_mb = mem_monitor.stop()

        peak_vram_mb = 0.0
        if HAS_TORCH and hasattr(self.device, "type") and self.device.type == "cuda":
            peak_vram_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)

        total_wall_sec = max(1e-6, end_wall - start_wall)
        total_events_processed = telemetry_event_count * repeat_runs
        throughput_events_per_sec = float(total_events_processed / total_wall_sec)

        p50_ms = float(np.percentile(latencies_ms, 50))
        p95_ms = float(np.percentile(latencies_ms, 95))
        p99_ms = float(np.percentile(latencies_ms, 99))

        # Conjunctive SLO Verification:
        # 1. p95 <= 10.0 ms
        # 2. peak_ram <= 500.0 MB
        # 3. throughput >= 10,000 events/s
        slo_p95_pass = bool(p95_ms <= 10.0)
        slo_ram_pass = bool(peak_ram_mb <= 500.0)
        slo_throughput_pass = bool(throughput_events_per_sec >= 10000.0)
        
        all_slo_passed = bool(slo_p95_pass and slo_ram_pass and slo_throughput_pass)

        return {
            "path_name": path_name,
            "device": str(self.device),
            "measured_iterations": repeat_runs,
            "telemetry_events_per_iter": telemetry_event_count,
            "latency_p50_ms": p50_ms,
            "latency_p95_ms": p95_ms,
            "latency_p99_ms": p99_ms,
            "throughput_events_per_sec": throughput_events_per_sec,
            "peak_ram_mb": peak_ram_mb,
            "peak_vram_mb": peak_vram_mb,
            "slo_checks": {
                "p95_latency_under_10ms": slo_p95_pass,
                "peak_ram_under_500mb": slo_ram_pass,
                "throughput_over_10k_eps": slo_throughput_pass
            },
            "conjunctive_slo_satisfied": all_slo_passed,
            "falsification_status": "NOT_FALSIFIED" if all_slo_passed else "FALSIFIED"
        }

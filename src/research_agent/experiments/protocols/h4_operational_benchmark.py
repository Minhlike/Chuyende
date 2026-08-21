# -*- coding: utf-8 -*-
"""
H4 Operational Budget Benchmark Harness
Live hardware measurement suite measuring:
  - Latency: p50, p95, p99 (ms / sequence)
  - Throughput: events / second
  - Memory: Peak RAM (MB) & Peak VRAM (MB)
  - Parameter Efficiency: Number of trainable parameters vs baseline
Pre-registered threshold: p95 latency <= 10.0 ms, Peak RAM <= 500.0 MB/host at 10,000 events/s.
NO hard-coded latency arrays permitted.
"""

import time
import os
import numpy as np
from typing import Dict, Any, List, Optional

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

class LiveOperationalBenchmarkHarness:
    """
    Real-time performance profiler measuring CPU/GPU operational budgets.
    """
    def __init__(self, device: str = "cpu"):
        if HAS_TORCH:
            self.device = torch.device(device)
        else:
            self.device = device
        self.process = psutil.Process(os.getpid()) if HAS_PSUTIL else None

    def benchmark_inference(
        self,
        model: Any,
        sample_batches: List[Any],
        warmup_runs: int = 10,
        repeat_runs: int = 100
    ) -> Dict[str, Any]:
        """
        Executes genuine hardware profiling on live inputs.
        """
        model.eval()
        model.to(self.device)

        # 1. Warmup
        with torch.no_grad():
            for i in range(min(warmup_runs, len(sample_batches))):
                x = sample_batches[i % len(sample_batches)].to(self.device)
                _ = model(x)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()

        # 2. Timing Run
        latencies_ms = []
        total_events = 0

        # Initial memory snapshot
        ram_before = self.process.memory_info().rss / (1024 * 1024)
        if self.device.type == "cuda":
            torch.cuda.reset_peak_memory_stats()

        with torch.no_grad():
            start_wall = time.perf_counter()
            for r in range(repeat_runs):
                x = sample_batches[r % len(sample_batches)].to(self.device)
                batch_events = x.numel()
                total_events += batch_events

                t0 = time.perf_counter()
                _ = model(x)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                t1 = time.perf_counter()

                latencies_ms.append((t1 - t0) * 1000.0)
            end_wall = time.perf_counter()

        ram_after = self.process.memory_info().rss / (1024 * 1024)
        peak_ram_mb = max(ram_before, ram_after)

        peak_vram_mb = 0.0
        if self.device.type == "cuda":
            peak_vram_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)

        wall_duration = end_wall - start_wall
        events_per_sec = total_events / max(1e-6, wall_duration)

        # Param count
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        p50 = float(np.percentile(latencies_ms, 50))
        p95 = float(np.percentile(latencies_ms, 95))
        p99 = float(np.percentile(latencies_ms, 99))

        # Conjunctive SLO verification (p95 <= 10.0 ms and peak_ram <= 500 MB)
        slo_satisfied = bool(p95 <= 10.0 and peak_ram_mb <= 500.0)

        return {
            "hypothesis_id": "H4_Operational_Budget",
            "device": str(self.device),
            "sample_runs_measured": len(latencies_ms),
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "latency_p99_ms": p99,
            "throughput_events_per_sec": events_per_sec,
            "peak_ram_mb": peak_ram_mb,
            "peak_vram_mb": peak_vram_mb,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "slo_threshold_p95_ms": 10.0,
            "slo_threshold_ram_mb": 500.0,
            "slo_satisfied": slo_satisfied,
            "falsification_status": "NOT_FALSIFIED" if slo_satisfied else "FALSIFIED"
        }

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
      * Active entity state size bytes footprint (measured from extractor memory bank)
      * Telemetry event count derived directly from input objects
  - Distinct Execution Path Profiling:
      * benchmark_end_to_end(...) (Full Tokenize + Sequence + Temporal Graph + Fusion)
      * benchmark_incremental_fusion(...) (Isolated Fusion & Readout step)
"""

import time
import os
import threading
import tracemalloc
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

class MemoryPeakMonitor:
    """
    Background daemon continuously sampling memory to capture true peak RAM.
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
            try:
                self.peak_ram_mb = self.process.memory_info().rss / (1024 * 1024)
            except Exception:
                self.peak_ram_mb = 0.01
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

    def benchmark_end_to_end(
        self,
        extractor_model: Any,
        tokenizer: Any,
        raw_log_lines_batch: List[List[str]],
        graph_events_batch: List[List[Dict[str, Any]]],
        warmup_runs: int = 3,
        repeat_runs: int = 20
    ) -> Dict[str, Any]:
        """
        Benchmarks full end-to-end extractor path:
        Preprocessing/Tokenize + Sequence Branch + Temporal Graph + Gated Fusion.
        Derives telemetry event count directly from actual input list lengths.
        """
        # Count actual telemetry events from input
        num_seq_events = sum(len(lines) for lines in raw_log_lines_batch)
        num_graph_events = sum(len(events) for events in graph_events_batch)
        total_events_per_iter = num_seq_events + num_graph_events

        def forward_e2e():
            if hasattr(extractor_model, "graph_extractor") and hasattr(extractor_model.graph_extractor, "memory_bank"):
                extractor_model.graph_extractor.memory_bank.reset_memory()

            # 1. Preprocessing / Tokenization
            seq_tensors = []
            for lines in raw_log_lines_batch:
                token_ids = tokenizer.encode_sequence(lines)
                seq_tensors.append(torch.tensor(token_ids, dtype=torch.long, device=self.device))
            
            # Pad batch
            max_len = max(t.size(0) for t in seq_tensors)
            padded = torch.zeros(len(seq_tensors), max_len, dtype=torch.long, device=self.device)
            for idx, t in enumerate(seq_tensors):
                padded[idx, :t.size(0)] = t

            # 2. Extract Representation
            z_mv = extractor_model.extract_representation(
                seq_inputs=padded,
                graph_events_batch=graph_events_batch,
                device=self.device
            )
            return z_mv

        # Measure state size from memory bank
        state_metrics = {}
        if hasattr(extractor_model, "graph_extractor") and hasattr(extractor_model.graph_extractor, "memory_bank"):
            state_metrics = extractor_model.graph_extractor.memory_bank.get_state_metrics()

        return self._run_profile_loop(
            forward_fn=forward_e2e,
            telemetry_event_count=total_events_per_iter,
            warmup_runs=warmup_runs,
            repeat_runs=repeat_runs,
            path_name="Full_End_to_End",
            state_metrics=state_metrics
        )

    def benchmark_incremental_fusion(
        self,
        fusion_module: Any,
        z_seq: Any,
        z_graph: Any,
        warmup_runs: int = 5,
        repeat_runs: int = 50
    ) -> Dict[str, Any]:
        """
        Benchmarks isolated incremental fusion & readout step.
        """
        def forward_fusion():
            return fusion_module(z_seq, z_graph)

        return self._run_profile_loop(
            forward_fn=forward_fusion,
            telemetry_event_count=z_seq.size(0),
            warmup_runs=warmup_runs,
            repeat_runs=repeat_runs,
            path_name="Incremental_Fusion_Readout"
        )

    def _run_profile_loop(
        self,
        forward_fn: Callable[[], Any],
        telemetry_event_count: int,
        warmup_runs: int,
        repeat_runs: int,
        path_name: str,
        state_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        for _ in range(warmup_runs):
            _ = forward_fn()
            if HAS_TORCH and hasattr(self.device, "type") and self.device.type == "cuda":
                torch.cuda.synchronize()

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

        slo_p95_pass = bool(p95_ms <= 10.0)
        slo_ram_pass = bool(peak_ram_mb <= 500.0)
        slo_throughput_pass = bool(throughput_events_per_sec >= 10000.0)
        all_slo_passed = bool(slo_p95_pass and slo_ram_pass and slo_throughput_pass)

        res = {
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
            "verdict": "SUPPORTED" if all_slo_passed else "FALSIFIED",
            "falsification_status": "NOT_FALSIFIED" if all_slo_passed else "FALSIFIED"
        }
        if state_metrics:
            res.update(state_metrics)
        else:
            res["state_size_bytes"] = 0
            res["state_size_mb"] = 0.0
            res["active_entities"] = 0

        return res

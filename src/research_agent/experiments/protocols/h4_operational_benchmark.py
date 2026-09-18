# -*- coding: utf-8 -*-
"""
bộ khung benchmark ngân sách hoạt động H4
Triển khai Đặc tả hoạt động đóng băng (frozen) Chương 2 & Chương 3 (Phần 2.5 & Phần 4):
  - Hợp đồng mục tiêu cấp độ dịch vụ kết hợp (SLO):
      1. p95 Độ trễ <= 10,0 ms/chuỗi
      2. Đỉnh RAM <= 500,0 MB/máy chủ
      3. Thông lượng xử lý >= 10.000 sự kiện đo từ xa/giây
      (ALL 3 CONDITIONS MUST PASS FOR NOT_FALSIFIED)
  - Trình phân tích tài nguyên phần cứng thực:
      * Theo dõi RAM đỉnh liên tục trong vòng lặp điểm chuẩn
      * Theo dõi đỉnh VRAM qua bộ đếm bộ nhớ CUDA
      * Kích thước byte trạng thái thực thể hoạt động và byte trạng thái cao nhất được đo trong/sau khi chạy
      * Số lượng sự kiện đo từ xa được loại bỏ khỏi các đơn vị quan sát nguồn thực tế
  - Hồ sơ đường dẫn thực thi riêng biệt:
      * benchmark_end_to_end(...) (token đầy đủ + Trình tự + Biểu đồ thời gian + Kết hợp)
      * benchmark_incremental_fusion(...) (Bước kết hợp & đọc tách biệt)
"""

import time
import os
import threading
import tracemalloc
from typing import Dict, Any, List, Optional, Tuple, Callable, Set
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
    Trình nền nền liên tục lấy mẫu bộ nhớ để ghi lại đỉnh RAM thực sự.
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
    Khai thác đo lường phần cứng đánh giá hợp đồng SLO đầy đủ.
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
        source_event_ids: Optional[Set[Any]] = None,
        warmup_runs: int = 3,
        repeat_runs: int = 20
    ) -> Dict[str, Any]:
        """
        Điểm chuẩn đường dẫn trích xuất từ ​​đầu đến cuối đầy đủ.
        Loại bỏ các sự kiện đo từ xa nguồn trùng lặp: nếu góc nhìn (view) trình tự và biểu đồ thể hiện giống nhau
        các sự kiện đo từ xa cơ bản, đếm từng đơn vị quan sát nguồn ONCE.
        """
        if source_event_ids is not None:
            telemetry_event_count = len(source_event_ids)
        else:
            num_seq = sum(len(lines) for lines in raw_log_lines_batch)
            num_graph = sum(len(events) for events in graph_events_batch)
            # Khi các biểu diễn đa góc nhìn (multi-view) tương ứng phản ánh cùng một phiên nhật ký, hãy đếm các sự kiện chuẩn một lần
            telemetry_event_count = max(num_seq, num_graph)

        def forward_e2e():
            if hasattr(extractor_model, "graph_extractor") and hasattr(extractor_model.graph_extractor, "memory_bank"):
                extractor_model.graph_extractor.memory_bank.reset_memory()

            seq_tensors = []
            for lines in raw_log_lines_batch:
                token_ids = tokenizer.encode_sequence(lines)
                seq_tensors.append(torch.tensor(token_ids, dtype=torch.long, device=self.device))
            
            max_len = max(t.size(0) for t in seq_tensors)
            padded = torch.zeros(len(seq_tensors), max_len, dtype=torch.long, device=self.device)
            for idx, t in enumerate(seq_tensors):
                padded[idx, :t.size(0)] = t

            z_mv = extractor_model.extract_representation(
                seq_inputs=padded,
                graph_events_batch=graph_events_batch,
                device=self.device
            )
            return z_mv

        res = self._run_profile_loop(
            forward_fn=forward_e2e,
            telemetry_event_count=telemetry_event_count,
            warmup_runs=warmup_runs,
            repeat_runs=repeat_runs,
            path_name="Full_End_to_End"
        )

        # Đo số liệu trạng thái trong/sau khi chạy từ ngân hàng bộ nhớ hoạt động
        if hasattr(extractor_model, "graph_extractor") and hasattr(extractor_model.graph_extractor, "memory_bank"):
            state_metrics = extractor_model.graph_extractor.memory_bank.get_state_metrics()
            res.update(state_metrics)

        return res

    def benchmark_incremental_fusion(
        self,
        fusion_module: Any,
        z_seq: Any,
        z_graph: Any,
        warmup_runs: int = 5,
        repeat_runs: int = 50
    ) -> Dict[str, Any]:
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
        path_name: str
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
            "falsification_status": "NOT_FALSIFIED" if all_slo_passed else "FALSIFIED",
            "state_size_bytes": 0,
            "peak_state_bytes": 0,
            "state_size_mb": 0.0,
            "peak_state_mb": 0.0,
            "active_entities": 0,
            "peak_active_entities": 0
        }

        return res

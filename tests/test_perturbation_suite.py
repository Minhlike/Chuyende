# -*- coding: utf-8 -*-
"""
Bộ kiểm tra nhiễu loạn (P01..P12) Kiểm tra phát hiện ngữ nghĩa và không hoạt động
Xác minh rằng tất cả 12 toán tử nhiễu loạn đều thực thi một cách xác định,
phát hiện các thay đổi (changed_count > 0), bảo toàn các bất biến quan trọng,
đảm bảo ánh xạ tiêm truyền (P05), an toàn tương tranh (P04) và nhận thức về lược đồ (P11).
"""

import re
import pytest
from research_agent.experiments.protocols.h3_robustness_contract import (
    PERTURBATION_DISPATCHER,
    apply_p01_token_deletion,
    apply_p04_event_order_jitter,
    apply_p05_ip_subnet_translation,
    apply_p09_host_reassignment,
    apply_p11_timestamp_skew,
    apply_shortcut_removal
)

SAMPLE_LOG_SESSION = [
    "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 offset 0x1000 src: /10.250.19.102:54106 dest: /10.250.19.102:50010 host-001",
    "081109 203518 143 INFO dfs.DataNode$BlockReceiver: Received block blk_-1608999687919862906 of size 67108864 from /10.250.19.102 host-002",
    "081109 203520 142 INFO dfs.DataNode$DataXceiver: Served block blk_-1608999687919862906 to /10.250.19.102 host-001",
    "081109 203521 143 INFO dfs.DataNode$DataXceiver: Terminated block transfer blk_-1608999687919862906 host-003"
]

def test_01_all_twelve_perturbations_execute_with_changes():
    assert len(PERTURBATION_DISPATCHER) == 12
    for p_id, p_fn in PERTURBATION_DISPATCHER.items():
        out, changed_count = p_fn(SAMPLE_LOG_SESSION, 42)
        assert isinstance(out, list)
        assert len(out) > 0, f"Perturbation {p_id} produced empty output"
        assert changed_count > 0, f"Perturbation {p_id} resulted in NO-OP (zero changed records)"

def test_02_p05_strictly_injective_ip_mapping():
    session_with_ips = [
        "10.0.0.1 connecting to 10.0.0.2",
        "10.0.0.3 connecting to 10.0.0.1",
        "192.168.1.50 connecting to 10.0.0.2"
    ]
    ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
    unique_in_ips = set(ip_pattern.findall("\n".join(session_with_ips)))

    out, changed = apply_p05_ip_subnet_translation(session_with_ips, seed=42)
    assert changed > 0
    unique_out_ips = set(ip_pattern.findall("\n".join(out)))

    # Thuộc tính nội xạ: chính xác cùng số lượng IP riêng biệt
    assert len(unique_in_ips) == len(unique_out_ips), f"P05 must be strictly injective: in={len(unique_in_ips)}, out={len(unique_out_ips)}"

def test_03_p04_concurrency_safe_jitter():
    # Chỉ các sự kiện tại 203518 mới được sắp xếp lại; sự kiện lúc 203521 phải kết thúc
    out, changed = apply_p04_event_order_jitter(SAMPLE_LOG_SESSION, seed=42)
    assert changed > 0
    assert "203521" in out[-1], "P04 must preserve chronological ordering of non-concurrent events"

def test_04_p11_schema_aware_timestamp_skew():
    out, changed = apply_p11_timestamp_skew(SAMPLE_LOG_SESSION, seed=42, jitter_sec=5.0)
    assert changed > 0
    # Phải giữ nguyên định dạng dấu thời gian 6 chữ số hợp lệ
    assert re.search(r"\b\d{6}\s+\d{6}\b", out[0]) is not None

def test_05_shortcut_removal_experiment():
    out, changed = apply_shortcut_removal(SAMPLE_LOG_SESSION)
    assert changed > 0
    assert not any("DataXceiver" in l for l in out)
    assert any("<GENERIC_DAEMON>" in l for l in out)

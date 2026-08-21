# -*- coding: utf-8 -*-
"""
Perturbation Suite (P01..P12) Semantic & No-Op Detection Tests
Verifies that all 12 perturbation operators execute deterministically,
detect changes (changed_count > 0), preserve critical invariants,
and executes shortcut removal.
"""

import pytest
from research_agent.experiments.protocols.h3_robustness_contract import (
    PERTURBATION_DISPATCHER,
    apply_p01_token_deletion,
    apply_p05_ip_subnet_translation,
    apply_p09_host_reassignment,
    apply_shortcut_removal
)

SAMPLE_LOG_SESSION = [
    "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 offset 0x1000 src: /10.250.19.102:54106 dest: /10.250.19.102:50010 host-001",
    "081109 203519 143 INFO dfs.DataNode$BlockReceiver: Received block blk_-1608999687919862906 of size 67108864 from /10.250.19.102 host-002",
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

def test_02_collision_safe_host_reassignment():
    out, changed = apply_p09_host_reassignment(SAMPLE_LOG_SESSION, seed=42)
    assert changed > 0
    # Different hosts must map to different worker nodes
    assert "worker-node-001" in out[0]
    assert "worker-node-002" in out[1]
    assert "worker-node-003" in out[3]

def test_03_shortcut_removal_experiment():
    out, changed = apply_shortcut_removal(SAMPLE_LOG_SESSION)
    assert changed > 0
    assert not any("DataXceiver" in l for l in out)
    assert any("<GENERIC_DAEMON>" in l for l in out)

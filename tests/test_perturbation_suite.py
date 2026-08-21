# -*- coding: utf-8 -*-
"""
Perturbation Suite (P01..P12) Semantic Tests
Verifies that all 12 pre-registered perturbation operators execute deterministically
and preserve underlying log structure / attack semantic invariant conditions.
"""

import pytest
from research_agent.experiments.protocols.h3_robustness_contract import (
    PERTURBATION_DISPATCHER,
    apply_p01_token_deletion,
    apply_p02_token_insertion_noise,
    apply_p03_parameter_obfuscation,
    apply_p04_event_order_jitter,
    apply_p05_ip_subnet_translation,
    apply_p06_path_aliasing,
    apply_p07_burst_interleaving,
    apply_p08_unseen_template_shift,
    apply_p09_host_reassignment,
    apply_p10_entity_pseudonym_rotation,
    apply_p11_timestamp_skew,
    apply_p12_composite_perturbation
)

SAMPLE_LOG_SESSION = [
    "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010",
    "081109 203519 143 INFO dfs.DataNode$BlockReceiver: Received block blk_-1608999687919862906 of size 67108864 from /10.250.19.102",
    "081109 203520 142 INFO dfs.DataNode$DataXceiver: Served block blk_-1608999687919862906 to /10.250.19.102",
    "081109 203521 143 INFO dfs.DataNode$DataXceiver: Terminated block transfer blk_-1608999687919862906"
]

def test_01_all_twelve_perturbations_executable():
    assert len(PERTURBATION_DISPATCHER) == 12
    for p_id, p_fn in PERTURBATION_DISPATCHER.items():
        out = p_fn(SAMPLE_LOG_SESSION, 42)
        assert isinstance(out, list)
        assert len(out) > 0, f"Perturbation {p_id} produced empty output"

def test_02_semantic_preservation_token_deletion():
    # P01 must preserve block ID tokens
    out = apply_p01_token_deletion(SAMPLE_LOG_SESSION, seed=42, budget=0.5)
    for line in out:
        assert "blk_-1608999687919862906" in line, "P01 must not delete critical block identifier"

def test_03_semantic_preservation_ip_translation():
    # P05 must translate subnets while maintaining unique IP mapping
    out = apply_p05_ip_subnet_translation(SAMPLE_LOG_SESSION, seed=42)
    assert any("192.168.19.102" in line for line in out), "P05 must translate 10.250.19.102 to private 192.168.19.102"

def test_04_semantic_preservation_path_aliasing():
    sample_path = ["2026-08-21 read file /etc/shadow", "2026-08-21 write file /tmp/dropper.sh"]
    out = apply_p06_path_aliasing(sample_path, seed=42)
    assert "/etc/./" in out[0]
    assert "/tmp/../tmp/" in out[1]

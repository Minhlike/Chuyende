# -*- coding: utf-8 -*-
"""
Unit tests for Stage A2 Graph Contract Schema and Pre-Execution Invariants.
"""

import json
import pytest
import hashlib
from pathlib import Path

def test_stage_a2_graph_contract_schema_valid():
    base_dir = Path("D:/Research")
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    assert contract_path.exists(), "Graph contract file must exist"
    
    data = json.loads(contract_path.read_text(encoding="utf-8"))
    assert data["contract_id"] == "SCHEMA-STAGE-A2-GRAPH-CONTRACT-V1"
    assert data["causality_invariants"]["predict_before_update"]["enforced"] is True
    assert data["causality_invariants"]["future_neighbor_firewall"]["enforced"] is True
    assert data["causality_invariants"]["split_memory_boundary_policy"]["canonical_policy"] == "INDUCTIVE_SPLIT_RESET_ZERO_MEMORY"
    assert data["causality_invariants"]["negative_sampling"]["algorithm"] == "CAUSAL_UNIFORM_SAMPLED_HISTORICAL_DESTINATION"
    assert data["privacy_and_firewall"]["test_opened_invariant"] is False


def test_stage_a2_preexecution_verifier_passes():
    from scripts.verify_stage_a2_preexecution import verify_stage_a2_preexecution
    # Must exit cleanly with 0
    try:
        verify_stage_a2_preexecution()
    except SystemExit as e:
        assert e.code == 0, f"Verifier failed with exit code {e.code}"

# -*- coding: utf-8 -*-
"""
Tests for STAGE-A2-SEED42-FRESH-CANONICAL.ipynb Google Colab Notebook.
Verifies all 11 structural and behavioral invariants.
"""

import json
import ast
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = REPO_ROOT / "notebooks" / "STAGE-A2-SEED42-FRESH-CANONICAL.ipynb"
EXPECTED_COMMIT = "c6d9805ae4dd9d3f6740222ec1eb3ec98554aeb6"
EXPECTED_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
EXPECTED_OLD_CHECKPOINT_SHA = "cac60f9f64c1e0ccbf87cc326aef384df31d0784a1225bea89ac0d108f29d372"

def test_notebook_file_exists():
    assert NOTEBOOK_PATH.exists(), f"Notebook missing at {NOTEBOOK_PATH}"

def test_notebook_json_valid():
    content = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    assert "cells" in content
    assert "metadata" in content
    assert content["nbformat"] == 4

def test_notebook_has_exactly_four_code_cells():
    content = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    code_cells = [c for c in content["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 4, f"Expected 4 code cells, got {len(code_cells)}"

def test_all_code_cells_compile_cleanly():
    content = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    code_cells = [c for c in content["cells"] if c["cell_type"] == "code"]
    for idx, cell in enumerate(code_cells, 1):
        source = "".join(cell["source"])
        compiled = compile(source, f"cell_{idx}", "exec")
        assert compiled is not None

def test_no_prohibited_resume_flag():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert "--resume" not in text

def test_exactly_one_real_execution_flag():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert text.count("--authorize-real-empirical-execution") == 1

def test_execution_commit_matches_approved_fix_commit():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert EXPECTED_COMMIT in text

def test_hdfs_sha_matches_raw_dataset():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert EXPECTED_HDFS_SHA in text

def test_canonical_durable_root_matches_drive_path():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert "/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS" in text

def test_forensic_archive_and_old_checkpoint_sha_present():
    text = NOTEBOOK_PATH.read_text(encoding="utf-8")
    assert "seed-42-forensic-noncanonical-" in text
    assert EXPECTED_OLD_CHECKPOINT_SHA in text
    assert "NONCANONICAL_RNG_INITIALIZATION" in text

def test_zero_real_optimizer_steps_during_preflight():
    content = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    cell3_source = "".join(content["cells"][3]["source"])
    assert "--dry-run" in cell3_source
    assert "OptimizerStepsExecuted=0" in cell3_source or "Optimizer Steps Executed: 0" in cell3_source

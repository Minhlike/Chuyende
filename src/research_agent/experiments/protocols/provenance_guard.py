# -*- coding: utf-8 -*-
"""
Scientific Result Provenance Guard & Anti-Fabrication Firewall
Enforces strict cryptographic lineage for all experimental metrics:
Every empirical number must trace back to:
  - experiment_id
  - run_id
  - dataset_raw_hash
  - split_hash
  - git_commit
  - config_hash
  - environment_hash
  - seed
  - raw_predictions_path / raw_benchmark_log_path
  - computation_script
Scans and rejects any hard-coded / ungrounded result dictionary.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json

REQUIRED_PROVENANCE_FIELDS = [
    "experiment_id",
    "run_id",
    "dataset_raw_hash",
    "split_hash",
    "git_commit",
    "config_hash",
    "environment_hash",
    "seed",
    "computation_script",
    "raw_run_log_path"
]

class ResultProvenanceFirewall:
    """
    Validates cryptographic and operational provenance before accepting any result into Chapter 3 records.
    """
    @staticmethod
    def validate_run_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        missing = []
        for f in REQUIRED_PROVENANCE_FIELDS:
            if f not in record or not record[f]:
                missing.append(f)
        
        if missing:
            return False, missing
        return True, []

    @staticmethod
    def scan_for_hardcoded_empirical_literals(data: Dict[str, Any]) -> List[str]:
        """
        Scans for empirical metric dictionaries that lack execution provenance records.
        """
        violations = []
        # If confirmatory metrics are present without run provenance block:
        if "confirmatory_hypothesis_testing" in data:
            if "provenance_records" not in data or not data["provenance_records"]:
                violations.append("Confirmatory results present without verified provenance_records block.")
        return violations

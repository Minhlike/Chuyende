# -*- coding: utf-8 -*-
"""
Tests for scripts/validate_experiment_index.py
Includes positive verification and negative tests verifying that tampering with CSV hash or availability fails.
"""

import unittest
import tempfile
import csv
from pathlib import Path
from scripts.validate_experiment_index import validate_experiment_index, validate_artifact_manifest


class TestExperimentIndexValidator(unittest.TestCase):
    def test_positive_validation(self):
        """Standard repository files must pass validation 100%."""
        self.assertTrue(validate_experiment_index(), "Expected standard experiment_index.csv to pass")
        self.assertTrue(validate_artifact_manifest(), "Expected standard ARTIFACT-MANIFEST.json to pass")

    def test_negative_tampered_hash_fails(self):
        """Tampering with a single character in manifest_sha256 must be detected and fail."""
        repo_root = Path(__file__).resolve().parent.parent
        original_csv = repo_root / "experiments" / "experiment_index.csv"

        with open(original_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        # Intentionally tamper with the first character of row 0 manifest_sha256
        old_hash = rows[0]["manifest_sha256"]
        tampered_hash = ("0" if old_hash[0] != "0" else "1") + old_hash[1:]
        rows[0]["manifest_sha256"] = tampered_hash

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".csv", newline="") as tf:
            writer = csv.DictWriter(tf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            temp_csv_path = Path(tf.name)

        try:
            # Pass relative or absolute path to validator
            rel_temp = temp_csv_path.relative_to(repo_root) if temp_csv_path.is_relative_to(repo_root) else str(temp_csv_path)
            result = validate_experiment_index(csv_path=str(temp_csv_path))
            self.assertFalse(result, "Validator should have FAILED on tampered manifest_sha256!")
        finally:
            if temp_csv_path.exists():
                temp_csv_path.unlink()


if __name__ == "__main__":
    unittest.main()

"""
Multi-Tier Scientific Reproduction Runner (Prompt 6 Sections 80..82)
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from research_agent.core.enums import ReproducibilityLevel


class ReproductionRunner:
    """
    Executes reproduction workflows across the 5 standard tiers:
    - Level 1: Hash integrity of existing artifacts.
    - Level 2: Metric recomputation from saved prediction files.
    - Level 3: Statistical analysis & table/figure regeneration from metric logs.
    - Level 4: Rerun model inference on test split with locked checkpoints.
    - Level 5: End-to-end retraining and evaluation from raw logs.
    """

    def verify_level_1_integrity(
        self,
        artifact_path: Path | str,
        expected_sha256: str,
    ) -> Tuple[bool, str]:
        """Level 1: Cryptographic hash check on file artifact."""
        p = Path(artifact_path)
        if not p.exists():
            return False, f"Artifact not found: {artifact_path}"

        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual = hasher.hexdigest()

        if actual.lower() == expected_sha256.lower():
            return True, f"LEVEL 1 PASS: SHA-256 matches {actual}"
        return False, f"LEVEL 1 FAIL: Expected {expected_sha256}, got {actual}"

    def verify_level_2_metrics(
        self,
        recomputed_metrics: Dict[str, float],
        original_metrics: Dict[str, float],
        tolerance: float = 1e-5,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Level 2: Numerical equality check between original and recomputed metrics."""
        divergences = {}
        passed = True

        for k, orig_v in original_metrics.items():
            if k not in recomputed_metrics:
                divergences[k] = {"error": "Missing from recomputation", "original": orig_v}
                passed = False
                continue

            recomp_v = recomputed_metrics[k]
            diff = abs(orig_v - recomp_v)
            if diff > tolerance:
                divergences[k] = {
                    "original": orig_v,
                    "recomputed": recomp_v,
                    "diff": diff,
                    "tolerance": tolerance,
                }
                passed = False

        return passed, {
            "level": ReproducibilityLevel.LEVEL_2_METRIC.value,
            "passed": passed,
            "divergences": divergences,
            "metrics_evaluated": len(original_metrics),
        }

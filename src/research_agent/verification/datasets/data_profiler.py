"""
Deterministic Dataset Profiler (Prompt 6 Section 23)
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd
from research_agent.schemas.verification import DataProfile


class DataProfiler:
    """
    Computes deterministic statistical summaries of log datasets.
    Links dataset version, computing script, and SHA-256 profile hash.
    """

    def compute_profile(
        self,
        df: pd.DataFrame,
        dataset_version_id: str,
        script_path: str = "src/research_agent/verification/datasets/data_profiler.py",
        code_commit_hash: str = "HEAD",
        timestamp_col: Optional[str] = None,
        label_col: Optional[str] = None,
        entity_col: Optional[str] = None,
        template_col: Optional[str] = None,
    ) -> DataProfile:
        """Computes summary statistics and generates a hashed DataProfile."""
        total_events = len(df)
        total_entities = df[entity_col].nunique() if entity_col and entity_col in df.columns else 0
        template_count = df[template_col].nunique() if template_col and template_col in df.columns else None
        host_count = df[entity_col].nunique() if entity_col and entity_col in df.columns else None

        label_counts: Dict[str, int] = {}
        class_ratios: Dict[str, float] = {}
        if label_col and label_col in df.columns:
            vc = df[label_col].value_counts()
            label_counts = {str(k): int(v) for k, v in vc.items()}
            class_ratios = {str(k): float(v / total_events) for k, v in vc.items()} if total_events > 0 else {}

        missing_rates = {str(col): float(df[col].isna().mean()) for col in df.columns}

        ts_range = None
        if timestamp_col and timestamp_col in df.columns:
            ts = pd.to_datetime(df[timestamp_col], errors="coerce")
            if not ts.isna().all():
                ts_range = f"{ts.min().isoformat()} to {ts.max().isoformat()}"

        profile_dict = {
            "dataset_version_id": dataset_version_id,
            "total_events": total_events,
            "total_entities": total_entities,
            "label_counts": label_counts,
            "class_ratios": class_ratios,
            "missing_rates": missing_rates,
            "template_count": template_count,
            "host_count": host_count,
            "timestamp_range": ts_range,
        }
        profile_json = json.dumps(profile_dict, sort_keys=True)
        profile_sha256 = hashlib.sha256(profile_json.encode("utf-8")).hexdigest()
        profile_id = f"DPF-{abs(hash(dataset_version_id + profile_sha256)) % 1000000:06d}"

        return DataProfile(
            profile_id=profile_id,
            dataset_version_id=dataset_version_id,
            total_events=total_events,
            total_entities=total_entities,
            label_counts=label_counts,
            class_ratios=class_ratios,
            missing_rates=missing_rates,
            template_count=template_count,
            host_count=host_count,
            timestamp_range=ts_range,
            script_path=script_path,
            code_commit_hash=code_commit_hash,
            profile_sha256=profile_sha256,
            computed_at=datetime.now(timezone.utc),
        )

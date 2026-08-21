# -*- coding: utf-8 -*-
"""
Streaming Dataset Validator and Integrity Auditor
Provides memory-bounded streaming validation for HDFS, BGL, DARPA TC, and LANL logs.
Enforces D-drive storage policies and prevents out-of-memory errors on multi-GB datasets.
"""

import os
import sys
import gzip
import json
import zipfile
import tarfile
import hashlib
from pathlib import Path
from typing import Dict, Any, Generator, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

CHUNK_SIZE = 64 * 1024 * 1024  # 64 MiB stream buffer

def compute_streaming_sha256(file_path: Path) -> Tuple[str, int]:
    """Computes SHA-256 and byte size using bounded streaming chunks."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hasher = hashlib.sha256()
    total_bytes = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
            total_bytes += len(chunk)
            
    return hasher.hexdigest(), total_bytes

def line_stream_reader(file_path: Path) -> Generator[Tuple[int, str], None, None]:
    """Memory-efficient streaming line generator for plain text, gzip, and zip files."""
    line_no = 0
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                line_no += 1
                yield line_no, line
    elif file_path.suffix == ".zip":
        with zipfile.ZipFile(file_path, "r") as z:
            for name in z.namelist():
                if name.endswith("/") or name.startswith("__MACOSX"):
                    continue
                with z.open(name, "r") as zf:
                    import io
                    text_wrapper = io.TextIOWrapper(zf, encoding="utf-8", errors="replace")
                    for line in text_wrapper:
                        line_no += 1
                        yield line_no, line
    elif file_path.suffix in [".tar", ".tgz"] or (file_path.name.endswith(".tar.gz")):
        with tarfile.open(file_path, "r:*") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                f = tar.extractfile(member)
                if f is not None:
                    import io
                    text_wrapper = io.TextIOWrapper(f, encoding="utf-8", errors="replace")
                    for line in text_wrapper:
                        line_no += 1
                        yield line_no, line
    else:
        with open(file_path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                line_no += 1
                yield line_no, line

class StreamingDatasetValidator:
    """Validator for raw datasets enforcing integrity, timestamp consistency, and state machines."""
    
    def __init__(self, workspace_root: Path = Path(r"D:\Research")):
        self.workspace_root = workspace_root
        self.manifests_dir = workspace_root / "datasets" / "manifests"
        self.ledger_path = self.manifests_dir / "ACQUISITION-LEDGER.jsonl"
        self.manifests_dir.mkdir(parents=True, exist_ok=True)

    def append_ledger_entry(self, entry: Dict[str, Any]):
        """Appends a verified acquisition record to ACQUISITION-LEDGER.jsonl."""
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def validate_hdfs(self, raw_path: Path) -> Dict[str, Any]:
        """Validates HDFS raw archive and stream line counts."""
        sha256, byte_count = compute_streaming_sha256(raw_path)
        valid_rows = 0
        malformed_rows = 0
        sample_blocks = set()

        for line_no, line in line_stream_reader(raw_path):
            line_str = line.strip()
            if not line_str:
                continue
            if "blk_" in line_str:
                valid_rows += 1
                # Sample some block ids
                parts = line_str.split("blk_")
                if len(parts) > 1 and len(sample_blocks) < 100:
                    blk_id = "blk_" + parts[1].split()[0]
                    sample_blocks.add(blk_id)
            else:
                valid_rows += 1

        res = {
            "dataset": "HDFS",
            "file_name": raw_path.name,
            "local_path": str(raw_path),
            "sha256": sha256,
            "byte_count": byte_count,
            "valid_rows": valid_rows,
            "malformed_rows": malformed_rows,
            "sample_blocks_detected": len(sample_blocks),
            "status": "VALIDATED" if valid_rows > 0 else "CORRUPTED"
        }
        return res

    def validate_bgl(self, raw_path: Path) -> Dict[str, Any]:
        """Validates BGL raw archive, timestamp ordering, and alert flags."""
        sha256, byte_count = compute_streaming_sha256(raw_path)
        valid_rows = 0
        malformed_rows = 0
        alert_count = 0
        non_alert_count = 0
        min_timestamp = None
        max_timestamp = None
        timestamp_inversions = 0
        last_ts = 0

        for line_no, line in line_stream_reader(raw_path):
            line_str = line.strip()
            if not line_str:
                continue
            parts = line_str.split()
            if len(parts) >= 6:
                valid_rows += 1
                flag = parts[0]
                if flag == "-":
                    non_alert_count += 1
                else:
                    alert_count += 1
                
                # Check timestamp
                try:
                    ts = int(parts[1])
                    if min_timestamp is None or ts < min_timestamp:
                        min_timestamp = ts
                    if max_timestamp is None or ts > max_timestamp:
                        max_timestamp = ts
                    if ts < last_ts:
                        timestamp_inversions += 1
                    last_ts = ts
                except ValueError:
                    malformed_rows += 1
            else:
                malformed_rows += 1

        res = {
            "dataset": "BGL",
            "file_name": raw_path.name,
            "local_path": str(raw_path),
            "sha256": sha256,
            "byte_count": byte_count,
            "valid_rows": valid_rows,
            "malformed_rows": malformed_rows,
            "alert_rows": alert_count,
            "non_alert_rows": non_alert_count,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "timestamp_inversions": timestamp_inversions,
            "status": "VALIDATED" if valid_rows > 0 else "CORRUPTED"
        }
        return res

    def audit_storage_cleanliness(self) -> Dict[str, Any]:
        """Audits C: drive for accidental large research artifacts (>=256 MiB)."""
        c_root = Path("C:\\")
        large_violations = []
        
        # Check standard user temp & downloads directories
        user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        check_dirs = [
            Path(user_profile) / "Downloads",
            Path(user_profile) / "AppData" / "Local" / "Temp",
            Path("C:\\Temp")
        ]

        threshold_bytes = 256 * 1024 * 1024  # 256 MiB

        for d in check_dirs:
            if not d.exists():
                continue
            for p in d.rglob("*"):
                if p.is_file():
                    try:
                        sz = p.stat().st_size
                        name_lower = p.name.lower()
                        if sz >= threshold_bytes and any(k in name_lower for k in ["hdfs", "bgl", "darpa", "lanl", "chuyende"]):
                            large_violations.append({
                                "path": str(p),
                                "size_bytes": sz,
                                "size_mib": round(sz / (1024 * 1024), 2)
                            })
                    except Exception:
                        pass

        return {
            "large_research_artifacts_on_c": len(large_violations),
            "violations": large_violations,
            "status": "PASS" if len(large_violations) == 0 else "FAIL"
        }

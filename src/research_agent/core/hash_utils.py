"""
Cryptographic Integrity Hashing Utilities (SHA-256) (RC-10, RC-15, RC-16)
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def compute_file_sha256(file_path: Path | str, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a local file."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found for hash computation: {file_path}")

    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of raw byte sequence."""
    return hashlib.sha256(data).hexdigest()


def compute_string_sha256(text: str, encoding: str = "utf-8") -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def compute_dict_sha256(data: Dict[str, Any]) -> str:
    """Compute canonical deterministic SHA-256 hash of a dictionary (keys sorted)."""
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

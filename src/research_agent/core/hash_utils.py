"""
Tiện ích băm tính toàn vẹn mật mã (SHA-256) (RC-10, RC-15, RC-16)
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def compute_file_sha256(file_path: Path | str, chunk_size: int = 65536) -> str:
    """Tính hàm băm SHA-256 của tệp cục bộ."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found for hash computation: {file_path}")

    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Tính hàm băm SHA-256 của chuỗi (sequence) byte thô."""
    return hashlib.sha256(data).hexdigest()


def compute_string_sha256(text: str, encoding: str = "utf-8") -> str:
    """Tính hàm băm SHA-256 của một chuỗi (sequence)."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def compute_dict_sha256(data: Dict[str, Any]) -> str:
    """Tính toán hàm băm SHA-256 xác định chính tắc của một từ điển (các khóa được sắp xếp)."""
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

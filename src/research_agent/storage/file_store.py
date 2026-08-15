"""
Filesystem Canonical Artifact Store and Disposable Index Manager (ADR-0001, ADR-0004, RC-16, RC-17)
"""

import shutil
from pathlib import Path
from typing import Optional
from research_agent.config import WorkspaceConfig, get_default_config
from research_agent.core.guards import PathGuard
from research_agent.core.hash_utils import compute_file_sha256, compute_bytes_sha256, compute_string_sha256


class CanonicalFileStore:
    """Manages physical files within workspace root with PathGuard safety and SHA-256 hashing."""

    def __init__(self, config: Optional[WorkspaceConfig] = None):
        self.config = config or get_default_config()
        self.guard = PathGuard(self.config)

    def write_text(self, relative_path: str | Path, content: str, encoding: str = "utf-8") -> tuple[Path, str]:
        """Safely write text to file and return (absolute_path, sha256_hash)."""
        safe_path = self.guard.resolve_safe_path(relative_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding=encoding)
        file_hash = compute_file_sha256(safe_path)
        return safe_path, file_hash

    def write_bytes(self, relative_path: str | Path, data: bytes) -> tuple[Path, str]:
        """Safely write raw bytes to file and return (absolute_path, sha256_hash)."""
        safe_path = self.guard.resolve_safe_path(relative_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_bytes(data)
        file_hash = compute_file_sha256(safe_path)
        return safe_path, file_hash

    def read_text(self, relative_path: str | Path, encoding: str = "utf-8") -> str:
        """Safely read text from workspace file."""
        safe_path = self.guard.resolve_safe_path(relative_path, must_exist=True)
        return safe_path.read_text(encoding=encoding)

    def read_bytes(self, relative_path: str | Path) -> bytes:
        """Safely read binary bytes from workspace file."""
        safe_path = self.guard.resolve_safe_path(relative_path, must_exist=True)
        return safe_path.read_bytes()

    def purge_derived_indexes(self) -> tuple[int, int]:
        """Purge disposable derived indexes and caches (RC-17, ADR-0004).
        
        Returns (purged_cache_files, purged_index_files).
        """
        cache_dir = self.config.cache_dir
        index_dir = self.config.indexes_dir

        cache_count = 0
        if cache_dir.exists():
            for item in cache_dir.iterdir():
                if item.name != ".gitkeep":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    cache_count += 1

        index_count = 0
        if index_dir.exists():
            for item in index_dir.iterdir():
                if item.name != ".gitkeep":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    index_count += 1

        return cache_count, index_count

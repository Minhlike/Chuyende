"""
Workspace Configuration and Path Resolution
"""

from dataclasses import dataclass, field
from pathlib import Path
import os
from typing import Optional


@dataclass(frozen=True)
class WorkspaceConfig:
    """Canonical Workspace Configuration for the Research Engineering System.
    
    Default root is 'D:\\Research', which can be overridden via RESEARCH_WORKSPACE_ROOT.
    Centralizes all directory resolution and prevents hardcoding across the codebase.
    """
    workspace_root: Path = field(
        default_factory=lambda: Path(os.environ.get("RESEARCH_WORKSPACE_ROOT", r"D:\Research")).resolve()
    )
    specs_rel_dir: str = "research_specs"
    sources_rel_dir: str = "sources"
    datasets_rel_dir: str = "datasets"
    experiments_rel_dir: str = "experiments"
    artifacts_rel_dir: str = "artifacts"
    memory_rel_dir: str = "memory"
    runtime_rel_dir: str = "runtime"
    docs_rel_dir: str = "docs"
    db_rel_path: str = "runtime/db/research.db"
    strict_path_guard: bool = True
    allow_derived_index_purge: bool = True

    @property
    def specs_dir(self) -> Path:
        return (self.workspace_root / self.specs_rel_dir).resolve()

    @property
    def roadmap_specs_dir(self) -> Path:
        return (self.specs_dir / "roadmap").resolve()

    @property
    def reference_map_specs_dir(self) -> Path:
        return (self.specs_dir / "reference_map").resolve()

    @property
    def sources_dir(self) -> Path:
        return (self.workspace_root / self.sources_rel_dir).resolve()

    @property
    def datasets_dir(self) -> Path:
        return (self.workspace_root / self.datasets_rel_dir).resolve()

    @property
    def experiments_dir(self) -> Path:
        return (self.workspace_root / self.experiments_rel_dir).resolve()

    @property
    def artifacts_dir(self) -> Path:
        return (self.workspace_root / self.artifacts_rel_dir).resolve()

    @property
    def memory_dir(self) -> Path:
        return (self.workspace_root / self.memory_rel_dir).resolve()

    @property
    def runtime_dir(self) -> Path:
        return (self.workspace_root / self.runtime_rel_dir).resolve()

    @property
    def db_path(self) -> Path:
        return (self.workspace_root / self.db_rel_path).resolve()

    @property
    def cache_dir(self) -> Path:
        return (self.runtime_dir / "cache").resolve()

    @property
    def indexes_dir(self) -> Path:
        return (self.runtime_dir / "indexes").resolve()

    @property
    def logs_dir(self) -> Path:
        return (self.runtime_dir / "logs").resolve()

    @property
    def docs_dir(self) -> Path:
        return (self.workspace_root / self.docs_rel_dir).resolve()

    def resolve_path(self, relative_or_absolute: str | Path) -> Path:
        """Resolve a path relative to workspace root if relative."""
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p.resolve()
        return (self.workspace_root / p).resolve()

    def ensure_directories(self) -> None:
        """Ensure all canonical workspace directories exist."""
        dirs = [
            self.workspace_root,
            self.roadmap_specs_dir,
            self.reference_map_specs_dir,
            self.sources_dir / "original",
            self.sources_dir / "metadata",
            self.sources_dir / "manifests",
            self.datasets_dir / "raw",
            self.datasets_dir / "processed",
            self.datasets_dir / "manifests",
            self.experiments_dir / "configs",
            self.experiments_dir / "runs",
            self.experiments_dir / "manifests",
            self.artifacts_dir / "equations",
            self.artifacts_dir / "tables",
            self.artifacts_dir / "figures",
            self.memory_dir / "procedural",
            self.memory_dir / "snapshots",
            self.runtime_dir / "db",
            self.cache_dir,
            self.indexes_dir,
            self.logs_dir,
            self.docs_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


_DEFAULT_CONFIG: Optional[WorkspaceConfig] = None


def get_default_config(reload: bool = False) -> WorkspaceConfig:
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None or reload:
        _DEFAULT_CONFIG = WorkspaceConfig()
    return _DEFAULT_CONFIG

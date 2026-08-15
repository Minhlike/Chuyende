"""
Log Feature Extraction Research Engineering System
Core Package
"""

__version__ = "0.1.0"
__author__ = "Research Engineering Team"

from research_agent.config import WorkspaceConfig, get_default_config
from research_agent.core.guards import PathGuard
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
    EquationType,
    ArgumentRelationType,
    VerificationStatus,
    MemoryTier,
    ExperimentStatus,
)

__all__ = [
    "WorkspaceConfig",
    "get_default_config",
    "PathGuard",
    "ClaimType",
    "IntellectualOwnership",
    "EpistemicStatus",
    "EquationType",
    "ArgumentRelationType",
    "VerificationStatus",
    "MemoryTier",
    "ExperimentStatus",
]

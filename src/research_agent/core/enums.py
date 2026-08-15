"""
Core Enums defining Epistemic, Claim, Ownership, and Memory taxonomies.
"""

from enum import Enum


class ClaimType(str, Enum):
    """Canonical Claim Types (RC-05)."""
    SOURCE_FACT = "SOURCE_FACT"
    SOURCE_CLAIM = "SOURCE_CLAIM"
    SYNTHESIS = "SYNTHESIS"
    OUR_INFERENCE = "OUR_INFERENCE"
    OUR_DESIGN = "OUR_DESIGN"
    EXPERIMENT_RESULT = "EXPERIMENT_RESULT"
    HYPOTHESIS = "HYPOTHESIS"


class IntellectualOwnership(str, Enum):
    """Intellectual Ownership Boundaries (RC-06)."""
    SOURCE = "SOURCE"
    ADAPTED = "ADAPTED"
    OURS = "OURS"
    BASELINE = "BASELINE"


class EpistemicStatus(str, Enum):
    """Epistemic Status Lifecycle Matrix (RC-07)."""
    UNVERIFIED = "UNVERIFIED"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTESTED = "CONTESTED"
    FALSIFIED = "FALSIFIED"
    SUPERSEDED = "SUPERSEDED"


class EquationType(str, Enum):
    """Equation Provenance Taxonomy (RC-08)."""
    SOURCE_EQUATION = "SOURCE_EQUATION"
    DERIVED_EQUATION = "DERIVED_EQUATION"
    PROPOSED_EQUATION = "PROPOSED_EQUATION"


class ArgumentRelationType(str, Enum):
    """Argument Graph Edge Relations (Section 11)."""
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    QUALIFIES = "QUALIFIES"
    DEPENDS_ON = "DEPENDS_ON"
    ASSUMES = "ASSUMES"
    DERIVED_FROM = "DERIVED_FROM"
    GENERALIZES = "GENERALIZES"
    SPECIALIZES = "SPECIALIZES"
    FALSIFIES = "FALSIFIES"
    REPLICATES = "REPLICATES"
    FAILS_TO_REPLICATE = "FAILS_TO_REPLICATE"
    MOTIVATES = "MOTIVATES"
    COMPARES_WITH = "COMPARES_WITH"


class VerificationStatus(str, Enum):
    """Verification States."""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class MemoryTier(str, Enum):
    """Long-term Memory Architecture Tiers (Section 7)."""
    M0_WORKING = "M0_WORKING"
    M1_SOURCE = "M1_SOURCE"
    M2_SEMANTIC = "M2_SEMANTIC"
    M3_EPISODIC = "M3_EPISODIC"
    M4_ARGUMENT = "M4_ARGUMENT"
    M5_PROCEDURAL = "M5_PROCEDURAL"


class ExperimentStatus(str, Enum):
    """Experiment and Run Lifecycles (RC-10, RC-14)."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class ArtifactCategory(str, Enum):
    """Canonical Artifact Categories."""
    EQUATION = "EQUATION"
    TABLE = "TABLE"
    FIGURE = "FIGURE"
    DATASET_SPLIT = "DATASET_SPLIT"
    MODEL_WEIGHT = "MODEL_WEIGHT"
    LOG_FEATURE_VECTOR = "LOG_FEATURE_VECTOR"
    SPECIFICATION = "SPECIFICATION"
    REPORT = "REPORT"

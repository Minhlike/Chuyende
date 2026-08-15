"""
Core Enums defining Epistemic, Claim, Ownership, and Memory taxonomies (Prompt 1, 2, 3).
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
    """Canonical 4-class Intellectual Ownership Boundaries (RC-06, Section 4)."""
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


class SourceVerificationState(str, Enum):
    """Bibliographic & Content Verification States (Section 7)."""
    DISCOVERED = "DISCOVERED"
    METADATA_VERIFIED = "METADATA_VERIFIED"
    CONTENT_VERIFIED = "CONTENT_VERIFIED"
    INGESTED = "INGESTED"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"
    UNAVAILABLE = "UNAVAILABLE"


class SourceRole(str, Enum):
    """Functional roles of an external source in the research graph (Section 18)."""
    DEFINITION = "DEFINITION"
    BACKGROUND = "BACKGROUND"
    METHOD = "METHOD"
    BASELINE = "BASELINE"
    DATASET = "DATASET"
    VALIDITY = "VALIDITY"
    ROBUSTNESS = "ROBUSTNESS"
    PRIVACY = "PRIVACY"
    REPRODUCIBILITY = "REPRODUCIBILITY"
    METRIC = "METRIC"
    CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"
    IMPLEMENTATION_REFERENCE = "IMPLEMENTATION_REFERENCE"
    EMERGING_WORK = "EMERGING_WORK"


class SourceQualityTier(str, Enum):
    """Bibliographic quality and provenance classes (Section 19)."""
    PRIMARY_STANDARD = "PRIMARY_STANDARD"
    PEER_REVIEWED_TOP_VENUE = "PEER_REVIEWED_TOP_VENUE"
    PEER_REVIEWED = "PEER_REVIEWED"
    OFFICIAL_DATASET = "OFFICIAL_DATASET"
    INSTITUTIONAL_REPORT = "INSTITUTIONAL_REPORT"
    PREPRINT = "PREPRINT"
    SOFTWARE_ARTIFACT = "SOFTWARE_ARTIFACT"
    SECONDARY_SURVEY = "SECONDARY_SURVEY"
    DISCOVERY_ONLY = "DISCOVERY_ONLY"


class SupportType(str, Enum):
    """Citation Firewall support type relationship (Section 10)."""
    DIRECT_SUPPORT = "DIRECT_SUPPORT"
    PARTIAL_SUPPORT = "PARTIAL_SUPPORT"
    BACKGROUND = "BACKGROUND"
    MOTIVATION = "MOTIVATION"
    CONTRADICTION = "CONTRADICTION"
    METHOD_SOURCE = "METHOD_SOURCE"
    DATASET_SOURCE = "DATASET_SOURCE"
    BASELINE_SOURCE = "BASELINE_SOURCE"


class EvidenceStrength(str, Enum):
    """Categorical strength of evidence binding (Section 11)."""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class NoveltyStatus(str, Enum):
    """Novelty evaluation lifecycle states for candidate contributions (Section 17)."""
    CANDIDATE = "CANDIDATE"
    PRIOR_ART_SEARCHED = "PRIOR_ART_SEARCHED"
    POTENTIALLY_NOVEL = "POTENTIALLY_NOVEL"
    NOT_NOVEL = "NOT_NOVEL"
    PARTIALLY_NOVEL = "PARTIALLY_NOVEL"
    NOVELTY_UNRESOLVED = "NOVELTY_UNRESOLVED"


class CitationFirewallStatus(str, Enum):
    """Citation readiness state in Citation Firewall (Section 10)."""
    READY = "READY"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


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

"""
Scientific Verification Package (Prompt 6, RC-08, RC-09, RC-10, RC-14, RC-16, RC-18)
"""

from research_agent.verification.equations.symbolic_engine import SymbolicVerificationEngine
from research_agent.verification.equations.symbol_registry import SymbolRegistry
from research_agent.verification.equations.provenance import EquationProvenanceAuditor
from research_agent.verification.datasets.data_validator import DataValidator
from research_agent.verification.datasets.data_profiler import DataProfiler
from research_agent.verification.datasets.split_validator import AntiLeakageSplitValidator
from research_agent.verification.datasets.lineage import DatasetLineageTracker
from research_agent.verification.metrics.recomputation import MetricRecomputationEngine
from research_agent.verification.metrics.thresholds import ThresholdAuditor
from research_agent.verification.statistics.descriptive import DescriptiveStatisticsEngine
from research_agent.verification.statistics.confidence_intervals import ConfidenceIntervalEngine
from research_agent.verification.statistics.effect_sizes import EffectSizeEngine
from research_agent.verification.statistics.hypothesis_tests import HypothesisTestingEngine
from research_agent.verification.statistics.multi_seed_aggregator import MultiSeedAggregator
from research_agent.verification.statistics.misuse_guards import StatisticalMisuseAuditor
from research_agent.verification.tables.builder import TableBuilder
from research_agent.verification.tables.fairness import TableFairnessAuditor
from research_agent.verification.figures.builder import FigureBuilder
from research_agent.verification.figures.metadata import FigureMetadataManager
from research_agent.verification.reproducibility.lineage_dag import ScientificLineageDAG
from research_agent.verification.reproducibility.invalidation import InvalidationManager
from research_agent.verification.reproducibility.reproduce import ReproductionRunner
from research_agent.verification.auditors import NumericalHallucinationAuditor, VerificationGateForWriting
from research_agent.verification.packaging import ResultBundleBuilder, VerifiedClaimBundleBuilder
from research_agent.verification.pipeline import ScientificVerificationPipeline

__all__ = [
    "SymbolicVerificationEngine",
    "SymbolRegistry",
    "EquationProvenanceAuditor",
    "DataValidator",
    "DataProfiler",
    "AntiLeakageSplitValidator",
    "DatasetLineageTracker",
    "MetricRecomputationEngine",
    "ThresholdAuditor",
    "DescriptiveStatisticsEngine",
    "ConfidenceIntervalEngine",
    "EffectSizeEngine",
    "HypothesisTestingEngine",
    "MultiSeedAggregator",
    "StatisticalMisuseAuditor",
    "TableBuilder",
    "TableFairnessAuditor",
    "FigureBuilder",
    "FigureMetadataManager",
    "ScientificLineageDAG",
    "InvalidationManager",
    "ReproductionRunner",
    "NumericalHallucinationAuditor",
    "VerificationGateForWriting",
    "ResultBundleBuilder",
    "VerifiedClaimBundleBuilder",
    "ScientificVerificationPipeline",
]

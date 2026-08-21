"""
Word 2016 Scientific Visuals Package
"""

from research_agent.visuals.schemas import (
    VisualType,
    CreationMethod,
    VisualNecessityReason,
    VisualNecessityEvaluation,
    ShapeNodeSpec,
    ConnectorSpec,
    DiagramSpecification,
    VisualRecord,
)
from research_agent.visuals.registry import VisualRegistry
from research_agent.visuals.necessity_gate import VisualNecessityGate
from research_agent.visuals.word_diagram_builder import WordDiagramBuilder
from research_agent.visuals.word_table_builder import WordTableBuilder
from research_agent.visuals.word_caption_manager import WordCaptionManager
from research_agent.visuals.word_cross_reference_manager import WordCrossReferenceManager
from research_agent.visuals.scientific_figure_inserter import ScientificFigureInserter
from research_agent.visuals.visual_qa import VisualQAEngine

__all__ = [
    "VisualType",
    "CreationMethod",
    "VisualNecessityReason",
    "VisualNecessityEvaluation",
    "ShapeNodeSpec",
    "ConnectorSpec",
    "DiagramSpecification",
    "VisualRecord",
    "VisualRegistry",
    "VisualNecessityGate",
    "WordDiagramBuilder",
    "WordTableBuilder",
    "WordCaptionManager",
    "WordCrossReferenceManager",
    "ScientificFigureInserter",
    "VisualQAEngine",
]

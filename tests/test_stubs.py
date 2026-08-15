"""
Tests for Subsystem Stubs (Explicit NOT_IMPLEMENTED verification)
"""

import pytest
from research_agent.stubs import (
    AdvancedRAGEngine,
    ResearchReasoningEngine,
    PaperDiscoveryService,
    PDFUnderstandingEngine,
    DOIVerificationService,
    SymbolicEquationVerifier,
    StatisticalHypothesisEngine,
    DeterministicFigureGenerator,
    ChapterComposer,
    ThesisAuditor,
)


def test_all_stubs_raise_not_implemented():
    """Verify that every future subsystem stub explicitly raises NotImplementedError instead of fake success."""
    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        AdvancedRAGEngine().retrieve("log representation")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        ResearchReasoningEngine().infer_conclusions(["CLM-000001"])

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        PaperDiscoveryService().search_literature("DeepLog")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        PDFUnderstandingEngine().extract_structured_document("paper.pdf")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        DOIVerificationService().verify_doi("10.1145/123456")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        SymbolicEquationVerifier().verify_derivation("a+b", "b+a")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        StatisticalHypothesisEngine().test_hypothesis([0.9], [0.95])

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        DeterministicFigureGenerator().generate_figure("plot.py", "RUN-000001")

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        ChapterComposer().compose_section("NOD-000001", ["CLM-000001"])

    with pytest.raises(NotImplementedError, match="NOT_IMPLEMENTED"):
        ThesisAuditor().audit_entire_thesis()

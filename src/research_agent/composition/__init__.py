"""
Academic Composition, Anti-Hallucination & Thesis Auditing Module (Prompt 7)
"""

from research_agent.composition.gates import WritingGate
from research_agent.composition.anti_hallucination import AntiHallucinationCompiler
from research_agent.composition.composer import AcademicComposer
from research_agent.composition.auditors import ThesisAuditor
from research_agent.composition.human_workflow import HumanWorkflowManager
from research_agent.composition.compiler import ThesisCompiler
from research_agent.composition.packaging import ResearchArtifactPackager

__all__ = [
    "WritingGate",
    "AntiHallucinationCompiler",
    "AcademicComposer",
    "ThesisAuditor",
    "HumanWorkflowManager",
    "ThesisCompiler",
    "ResearchArtifactPackager",
]

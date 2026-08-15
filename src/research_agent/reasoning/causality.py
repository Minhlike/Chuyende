"""
Causality Auditor & Causal Inflation Guard (Prompt 5 Section 27)
"""

import re
from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import ReasoningIssue
from research_agent.core.enums import ReasoningIssueType


class CausalityAuditor:
    """
    Audits research claims and inferences for unjustified causal assertions.
    Enforces the fundamental architectural boundary:
    PROVENANCE DEPENDENCY != CAUSAL EFFECT (Section 27, Roadmap 2.3.2).
    """

    CAUSAL_INDICATORS = [
        r'\bcauses\b',
        r'\bleads to\b',
        r'\bresults in\b',
        r'\beffect of\b',
        r'\bbecause of\b',
        r'\bcausal(?:ly)?\b',
        r'\bdetermines\b',
        r'\bdrives\b',
    ]

    def audit_text_causality(self, entity_id: str, text: str, is_interventional: bool = False) -> List[ReasoningIssue]:
        """
        Flags causal vocabulary if experimental basis is purely observational or correlational.
        """
        issues: List[ReasoningIssue] = []
        t_lower = text.lower()

        found_causal = []
        for pattern in self.CAUSAL_INDICATORS:
            if re.search(pattern, t_lower):
                found_causal.append(pattern.replace(r'\b', ''))

        if found_causal and not is_interventional:
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-CAUS-{abs(hash(entity_id + text)) % 1000000:06d}",
                    issue_type=ReasoningIssueType.CAUSALITY_INFLATION,
                    affected_entity_id=entity_id,
                    message=f"Causal terms ({found_causal}) used for observational telemetry or statistical correlation without interventional/counterfactual experiment.",
                    severity="HIGH",
                    mitigation="Rephrase statement using non-causal associational language ('is associated with', 'empirically correlates with', 'exhibits dependency linkage').",
                )
            )

        # Explicit Provenance Graph Guard (Roadmap 2.3.2)
        if "provenance" in t_lower and ("causal effect" in t_lower or "causes" in t_lower):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-PROV-CAUS-{abs(hash(entity_id + 'prov')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.CAUSALITY_INFLATION,
                    affected_entity_id=entity_id,
                    message="System audit provenance edges represent temporal/dataflow dependencies (DEPENDS_ON), NOT interventional causal mechanisms.",
                    severity="CRITICAL",
                    mitigation="Maintain clear distinction between observable dataflow provenance and causal effect.",
                )
            )

        return issues

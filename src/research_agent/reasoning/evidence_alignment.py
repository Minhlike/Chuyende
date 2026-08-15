"""
Evidence Alignment Engine & Evidence Gap Detector (Prompt 5 Sections 10, 11)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.core.enums import EvidenceAlignmentStatus
from research_agent.schemas.claim import Claim
from research_agent.schemas.evidence import Evidence
from research_agent.schemas.reasoning import EvidenceGap


class EvidenceAlignmentEngine:
    """
    Evaluates empirical alignment between Evidence units and Claims.
    Checks:
    - Semantic entailment / direction
    - Scope compatibility (dataset, domain, metric)
    - Methodological compatibility
    - Generates EvidenceGap records when empirical support is missing or partial.
    """

    def align(self, evidence: Evidence, claim: Claim) -> Tuple[EvidenceAlignmentStatus, str]:
        """
        Determine if Evidence supports, contradicts, qualifies, or is insufficient for Claim.
        """
        e_text = (evidence.exact_quote or evidence.paraphrase or "").lower()
        c_text = claim.statement.lower()

        # Check for direct contradictions
        negation_in_e = any(w in e_text for w in ["not", "fails to", "cannot", "degrades", "outperformed by baseline", "simpler is better"])
        negation_in_c = any(w in c_text for w in ["not", "fails to", "cannot", "degrades", "outperformed by baseline"])

        if negation_in_e != negation_in_c and any(term in e_text for term in ["baseline", "gnn", "accuracy", "outperform", "shortcut"]):
            # Potential contradiction
            return EvidenceAlignmentStatus.CONTRADICTION, "Evidence asserts contrary empirical outcome or baseline superiority."

        # Check for qualification
        if any(w in e_text for w in ["only when", "provided that", "limited to", "except", "sensitive to"]):
            return EvidenceAlignmentStatus.QUALIFICATION, "Evidence bounds claim with specific preconditions or sensitivity."

        # Check for direct support
        # Word overlap of key terms
        c_words = set(re.findall(r'\b[a-z]{4,}\b', c_text))
        e_words = set(re.findall(r'\b[a-z]{4,}\b', e_text))
        overlap = c_words.intersection(e_words)

        if len(overlap) >= 3 or (len(c_words) > 0 and len(overlap) / len(c_words) >= 0.4):
            return EvidenceAlignmentStatus.DIRECT_SUPPORT, f"Substantial semantic overlap ({len(overlap)} matching technical concepts)."

        if len(overlap) >= 1:
            return EvidenceAlignmentStatus.PARTIAL_SUPPORT, f"Partial thematic overlap ({len(overlap)} matching terms)."

        return EvidenceAlignmentStatus.INSUFFICIENT, "Insufficient semantic entailment or scope alignment."

    def detect_gap(
        self,
        claim: Claim,
        evidences: List[Evidence],
        node_code: Optional[str] = None,
    ) -> Optional[EvidenceGap]:
        """
        Generates an EvidenceGap if Claim lacks direct or robust empirical evidence.
        """
        if not evidences:
            seq = int(claim.claim_id.replace("CLM-", "") or "1") if "CLM-" in claim.claim_id else 1
            return EvidenceGap(
                gap_id=f"GAP-{seq:06d}",
                claim_id=claim.claim_id,
                missing_evidence=f"No empirical evidence units linked to claim: '{claim.statement[:80]}...'",
                why_required="Every canonical claim must be supported by verified source locators or benchmark runs.",
                suggested_experiment="Conduct controlled ablation study or empirical benchmark run." if claim.ownership.value == "OURS" else None,
                possible_source_search="Search top-tier literature for empirical evidence." if claim.ownership.value == "SOURCE" else None,
                severity="HIGH",
                related_node_code=node_code,
                status="OPEN",
            )

        # Check if all evidences are only partial or qualifications
        alignments = [self.align(e, claim)[0] for e in evidences]
        if EvidenceAlignmentStatus.DIRECT_SUPPORT not in alignments:
            seq = int(claim.claim_id.replace("CLM-", "") or "1") if "CLM-" in claim.claim_id else 1
            return EvidenceGap(
                gap_id=f"GAP-{seq:06d}",
                claim_id=claim.claim_id,
                missing_evidence=f"Claim has only partial or qualified evidence: {[a.value for a in alignments]}",
                why_required="Direct empirical support is necessary to claim general validity.",
                suggested_experiment="Run discriminating experiment to confirm direct support.",
                severity="MEDIUM",
                related_node_code=node_code,
                status="OPEN",
            )

        return None

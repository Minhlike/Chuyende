"""
Atomic Claim Extraction, Proposition Normalization & Scope Extraction (Prompt 5 Sections 6, 7, 8)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from research_agent.core.enums import (
    ClaimType,
    IntellectualOwnership,
    EpistemicStatus,
)
from research_agent.schemas.reasoning import (
    AtomicClaimCandidate,
    ClaimScope,
)


class ClaimExtractor:
    """
    Extracts atomic claims from unstructured or semi-structured scientific text.
    Enforces proposition normalization and qualifier/scope preservation.
    """

    # Qualifier preservation patterns (Prompt 5 Section 7)
    WEAK_QUALIFIERS = [
        "may", "might", "could", "suggests", "indicates", "appears to",
        "under specific conditions", "partially", "observed in",
    ]

    CAUSAL_INFLATION_WORDS = [
        "causes", "leads to", "proves", "guarantees", "always",
        "is superior", "is better", "eliminates",
    ]

    def extract_atomic_claims(
        self,
        text: str,
        source_id: Optional[str] = None,
        locator: Optional[str] = None,
        claim_type: ClaimType = ClaimType.SOURCE_CLAIM,
        ownership: IntellectualOwnership = IntellectualOwnership.SOURCE,
    ) -> List[AtomicClaimCandidate]:
        """
        Decomposes compound sentences into atomic propositional assertions.
        """
        raw_sentences = self._split_sentences(text)
        candidates: List[AtomicClaimCandidate] = []

        for sent in raw_sentences:
            sent_clean = sent.strip()
            if not sent_clean or len(sent_clean) < 15:
                continue

            # Split compound conjunctions where distinct empirical claims exist
            sub_propositions = self._split_compound_conjunctions(sent_clean)
            for prop in sub_propositions:
                scope = self._extract_scope(prop)
                qualifiers = self._extract_qualifiers(prop)
                normalized = self._normalize_proposition(prop, qualifiers)

                cand = AtomicClaimCandidate(
                    statement=normalized,
                    original_wording=prop,
                    source_id=source_id,
                    locator=locator,
                    claim_type=claim_type,
                    ownership=ownership,
                    scope=scope,
                    qualifiers=qualifiers,
                    conditions=self._extract_conditions(prop),
                    confidence_basis="Source locator extract" if locator else "Context analysis",
                    is_normalized=True,
                    extracted_from=sent_clean,
                )
                candidates.append(cand)

        return candidates

    def _split_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries, avoiding decimals like 1.2 or citations like Bilot et al.
        pattern = r'(?<!\bet al)(?<!\bFig)(?<!\bSec)(?<!\bEq)(?<!\b[0-9])\.\s+'
        return re.split(pattern, text)

    def _split_compound_conjunctions(self, sentence: str) -> List[str]:
        """Splits multi-clause claims into atomic assertions."""
        # Check for multiple independent clauses joined by ', and ' or '; '
        clauses = re.split(r';\s+|\s*,\s*and\s+(?=[A-Z0-9a-z_]+\s+(?:is|was|had|outperformed|achieved|reduced))', sentence)
        return [c.strip() for c in clauses if c.strip()]

    def _extract_scope(self, text: str) -> ClaimScope:
        """Extracts dataset, domain, metric, and experimental parameters bounding the claim."""
        scope = ClaimScope()
        t_lower = text.lower()

        # Datasets
        if "darpa" in t_lower:
            scope.dataset = "DARPA TC (Transparent Computing)"
        elif "lanl" in t_lower:
            scope.dataset = "LANL Cyber Security Dataset"
        elif "bgl" in t_lower:
            scope.dataset = "BGL Supercomputer Log Dataset"
        elif "hdfs" in t_lower:
            scope.dataset = "HDFS Log Dataset"
        elif "thunderbird" in t_lower:
            scope.dataset = "Thunderbird Log Dataset"

        # Domain
        if "provenance" in t_lower or "graph" in t_lower or "sysflow" in t_lower:
            scope.domain = "Host Provenance Telemetry"
        elif "system log" in t_lower or "drain" in t_lower or "logbert" in t_lower:
            scope.domain = "System Event Logs"

        # Metric
        metrics = ["f1", "precision", "recall", "auc", "pr-auc", "latency", "throughput", "fpr"]
        found_metrics = [m for m in metrics if re.search(rf'\b{m}\b', t_lower)]
        if found_metrics:
            scope.metric = ", ".join(found_metrics).upper()

        return scope

    def _extract_qualifiers(self, text: str) -> List[str]:
        found = []
        t_lower = text.lower()
        for q in self.WEAK_QUALIFIERS:
            if q in t_lower:
                found.append(q)
        return found

    def _extract_conditions(self, text: str) -> List[str]:
        conditions = []
        cond_matches = re.findall(r'\b(when|if|under|assuming|provided that)\s+([^,.;]+)', text, re.IGNORECASE)
        for prefix, body in cond_matches:
            conditions.append(f"{prefix} {body.strip()}")
        return conditions

    def _normalize_proposition(self, text: str, qualifiers: List[str]) -> str:
        """
        Normalizes wording without inflating strength (Section 7).
        Preserves qualifiers like 'may', 'under setup X'.
        """
        norm = text.strip()
        # Ensure sentence capitalization and clean punctuation
        if norm and not norm[0].isupper():
            norm = norm[0].upper() + norm[1:]
        if not norm.endswith(('.', '!', '?')):
            norm += '.'
        return norm

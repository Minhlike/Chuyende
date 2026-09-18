"""
Trích xuất yêu cầu nguyên tử, chuẩn hóa đề xuất & trích xuất phạm vi (Nhắc 5 Phần 6, 7, 8)
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
    Trích xuất các tuyên bố nguyên tử từ văn bản khoa học phi cấu trúc hoặc bán cấu trúc.
    Thực thi chuẩn hóa đề xuất và bảo toàn vòng loại/phạm vi.
    """

    # Các mẫu bảo toàn vòng loại (Nhắc 5 Phần 7)
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
        Phân tách các câu ghép thành các khẳng định mệnh đề nguyên tử.
        """
        raw_sentences = self._split_sentences(text)
        candidates: List[AtomicClaimCandidate] = []

        for sent in raw_sentences:
            sent_clean = sent.strip()
            if not sent_clean or len(sent_clean) < 15:
                continue

            # Phân chia các liên từ ghép nơi tồn tại các yêu cầu thực nghiệm riêng biệt
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
        # Phân chia ranh giới câu, tránh số thập phân như 1,2 hoặc trích dẫn như Bilot et al.
        pattern = r'(?<!\bet al)(?<!\bFig)(?<!\bSec)(?<!\bEq)(?<!\b[0-9])\.\s+'
        return re.split(pattern, text)

    def _split_compound_conjunctions(self, sentence: str) -> List[str]:
        """Tách các yêu cầu nhiều mệnh đề thành các khẳng định nguyên tử."""
        # Kiểm tra nhiều mệnh đề độc lập được nối bởi ' và ' hoặc '; '
        clauses = re.split(r';\s+|\s*,\s*and\s+(?=[A-Z0-9a-z_]+\s+(?:is|was|had|outperformed|achieved|reduced))', sentence)
        return [c.strip() for c in clauses if c.strip()]

    def _extract_scope(self, text: str) -> ClaimScope:
        """Trích xuất các tham số tập dữ liệu, tên miền, số liệu và thử nghiệm giới hạn luận điểm (claim)."""
        scope = ClaimScope()
        t_lower = text.lower()

        # Bộ dữ liệu
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

        # Tên miền
        if "provenance" in t_lower or "graph" in t_lower or "sysflow" in t_lower:
            scope.domain = "Host Provenance Telemetry"
        elif "system log" in t_lower or "drain" in t_lower or "logbert" in t_lower:
            scope.domain = "System Event Logs"

        # Số liệu
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
        Bình thường hóa cách diễn đạt mà không tăng cường độ mạnh (Phần 7).
        Giữ nguyên các vòng loại như 'có thể', 'theo thiết lập X'.
        """
        norm = text.strip()
        # Đảm bảo viết hoa câu và dấu câu rõ ràng
        if norm and not norm[0].isupper():
            norm = norm[0].upper() + norm[1:]
        if not norm.endswith(('.', '!', '?')):
            norm += '.'
        return norm

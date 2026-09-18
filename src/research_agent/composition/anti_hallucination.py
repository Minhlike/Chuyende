"""
Trình biên dịch chống ảo giác & Trình kiểm tra tính toàn vẹn ở cấp độ câu (Nhắc 7 Phần 8..33)
"""

import re
from typing import Dict, List, Optional, Tuple
from research_agent.core.enums import (
    AllowedWordingStrength,
    IntellectualOwnership,
    SentenceClaimType,
    SentenceCompilationState,
    VerificationStatus,
)
from research_agent.schemas.composition import SentenceRecord
from research_agent.schemas.reasoning import ArgumentBundle
from research_agent.schemas.verification import ResultBundle, VerifiedClaimBundle
from research_agent.storage.repository import ResearchRepository


class AntiHallucinationCompiler:
    """
    Biên soạn các câu dự thảo dựa trên Bản đồ tham khảo chuẩn, Tường lửa trích dẫn,
    Sổ đăng ký yêu cầu bằng số, Sổ đăng ký phương trình và Biểu đồ đối số.
    Thực thi nghiêm ngặt việc chống ảo giác, yêu cầu trích dẫn và giới hạn quyền sở hữu.
    """

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

        # Các cụm từ mới lạ bị cấm không được hỗ trợ
        self.novelty_buzzwords = [
            r"\bfirst\b",
            r"\bfirst-ever\b",
            r"\bunprecedented\b",
            r"\bunique\b",
            r"\bstate-of-the-art\b",
            r"\bsota\b",
            r"\bđầu tiên\b",
            r"\bchưa từng có\b",
            r"\bđộc nhất\b",
        ]

        # Khẳng định nhân quả mạnh mẽ
        self.causal_words = [
            r"\bcauses\b",
            r"\bcausal\b",
            r"\bcausality\b",
            r"\bleads to\b",
            r"\bnguyên nhân trực tiếp\b",
            r"\bgây ra\b",
        ]

    def classify_sentence(self, text: str, ownership: IntellectualOwnership = IntellectualOwnership.OURS) -> SentenceClaimType:
        """Phân loại một cách dứt khoát kiểu câu mệnh đề."""
        t_low = text.lower()
        if any(w in t_low for w in ["we propose", "chúng tôi đề xuất", "we design", "thiết kế"]):
            return SentenceClaimType.OUR_DESIGN
        if any(w in t_low for w in ["achieves", "đạt được", "f1 =", "recall =", "p-value", "latency of"]):
            return SentenceClaimType.EXPERIMENT_RESULT
        if any(w in t_low for w in ["we hypothesize", "giả thuyết rằng", "hypothesis", "h1", "h2"]):
            return SentenceClaimType.HYPOTHESIS
        if any(w in t_low for w in ["limitation", "hạn chế", "threat to validity", "không thể"]):
            return SentenceClaimType.LIMITATION
        if any(w in t_low for w in ["suggests that", "indicates that", "cho thấy rằng", "có thể suy ra"]):
            return SentenceClaimType.INTERPRETATION
        if any(w in t_low for w in ["specifically,", "furthermore,", "tóm lại,", "in contrast,"]):
            return SentenceClaimType.TRANSITION
        if ownership == IntellectualOwnership.SOURCE:
            return SentenceClaimType.SOURCE_CLAIM
        return SentenceClaimType.SYNTHESIS

    def compile_sentence(
        self,
        sentence: SentenceRecord,
        argument_bundle: Optional[ArgumentBundle] = None,
        verified_bundle: Optional[VerifiedClaimBundle] = None,
        result_bundle: Optional[ResultBundle] = None,
    ) -> SentenceRecord:
        """
        Chạy toàn bộ quy trình biên dịch chống ảo giác 10 điểm trên một câu.
        """
        text = sentence.text
        t_low = text.lower()
        issues: List[str] = []
        state = SentenceCompilationState.PASS

        # 1. Tuyên bố thực tế bên ngoài yêu cầu trích dẫn
        if sentence.claim_type in (SentenceClaimType.SOURCE_FACT, SentenceClaimType.SOURCE_CLAIM):
            if not sentence.citation_source_ids:
                issues.append("External factual/source claim requires verified citation from Citation Firewall.")
                state = SentenceCompilationState.NEEDS_CITATION
            else:
                # Xác minh nguồn tồn tại trong Bản đồ tham khảo
                for src_id in sentence.citation_source_ids:
                    src = self.repo.get_source(src_id)
                    if not src:
                        issues.append(f"Citation source ID '{src_id}' not found in Source Registry.")
                        state = SentenceCompilationState.REJECTED

        # 2. Kiểm tra yêu cầu trích dẫn (Nhắc 7 Phần 12)
        if sentence.citation_source_ids and sentence.target_claim_id:
            claim = self.repo.get_claim(sentence.target_claim_id)
            if claim:
                # Kiểm tra sự liên kết ngữ nghĩa: từ khóa hoặc phạm vi mệnh đề phù hợp
                claim_words = set(re.findall(r"\w+", claim.statement.lower()))
                sent_words = set(re.findall(r"\w+", t_low))
                overlap = len(claim_words.intersection(sent_words))
                if overlap < 2 and len(claim_words) > 3:
                    issues.append(f"Citation does not entail proposition: sentence claims '{text[:40]}...' but source claim '{claim.statement[:40]}...'.")
                    state = SentenceCompilationState.SCOPE_MISMATCH

        # 3. Kiểm tra rửa tiền và trộm cắp quyền sở hữu (Nhắc 7 Mục 15-16)
        if sentence.claim_type == SentenceClaimType.OUR_DESIGN and sentence.ownership == IntellectualOwnership.SOURCE:
            issues.append("OWNERSHIP_CONFLICT: OUR_DESIGN cannot be attributed to external SOURCE ownership.")
            state = SentenceCompilationState.OWNERSHIP_CONFLICT

        if sentence.claim_type == SentenceClaimType.SOURCE_CLAIM and sentence.ownership == IntellectualOwnership.OURS:
            issues.append("SOURCE_LAUNDERING: Prior art source claim labeled as OURS.")
            state = SentenceCompilationState.OWNERSHIP_CONFLICT

        # 4. Bảo vệ yêu cầu bồi thường mới lạ (Nhắc 7 Phần 17)
        for pattern in self.novelty_buzzwords:
            if re.search(pattern, t_low):
                # Xác minh xem đóng góp của ứng viên đã đăng ký có được phê duyệt tính mới hay không
                contributions = self.repo.list_candidate_contributions()
                has_approved_novelty = any(
                    c.candidate_id in text or c.novelty_justification for c in contributions
                )
                if not has_approved_novelty:
                    issues.append(f"OVERGENERALIZED: Unjustified novelty claim '{pattern}' without approved contribution review.")
                    state = SentenceCompilationState.OVERGENERALIZED

        # 5. Phòng chống lạm phát nhân quả (Nhắc 7 Mục 19)
        for c_pat in self.causal_words:
            if re.search(c_pat, t_low):
                if verified_bundle and verified_bundle.allowed_wording_strength in (
                    AllowedWordingStrength.DESCRIPTIVE_ONLY,
                    AllowedWordingStrength.ASSOCIATIONAL,
                ):
                    issues.append(f"OVERGENERALIZED: Causal claim '{c_pat}' used for non-causal (associational/dependency) evidence.")
                    state = SentenceCompilationState.OVERGENERALIZED

        # 6. Lan can miền (Nhắc 7 Phần 20-23)
        # 6a. Bảo vệ tuyến tính ATT&CK
        if "progresses from" in t_low and "tactic" in t_low:
            issues.append("OVERGENERALIZED: ATT&CK attack trajectory linearized without empirical campaign proof.")
            state = SentenceCompilationState.OVERGENERALIZED

        # 6b. Bất thường != Bảo vệ tấn công
        if "hdfs" in t_low and any(k in t_low for k in ["attack detection", "cyberattack", "tấn công"]):
            issues.append("SCOPE_MISMATCH: HDFS system-log anomaly benchmark conflated with cyberattack detection.")
            state = SentenceCompilationState.SCOPE_MISMATCH

        # 6c. Bảo vệ chống yêu cầu bồi thường quyền riêng tư
        if "privacy-preserving" in t_low or "bảo vệ quyền riêng tư tuyệt đối" in t_low:
            # Yêu cầu đánh giá tấn công quyền riêng tư đã được xác minh
            if not any("privacy" in nc.lower() for nc in sentence.numerical_claim_ids):
                issues.append("OVERGENERALIZED: Claimed 'privacy-preserving' without verified privacy membership/inversion attack test.")
                state = SentenceCompilationState.OVERGENERALIZED

        # 6ngày. Bảo vệ khả năng mở rộng hoạt động
        if any(k in t_low for k in ["real-time soc", "production ready", "sẵn sàng triển khai thực tế"]):
            # Yêu cầu bằng chứng số về thông lượng hoặc độ trễ
            has_ops_evidence = False
            for num_id in sentence.numerical_claim_ids:
                nc_obj = self.repo.get_numerical_claim(num_id)
                if nc_obj and nc_obj.unit in ("ms", "events/s", "MB"):
                    has_ops_evidence = True
            if not has_ops_evidence:
                issues.append("OVERGENERALIZED: Claimed 'real-time SOC readiness' without latency/throughput/memory verification.")
                state = SentenceCompilationState.OVERGENERALIZED

        # 7. Kiểm tra xác minh bằng số (Nhắc 7 Mục 24)
        if sentence.numerical_claim_ids:
            for num_id in sentence.numerical_claim_ids:
                num_claim = self.repo.get_numerical_claim(num_id)
                if not num_claim:
                    issues.append(f"NUMERICALLY_UNVERIFIED: Numerical claim ID '{num_id}' not found in registry.")
                    state = SentenceCompilationState.NUMERICALLY_UNVERIFIED
                elif num_claim.verification_status != VerificationStatus.VERIFIED:
                    issues.append(f"NUMERICALLY_UNVERIFIED: Numerical claim '{num_id}' has status {num_claim.verification_status.value}.")
                    state = SentenceCompilationState.NUMERICALLY_UNVERIFIED

        # 8. Kiểm tra xác minh phương trình (Nhắc 7 Mục 27)
        if sentence.equation_ids:
            for eq_id in sentence.equation_ids:
                eq = self.repo.get_equation(eq_id)
                if not eq:
                    issues.append(f"EQUATION_UNVERIFIED: Equation ID '{eq_id}' not found in Equation Registry.")
                    state = SentenceCompilationState.EQUATION_UNVERIFIED

        # Cập nhật bản ghi câu
        sentence.compilation_state = state
        sentence.issues = issues
        return sentence

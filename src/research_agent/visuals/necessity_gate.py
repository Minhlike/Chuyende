"""
Cổng cần thiết về thị giác (Quy tắc 8)
Đảm bảo rằng không có hình ảnh trang trí hoặc hình ảnh vô cớ nào được đưa vào báo cáo khoa học.
"""

from typing import Optional
from research_agent.visuals.schemas import (
    VisualNecessityEvaluation,
    VisualNecessityReason,
    VisualType,
    CreationMethod,
)


class VisualNecessityGate:
    """
    Xác thực xem hình ảnh được đề xuất có đáp ứng các tiêu chí cần thiết về mặt khoa học hay không trước khi đưa vào.
    """

    @staticmethod
    def evaluate(
        visual_id: str,
        visual_type: VisualType,
        purpose: str,
        clarity_statement: str,
        alternative_prose_deficiency: str,
        primary_reason: Optional[VisualNecessityReason] = None,
    ) -> VisualNecessityEvaluation:
        """
        Đánh giá sự cần thiết về mặt thị giác.
        Yêu cầu mục đích không trống rỗng, tuyên bố rõ ràng và giải thích cụ thể
        về lý do tại sao chỉ văn bản/văn xuôi không thể truyền tải đầy đủ cấu trúc hoặc dữ liệu định lượng.
        """
        if not purpose or len(purpose.strip()) < 10:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement or "",
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Purpose is empty or too vague (< 10 chars).",
            )

        if not clarity_statement or len(clarity_statement.strip()) < 15:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement or "",
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Clarity statement is too brief; must explain the single clear idea conveyed.",
            )

        if not alternative_prose_deficiency or len(alternative_prose_deficiency.strip()) < 15:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement,
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Alternative prose deficiency statement required (< 15 chars). Must justify why prose is deficient.",
            )

        # Loại bản đồ theo lý do mặc định nếu không được cung cấp
        if not primary_reason:
            if visual_type == VisualType.CONCEPTUAL_DIAGRAM:
                primary_reason = VisualNecessityReason.ARCHITECTURE
            elif visual_type in (VisualType.DATA_FIGURE, VisualType.STATISTICAL_CHART):
                primary_reason = VisualNecessityReason.QUANTITATIVE_COMPARISON
            elif visual_type == VisualType.NATIVE_TABLE:
                primary_reason = VisualNecessityReason.QUANTITATIVE_COMPARISON

        return VisualNecessityEvaluation(
            is_necessary=True,
            primary_reason=primary_reason,
            clarity_statement=clarity_statement.strip(),
            alternative_prose_deficiency=alternative_prose_deficiency.strip(),
            rejection_reason=None,
        )

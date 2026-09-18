"""
Hệ thống phân cấp ngoại lệ cho hệ thống kỹ thuật nghiên cứu
"""


class ResearchSystemError(Exception):
    """Ngoại lệ cơ bản cho tất cả các hoạt động của hệ thống nghiên cứu."""
    pass


class ConstitutionViolationError(ResearchSystemError):
    """Xảy ra khi một hành động vi phạm bất biến Hiến pháp nghiên cứu cơ bản."""
    def __init__(self, rule_id: str, message: str):
        self.rule_id = rule_id
        super().__init__(f"[{rule_id}] Constitution Violation: {message}")


class InvariantViolationError(ResearchSystemError):
    """Xảy ra khi hợp đồng hoặc bất biến dữ liệu nội bộ bị vi phạm."""
    pass


class SecurityPathViolationError(ResearchSystemError):
    """Xảy ra khi một thao tác I/O cố gắng vi phạm ranh giới không gian làm việc."""
    pass


class EntityNotFoundError(ResearchSystemError):
    """Xảy ra khi ID thực thể được tham chiếu không tồn tại."""
    pass


class DuplicateEntityError(ResearchSystemError):
    """Xảy ra khi một thực thể có ID hiện tại hoặc ràng buộc duy nhất được thêm vào."""
    pass


class EpistemicStateError(ResearchSystemError):
    """Tăng lên khi chuyển đổi trạng thái nhận thức không hợp lệ."""
    pass


class ProvenanceError(ConstitutionViolationError):
    """Tăng lên khi vi phạm yêu cầu về xuất xứ (RC-02, RC-08, RC-09, RC-10)."""
    def __init__(self, rule_id: str, message: str):
        super().__init__(rule_id=rule_id, message=message)

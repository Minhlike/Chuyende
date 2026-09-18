"""
Bảo vệ ngăn chặn đường dẫn và cách ly dữ liệu không đáng tin cậy (ADR-0005, RC-18)
"""

from pathlib import Path
from typing import Any, Dict
from research_agent.core.exceptions import SecurityPathViolationError
from research_agent.config import WorkspaceConfig, get_default_config


class PathGuard:
    """Bảo vệ chống lại việc tấn công duyệt thư mục (path traversal) tùy ý và ghi ngoài không gian làm việc."""
    def __init__(self, config: WorkspaceConfig | None = None):
        self.config = config or get_default_config()
        self.root = self.config.workspace_root.resolve()

    def resolve_safe_path(self, target: str | Path, must_exist: bool = False) -> Path:
        """
Giải quyết một đường dẫn một cách an toàn, đảm bảo nó nằm hoàn toàn bên trong thư mục gốc của không gian làm việc.

        Tăng:
            SecurityPathViolationError: Nếu đường dẫn đích thoát khỏi vùng làm việc gốc.
            FileNotFoundError: Nếu must_exist là True và thiếu tệp/thư mục.
        """
        p = Path(target)
        if not p.is_absolute():
            resolved = (self.root / p).resolve()
        else:
            resolved = p.resolve()

        # Kiểm tra ngăn chặn
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise SecurityPathViolationError(
                f"Path traversal detected: Target path '{resolved}' is outside workspace root '{self.root}'"
            )

        if must_exist and not resolved.exists():
            raise FileNotFoundError(f"Safe path does not exist: '{resolved}'")

        return resolved

    def assert_containment(self, target: str | Path) -> None:
        """Xác nhận rằng đường dẫn đích nằm trong thư mục gốc của không gian làm việc."""
        self.resolve_safe_path(target, must_exist=False)


class UntrustedDocumentPayload:
    """Bao bọc văn bản thô, nội dung PDF và mẫu nhật ký dưới dạng dữ liệu không thể thực thi (ADR-0005)."""

    def __init__(self, source_id: str, content: str, mime_type: str = "text/plain", metadata: Dict[str, Any] | None = None):
        self.source_id = source_id
        self.content = content
        self.mime_type = mime_type
        self.metadata = metadata or {}
        self.is_sanitized = True

    def get_raw_text(self) -> str:
        """Trả về nội dung dữ liệu đơn giản chưa được thực hiện."""
        return self.content

    def __repr__(self) -> str:
        return f"<UntrustedDocumentPayload source={self.source_id} len={len(self.content)}>"

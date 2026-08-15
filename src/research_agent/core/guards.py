"""
Path Containment Guard and Untrusted Data Isolation (ADR-0005, RC-18)
"""

from pathlib import Path
from typing import Any, Dict
from research_agent.core.exceptions import SecurityPathViolationError
from research_agent.config import WorkspaceConfig, get_default_config


class PathGuard:
    """Guards against arbitrary path traversal and out-of-workspace writes."""

    def __init__(self, config: WorkspaceConfig | None = None):
        self.config = config or get_default_config()
        self.root = self.config.workspace_root.resolve()

    def resolve_safe_path(self, target: str | Path, must_exist: bool = False) -> Path:
        """Resolve a path safely, ensuring it is strictly inside the workspace root.
        
        Raises:
            SecurityPathViolationError: If target path escapes workspace root.
            FileNotFoundError: If must_exist is True and file/dir is missing.
        """
        p = Path(target)
        if not p.is_absolute():
            resolved = (self.root / p).resolve()
        else:
            resolved = p.resolve()

        # Check containment
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
        """Assert that target path is within workspace root."""
        self.resolve_safe_path(target, must_exist=False)


class UntrustedDocumentPayload:
    """Wraps raw text, PDF content, and log samples as non-executable data (ADR-0005)."""

    def __init__(self, source_id: str, content: str, mime_type: str = "text/plain", metadata: Dict[str, Any] | None = None):
        self.source_id = source_id
        self.content = content
        self.mime_type = mime_type
        self.metadata = metadata or {}
        self.is_sanitized = True

    def get_raw_text(self) -> str:
        """Return the unexecuted plain data content."""
        return self.content

    def __repr__(self) -> str:
        return f"<UntrustedDocumentPayload source={self.source_id} len={len(self.content)}>"

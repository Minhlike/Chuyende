"""
Cấu hình và lịch thi đấu Pytest
"""

import sys
import tempfile
from pathlib import Path
import pytest

# Đảm bảo src nằm trong sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from research_agent.config import WorkspaceConfig
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.storage.file_store import CanonicalFileStore


@pytest.fixture
def temp_workspace(tmp_path: Path) -> WorkspaceConfig:
    """Lịch thi đấu cung cấp một không gian làm việc tạm thời bị cô lập."""
    cfg = WorkspaceConfig(workspace_root=tmp_path)
    cfg.ensure_directories()
    return cfg


@pytest.fixture
def db_manager(temp_workspace: WorkspaceConfig) -> DatabaseManager:
    """Lịch thi đấu cung cấp Trình quản lý cơ sở dữ liệu được khởi tạo."""
    return DatabaseManager(config=temp_workspace)


@pytest.fixture
def repository(db_manager: DatabaseManager) -> ResearchRepository:
    """Fixture cung cấp một ResearchRepository sạch sẽ."""
    return ResearchRepository(db_manager=db_manager)


@pytest.fixture
def file_store(temp_workspace: WorkspaceConfig) -> CanonicalFileStore:
    """Lịch thi đấu cung cấp CanonicalFileStore."""
    return CanonicalFileStore(config=temp_workspace)

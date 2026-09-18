"""
script khởi tạo cơ sở dữ liệu
"""

import sys
from pathlib import Path

# Thêm src vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.schemas.project import ResearchProject
from research_agent.logging import configure_logging


def main():
    config = get_default_config()
    config.ensure_directories()
    logger = configure_logging(config)
    logger.info(f"Initializing database at: {config.db_path}")

    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)

    # Siêu dữ liệu dự án mặc định của Bootstrap
    project = ResearchProject()
    repo.save_project(project)
    logger.info(f"Initialized project record: {project.project_id} - '{project.title}'")
    print(f"SUCCESS: Database and project initialized at {config.db_path}")


if __name__ == "__main__":
    main()

"""
Roadmap Integrity Validation Script (Section 25)
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.cli import validate_roadmap_command


def main():
    config = get_default_config()
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)
    exit_code = validate_roadmap_command(repo)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

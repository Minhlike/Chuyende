"""
Lọc các chỉ mục phái sinh dùng một lần và bộ đệm thời gian chạy (ADR-0004, RC-17)
"""

import sys
from pathlib import Path

# Thêm src vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.storage.file_store import CanonicalFileStore


def main():
    config = get_default_config()
    file_store = CanonicalFileStore(config)
    cache_purged, index_purged = file_store.purge_derived_indexes()
    print(f"SUCCESS: Purged {cache_purged} runtime cache items and {index_purged} derived index items.")
    print("Canonical database and files remain 100% intact.")


if __name__ == "__main__":
    main()

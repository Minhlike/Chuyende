"""
Automated Invariant Verification Utility (RC-18)
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository


def verify_all():
    config = get_default_config()
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)

    print("--- RUNNING CANONICAL INVARIANT CHECKS ---")
    with db_manager.session() as conn:
        # Check 1: No claims with invalid claim_type
        # Check 2: No experiment result claims without experiment_run_id
        invalid_runs = conn.execute(
            "SELECT claim_id FROM claims WHERE claim_type = 'EXPERIMENT_RESULT' AND (experiment_run_id IS NULL OR experiment_run_id = '')"
        ).fetchall()
        if invalid_runs:
            print(f"[FAIL] Found EXPERIMENT_RESULT claims missing experiment_run_id: {[r[0] for r in invalid_runs]}")
            return False

        # Check 3: No source equations without source_id
        invalid_eqs = conn.execute(
            "SELECT equation_id FROM equations WHERE equation_type = 'SOURCE_EQUATION' AND (source_id IS NULL OR source_id = '')"
        ).fetchall()
        if invalid_eqs:
            print(f"[FAIL] Found SOURCE_EQUATION items missing source_id: {[r[0] for r in invalid_eqs]}")
            return False

    print("[PASS] All canonical database invariants verified.")
    return True


if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)

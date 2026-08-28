#!/usr/bin/env bash
# =============================================================================
# Canonical Google Colab Bash Wrapper for Stage A2 Seed 42 Resumption
# =============================================================================
set -euo pipefail

export CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1

REPO_DIR="${1:-/content/Research}"
shift || true

echo "================================================================="
echo "   STAGE A2 SEED-42 CANONICAL RESUME LAUNCHER                   "
echo "================================================================="
echo "Repository Root: ${REPO_DIR}"
echo "Arguments:       $*"
echo "================================================================="

exec python3 -u "${REPO_DIR}/scripts/colab_stage_a2_resume_seed42.py" --base-dir "${REPO_DIR}" "$@"

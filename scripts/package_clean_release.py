# -*- coding: utf-8 -*-
"""
Deterministic Packaging Script for Final Clean Repository (Minhlike/chuyen-de-chuyen-sau)
Copies only KEEP_FINAL and essential KEEP_EVIDENCE files from the working repository D:\Research
into the target clean repository D:\chuyen-de-chuyen-sau.
Strictly excludes all DEV_ONLY, TEMP/BACKUP, and LARGE_EXTERNAL files.
"""

import os
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SRC_DIR = Path(r"D:\Research")
DEST_DIR = Path(r"D:\chuyen-de-chuyen-sau")

ESSENTIAL_SCRIPTS = [
    "gpu_smoke_test.py",
    "evaluate_nineplus_v3.py",
    "run_nineplus_confirmatory.py",
    "provision_cleanroom_artifacts.py",
    "validate_experiment_index.py",
    "run_h1_masking_ablation.py",
    "run_h2_sequence_noparam_sensitivity.py"
]

def copy_file_clean(src_path: Path, dest_path: Path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest_path)
    print(f"  [COPIED] {src_path.relative_to(SRC_DIR)} -> {dest_path.relative_to(DEST_DIR)}")

def copy_dir_clean(src_dir: Path, dest_dir: Path, ignore_patterns=None):
    if not src_dir.exists():
        return
    for root, dirs, files in os.walk(src_dir):
        # Filter out __pycache__, .pytest_cache, .git
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git", "runtime", "backups", "lo_build")]
        rel_root = Path(root).relative_to(src_dir)
        target_dir = dest_dir / rel_root
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            # Skip python byte-code, temp, pt, pth, tar.gz, tmp
            if f.endswith((".pyc", ".pyo", ".pt", ".pth", ".tar.gz", ".tmp", ".db", ".sqlite")):
                continue
            if f.startswith(("~$", "tmp")):
                continue
            if ignore_patterns and any(p in f for p in ignore_patterns):
                continue
            src_file = Path(root) / f
            dest_file = target_dir / f
            shutil.copy2(src_file, dest_file)

def main():
    print("=" * 80)
    print("  PACKAGING FINAL CLEAN REPOSITORY")
    print(f"  Source: {SRC_DIR}")
    print(f"  Target: {DEST_DIR}")
    print("=" * 80)

    if DEST_DIR.exists():
        # Preserve .git if it already exists
        git_dir = DEST_DIR / ".git"
        temp_git = Path(r"D:\_temp_git_backup")
        if git_dir.exists():
            if temp_git.exists():
                shutil.rmtree(temp_git)
            shutil.move(str(git_dir), str(temp_git))
        shutil.rmtree(DEST_DIR)
        DEST_DIR.mkdir(parents=True, exist_ok=True)
        if temp_git.exists():
            shutil.move(str(temp_git), str(DEST_DIR / ".git"))
    else:
        DEST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Root files
    root_files = [
        "README.md",
        "HUONG_DAN_CHAY_VA_XAC_MINH.md",
        "Chuyên đề chuyên sâu.docx",
        "Chuyên đề chuyên sâu.pdf",
        "pyproject.toml",
        "requirements-lock.txt",
        ".gitignore",
        ".env.example"
    ]
    print("\n1. Copying Root Files:")
    for rf in root_files:
        p = SRC_DIR / rf
        if p.exists():
            copy_file_clean(p, DEST_DIR / rf)
        else:
            print(f"  [MISSING] {rf}")

    # 2. Source code (src/)
    print("\n2. Copying src/ (clean python library):")
    copy_dir_clean(SRC_DIR / "src", DEST_DIR / "src")

    # 3. Essential scripts (scripts/)
    print("\n3. Copying Essential scripts/:")
    for s in ESSENTIAL_SCRIPTS:
        p = SRC_DIR / "scripts" / s
        if p.exists():
            copy_file_clean(p, DEST_DIR / "scripts" / s)
        else:
            print(f"  [MISSING SCRIPT] {s}")

    # 4. manual_reproduction/
    print("\n4. Copying manual_reproduction/:")
    copy_dir_clean(SRC_DIR / "manual_reproduction", DEST_DIR / "manual_reproduction")

    # 5. cleanroom/
    print("\n5. Copying cleanroom/:")
    copy_dir_clean(SRC_DIR / "cleanroom", DEST_DIR / "cleanroom")

    # 6. experiments/ (index, manifest, evaluation_v3, confirmatory manifests)
    print("\n6. Copying experiments/ (index, manifests, protocol, configs):")
    copy_file_clean(SRC_DIR / "experiments" / "experiment_index.csv", DEST_DIR / "experiments" / "experiment_index.csv")
    copy_file_clean(SRC_DIR / "experiments" / "nineplus" / "ARTIFACT-MANIFEST.json", DEST_DIR / "experiments" / "nineplus" / "ARTIFACT-MANIFEST.json")
    
    # evaluation_v3 (JSONs only)
    copy_dir_clean(SRC_DIR / "experiments" / "nineplus" / "evaluation_v3", DEST_DIR / "experiments" / "nineplus" / "evaluation_v3")
    
    # confirmatory (JSON/JSONL only, no *.pt)
    conf_dir = SRC_DIR / "experiments" / "nineplus" / "confirmatory"
    if conf_dir.exists():
        for d in conf_dir.iterdir():
            if d.is_dir():
                target_conf = DEST_DIR / "experiments" / "nineplus" / "confirmatory" / d.name
                for f in ["RUN-MANIFEST.json", "TRAIN-LOG.jsonl"]:
                    p = d / f
                    if p.exists():
                        copy_file_clean(p, target_conf / f)

    for sub in ["protocol", "configs", "manifests", "environment"]:
        p = SRC_DIR / "experiments" / sub
        if p.exists():
            copy_dir_clean(p, DEST_DIR / "experiments" / sub)

    # 7. datasets/ (manifests only, gitkeeps)
    print("\n7. Copying datasets/ (manifests only):")
    copy_dir_clean(SRC_DIR / "datasets" / "manifests", DEST_DIR / "datasets" / "manifests")
    (DEST_DIR / "datasets" / "raw").mkdir(parents=True, exist_ok=True)
    (DEST_DIR / "datasets" / "raw" / ".gitkeep").touch()
    (DEST_DIR / "datasets" / "processed").mkdir(parents=True, exist_ok=True)
    (DEST_DIR / "datasets" / "processed" / ".gitkeep").touch()

    # 8. tests/
    print("\n8. Copying tests/:")
    copy_dir_clean(SRC_DIR / "tests", DEST_DIR / "tests")

    # 9. docs/
    print("\n9. Copying docs/:")
    copy_dir_clean(SRC_DIR / "docs", DEST_DIR / "docs")

    # 10. specs, memory, reference, artifacts
    for sub in ["research_specs", "memory", "KMA_REFERENCE", "skills"]:
        p = SRC_DIR / sub
        if p.exists():
            print(f"\n10. Copying {sub}/:")
            copy_dir_clean(p, DEST_DIR / sub)

    art_manifest = SRC_DIR / "artifacts" / "figure_math_manifest.md"
    if art_manifest.exists():
        copy_file_clean(art_manifest, DEST_DIR / "artifacts" / "figure_math_manifest.md")

    print("\n" + "=" * 80)
    print("  PACKAGING COMPLETE!")
    print(f"  Target directory: {DEST_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

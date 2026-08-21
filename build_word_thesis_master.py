"""
Root runner for Master Academic Word Document Builder with Frozen Chapter Hash Invariant.
"""

import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

# Ensure D:\Research\src is in sys.path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

CANONICAL_CH1_HASH = "6097fb1f051573adb21ce65a3466b41d50ba9b8bb9a526c96563e41705c81d5e"


def verify_chapter_1_frozen_hash():
    code_path = Path(__file__).parent / "src" / "research_agent" / "composition" / "build_word_visual_qa.py"
    lines = code_path.read_text(encoding="utf-8").splitlines()
    start = None
    end = None
    for i, l in enumerate(lines):
        if 'add_h1("TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT' in l:
            start = i
        elif 'add_h1("PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG' in l:
            end = i
            break

    if start is None or end is None:
        raise RuntimeError(f"Could not locate Chapter 1 boundaries in {code_path}")

    ch1_block = "\n".join(lines[start:end])
    curr_hash = hashlib.sha256(ch1_block.encode("utf-8")).hexdigest()
    if curr_hash != CANONICAL_CH1_HASH:
        raise ValueError(
            f"[CRITICAL VIOLATION] Chapter 1 code has mutated! Expected {CANONICAL_CH1_HASH}, got {curr_hash}."
        )
    print(f"[PASS] Frozen Chapter 1 SHA-256 Hash Verified: {curr_hash[:16]}... (UNCHANGED)")


if __name__ == "__main__":
    verify_chapter_1_frozen_hash()
    from research_agent.composition.build_word_visual_qa import build_and_audit_document

    pdf_out = build_and_audit_document()
    print(f"\n==========================================")
    print(f"MASTER BUILD COMPLETE: {pdf_out}")
    print(f"==========================================")

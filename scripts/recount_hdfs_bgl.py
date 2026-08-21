# -*- coding: utf-8 -*-
import tarfile
import re
from pathlib import Path

def recount_hdfs(tar_path: Path):
    print("Recounting HDFS from", tar_path)
    with tarfile.open(tar_path, "r:gz") as tar:
        f = tar.extractfile("HDFS.log")
        total = 0
        block_cnt = 0
        no_block_cnt = 0
        malformed = 0
        for line in f:
            total += 1
            s = line.decode("utf-8", errors="ignore").strip()
            parts = s.split(" ", 5)
            if len(parts) < 6:
                malformed += 1
            elif re.search(r"blk_[-0-9]+", parts[5]):
                block_cnt += 1
            else:
                no_block_cnt += 1
    print(f"HDFS Results: total={total}, block_cnt={block_cnt}, no_block_cnt={no_block_cnt}, malformed={malformed}")
    assert total == block_cnt + no_block_cnt + malformed
    return total, block_cnt, no_block_cnt, malformed

def recount_bgl(tar_path: Path):
    print("Recounting BGL from", tar_path)
    with tarfile.open(tar_path, "r:gz") as tar:
        f = tar.extractfile("BGL.log")
        total = 0
        min_ts = None
        max_ts = None
        for line in f:
            total += 1
            s = line.decode("utf-8", errors="ignore").strip()
            parts = s.split(" ", 3)
            if len(parts) >= 2 and parts[1].isdigit():
                ts = int(parts[1])
                if min_ts is None or ts < min_ts:
                    min_ts = ts
                if max_ts is None or ts > max_ts:
                    max_ts = ts
    print(f"BGL Results: total={total}, min_ts={min_ts}, max_ts={max_ts}")
    return total, min_ts, max_ts

if __name__ == "__main__":
    base_dir = Path("/mnt/d/Research") if Path("/mnt/d/Research").exists() else Path(r"D:\Research")
    recount_hdfs(base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
    recount_bgl(base_dir / "datasets" / "raw" / "bgl" / "BGL.tar.gz")

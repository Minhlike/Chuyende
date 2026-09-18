# -*- coding: utf-8 -*-
"""
Công cụ vật chất hóa một lần cho các Sự kiện đồ thị HDFS.
Truyền phát HDFS_1.tar.gz một lần và tách các sự kiện thành các phần tách TRAIN và VAL
bị ràng buộc chặt chẽ với quyền phân chia SPL-HDFS-001.
Bộ nhớ đệm dẫn đến tập dữ liệu/bộ đệm/hdfs_graph_events.pt.
"""

import time
import tarfile
import torch
from pathlib import Path
from typing import Dict, Any, List, Set

from research_agent.experiments.data.hdfs_split_authority import HDFSSplitAuthority
from research_agent.experiments.extractor.graph_builder import HDFSGraphBuilder, HDFS_RELATION_RULES, TestSetSealedError

def materialize_and_cache(base_dir: Path):
    cache_path = base_dir / "datasets" / "cache" / "hdfs_graph_events.pt"
    if cache_path.exists():
        print(f"[CACHE] Found existing cache at {cache_path}")
        d = torch.load(cache_path, weights_only=False)
        print(f"[CACHE] Train events: {len(d['train_events'])}, Val events: {len(d['val_events'])}")
        return d

    print("[MATERIALIZATION] Starting single-pass streaming extraction of HDFS graph events...")
    raw_tar_path = base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"
    split_auth = HDFSSplitAuthority(base_dir=base_dir, raw_tar_path=raw_tar_path)
    split_data = split_auth.get_split()

    train_block_ids: Set[str] = set(split_data["selected_train_block_ids"])
    val_block_ids: Set[str] = set(split_data["selected_val_block_ids"])
    test_block_ids: Set[str] = set(split_data.get("selected_test_block_ids", []))

    print(f"[SPLIT] Authorized Train block IDs: {len(train_block_ids)}")
    print(f"[SPLIT] Authorized Val block IDs: {len(val_block_ids)}")

    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth, raw_tar_path=raw_tar_path)

    train_events: List[Dict[str, Any]] = []
    val_events: List[Dict[str, Any]] = []

    t0 = time.time()
    with tarfile.open(raw_tar_path, "r:gz") as tar:
        log_member = None
        for m in tar.getmembers():
            if m.name.endswith("HDFS.log") or m.name.endswith(".log"):
                log_member = m
                break
        if not log_member:
            raise FileNotFoundError("HDFS.log not found in archive")

        f_obj = tar.extractfile(log_member)
        line_idx = 0

        for line_bytes in f_obj:
            line_idx += 1
            line_str = line_bytes.decode("utf-8", errors="ignore").strip()
            event, reject_reason, blk_id = builder.parse_raw_line(line_str, line_idx)

            if blk_id is None:
                continue

            # Kiểm tra tường lửa kiểm tra nghiêm ngặt: Bộ kiểm tra phải được đọc hoặc phân tích cú pháp NEVER để tìm các tính năng
            if blk_id in test_block_ids:
                continue

            if event is None:
                continue

            if blk_id in train_block_ids:
                train_events.append(event)
            elif blk_id in val_block_ids:
                val_events.append(event)

    t_scan = time.time() - t0
    print(f"[MATERIALIZATION] Single pass completed in {t_scan:.2f}s.")
    print(f"[MATERIALIZATION] Raw train events extracted: {len(train_events)}")
    print(f"[MATERIALIZATION] Raw val events extracted: {len(val_events)}")

    # Sắp xếp từng phần theo thứ tự thời gian
    train_events.sort(key=lambda e: (e["event_timestamp_utc_exact"], e["raw_line_index"]))
    val_events.sort(key=lambda e: (e["event_timestamp_utc_exact"], e["raw_line_index"]))

    assert len(train_events) == 586577, f"Expected 586577 train events, got {len(train_events)}"
    assert len(val_events) == 119531, f"Expected 119531 val events, got {len(val_events)}"
    print("[VERIFICATION] Event count conservation verified exactly (586,577 Train, 119,531 Val)!")

    # Định dạng sự kiện cho trình trích xuất biểu đồ (xây dựng bản đồ thực thể và vectơ thuộc tính)
    print("[PROCESSING] Formatting event node attributes and edge vectors...")
    entity_to_id = {"<UNK>": 0}
    for ev in train_events:
        for n in [ev["source_node"], ev["dest_node"]]:
            if n not in entity_to_id:
                entity_to_id[n] = len(entity_to_id)
    # Thực thể Val (ánh xạ quy nạp)
    for ev in val_events:
        for n in [ev["source_node"], ev["dest_node"]]:
            if n not in entity_to_id:
                entity_to_id[n] = len(entity_to_id)

    print(f"[PROCESSING] Total unique graph entities: {len(entity_to_id)}")

    def format_event(ev: Dict[str, Any]) -> Dict[str, Any]:
        s_id = entity_to_id[ev["source_node"]]
        d_id = entity_to_id[ev["dest_node"]]
        r_id = ev["relation_id"]  # 1..8
        ts = float(ev["event_timestamp_utc_exact"])
        
        # Thuộc tính nút 16 độ mờ (loại một điểm nóng trong 4 độ mờ đầu tiên)
        s_attr = [0.0] * 16
        s_attr[ev["source_type"]] = 1.0
        d_attr = [0.0] * 16
        d_attr[ev["dest_type"]] = 1.0
        
        # Tính năng 16 cạnh mờ (quan hệ một điểm nóng trong 8 mờ đầu tiên, kích thước trong mờ 8)
        e_feat = [0.0] * 16
        e_feat[r_id - 1] = 1.0
        e_feat[8] = float(ev.get("size_bytes", 0.0) or 0.0) / 1e6

        # Giữ các trường gốc cho TemporalGraphViewEncode + thêm các trường được định dạng
        formatted = dict(ev)
        formatted.update({
            "timestamp": ts,
            "src": s_id,
            "dst": d_id,
            "relation_type": r_id,
            "src_node_attr": s_attr,
            "dst_node_attr": d_attr,
            "edge_features": e_feat
        })
        return formatted

    train_formatted = [format_event(e) for e in train_events]
    val_formatted = [format_event(e) for e in val_events]

    package = {
        "dataset_split": "SPL-HDFS-001",
        "train_events": train_formatted,
        "val_events": val_formatted,
        "num_train_events": len(train_formatted),
        "num_val_events": len(val_formatted),
        "entity_to_id": entity_to_id,
        "created_at_epoch": time.time()
    }

    print(f"[CACHE] Saving package to {cache_path}...")
    torch.save(package, cache_path)
    print(f"[CACHE] Saved {cache_path.stat().st_size / (1024**2):.1f} MB successfully.")
    return package

if __name__ == "__main__":
    base_dir = Path(r"D:\Research")
    materialize_and_cache(base_dir)

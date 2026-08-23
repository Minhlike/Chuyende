# -*- coding: utf-8 -*-
"""
Canonical HDFS Causal Event-Entity Graph Builder & Parser (Contract V1.1)
Constructs causal temporal graph streams strictly grounded in raw HDFS audit logs:
  - Extractable entities: DATA_BLOCK, STORAGE_NODE, MANAGEMENT_SYSTEM, EXECUTION_THREAD
  - Extractable relations: RECEIVES_BLOCK, STORES_BLOCK, ALLOCATES_BLOCK, MONITORS_BLOCK,
                           SERVES_BLOCK, UPDATES_BLOCK_MAP, REPLICATES_BLOCK, DELETES_BLOCK
  - Fixed node targets: x_v_fixed_priv (6-dim: 4-dim one-hot type + 2-dim log1p causal in/out degrees)
  - Strict Test Firewall: TestSetSealedError enforced on test partition requests.
  - Conservation Law: raw_eligible_events = materialized_graph_events + explicitly_rejected_events
"""

import os
import re
import tarfile
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

class TestSetSealedError(Exception):
    """Raised when any code attempts to access the sealed Test split."""
    __test__ = False

HDFS_GRAPH_EXTRACTION_RULES = [
    # 1. RECEIVES_BLOCK: StorageNode (dest) -> DataBlock
    (re.compile(r"Receiving block (blk_[-0-9]+) src: (/?[0-9\.:]+) dest: (/?[0-9\.:]+)"), "RECEIVES_BLOCK", 1),
    # 2. STORES_BLOCK: StorageNode (src) -> DataBlock (with block size)
    (re.compile(r"Received block (blk_[-0-9]+) of size (\d+) from (/?[0-9\.:]+)"), "STORES_BLOCK", 2),
    # 3. ALLOCATES_BLOCK: FSNamesystem -> DataBlock
    (re.compile(r"BLOCK\* NameSystem\.allocateBlock: (.*)\. (blk_[-0-9]+)"), "ALLOCATES_BLOCK", 3),
    # 4. MONITORS_BLOCK: PacketResponder -> DataBlock
    (re.compile(r"PacketResponder (\d+) for block (blk_[-0-9]+) terminating"), "MONITORS_BLOCK", 4),
    # 5. SERVES_BLOCK: StorageNode -> DataBlock
    (re.compile(r"Served block (blk_[-0-9]+) to (/?[0-9\.:]+)"), "SERVES_BLOCK", 5),
    # 6. UPDATES_BLOCK_MAP: StorageNode -> DataBlock (with block size)
    (re.compile(r"BLOCK\* NameSystem\.addStoredBlock: blockMap updated: ([0-9\.:]+) is added to (blk_[-0-9]+) size (\d+)"), "UPDATES_BLOCK_MAP", 6),
    # 7. REPLICATES_BLOCK: StorageNode -> DataBlock
    (re.compile(r"BLOCK\* ask ([0-9\.:]+) to replicate (blk_[-0-9]+) to datanode\(s\) (.*)"), "REPLICATES_BLOCK", 7),
    # 8. DELETES_BLOCK: FSNamesystem -> DataBlock
    (re.compile(r"(?:BLOCK\* ask ([0-9\.:]+) to delete (blk_[-0-9]+)|Deleting block (blk_[-0-9]+) file (.*))"), "DELETES_BLOCK", 8),
]


class HDFSGraphBuilder:
    def __init__(self, base_dir: Path, max_train_events: int = 100000, max_val_events: int = 20000):
        self.base_dir = base_dir
        self.raw_tar_path = self.base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"
        self.max_train_events = max_train_events
        self.max_val_events = max_val_events

        self.node_to_id: Dict[str, int] = {"<UNK_NODE>": 0}
        self.node_to_type: Dict[str, int] = {"<UNK_NODE>": 0}
        self.train_max_in_degree = 1.0
        self.train_max_out_degree = 1.0
        self.train_mean_size_bytes = 1.0

    def parse_raw_line(self, line_str: str, line_idx: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Parses a single raw HDFS log line into a typed graph event."""
        # Format: Date Time Pid Level Component: Message
        # E.g.: 081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608961267986555555 src: /10.250.19.102:54106 dest: /10.250.19.102:50010
        parts = line_str.strip().split(" ", 5)
        if len(parts) < 6:
            return None, "MALFORMED_HEADER"

        d_str, t_str, pid, level, comp, msg = parts
        try:
            # Parse timestamp to UTC epoch
            # Year is 2008 (08)
            dt = datetime.strptime(f"20{d_str} {t_str}", "%Y%m%d %H%M%S")
            ts_epoch = float(dt.replace(tzinfo=timezone.utc).timestamp())
        except Exception:
            return None, "TIMESTAMP_PARSE_ERROR"

        for pattern, rel_name, rel_id in HDFS_GRAPH_EXTRACTION_RULES:
            m = pattern.search(msg)
            if m:
                # Extract source and destination depending on relation
                size_bytes = 0.0
                if rel_name == "RECEIVES_BLOCK":
                    blk_id = m.group(1)
                    src_node = m.group(3).lstrip("/")  # Dest storage node receives
                    dest_node = blk_id
                    src_type = 1  # STORAGE_NODE
                    dest_type = 0  # DATA_BLOCK
                elif rel_name == "STORES_BLOCK":
                    blk_id = m.group(1)
                    size_bytes = float(m.group(2))
                    src_node = m.group(3).lstrip("/")
                    dest_node = blk_id
                    src_type = 1
                    dest_type = 0
                elif rel_name == "ALLOCATES_BLOCK":
                    blk_id = m.group(2)
                    src_node = "FSNamesystem"
                    dest_node = blk_id
                    src_type = 2  # MANAGEMENT_SYSTEM
                    dest_type = 0
                elif rel_name == "MONITORS_BLOCK":
                    thread_id = m.group(1)
                    blk_id = m.group(2)
                    src_node = f"PacketResponder_{thread_id}"
                    dest_node = blk_id
                    src_type = 3  # EXECUTION_THREAD
                    dest_type = 0
                elif rel_name == "SERVES_BLOCK":
                    blk_id = m.group(1)
                    src_node = m.group(2).lstrip("/")
                    dest_node = blk_id
                    src_type = 1
                    dest_type = 0
                elif rel_name == "UPDATES_BLOCK_MAP":
                    src_node = m.group(1).lstrip("/")
                    blk_id = m.group(2)
                    size_bytes = float(m.group(3))
                    dest_node = blk_id
                    src_type = 1
                    dest_type = 0
                elif rel_name == "REPLICATES_BLOCK":
                    src_node = m.group(1).lstrip("/")
                    blk_id = m.group(2)
                    dest_node = blk_id
                    src_type = 1
                    dest_type = 0
                elif rel_name == "DELETES_BLOCK":
                    src_node = "FSNamesystem"
                    blk_id = m.group(2) if m.group(2) else m.group(3)
                    dest_node = blk_id
                    src_type = 2
                    dest_type = 0
                else:
                    return None, "UNMAPPED_RELATION"

                event = {
                    "raw_line_index": line_idx,
                    "event_timestamp_utc": ts_epoch,
                    "relation_id": rel_id,
                    "relation_name": rel_name,
                    "source_node": src_node,
                    "source_type": src_type,
                    "dest_node": dest_node,
                    "dest_type": dest_type,
                    "size_bytes": size_bytes
                }
                return event, None

        return None, "NO_BLOCK_ID_MATCH"

    def materialize_split(self, split_name: str) -> Dict[str, Any]:
        """Materializes graph events for Train or Val. Strictly prohibits Test split."""
        if split_name.upper() == "TEST":
            raise TestSetSealedError("Attempted to materialize sealed Test graph split!")

        if not self.raw_tar_path.exists():
            raise FileNotFoundError(f"Raw HDFS archive missing at {self.raw_tar_path}")

        events = []
        rejected_counts = {}
        total_scanned = 0

        # Read lines from tar
        with tarfile.open(self.raw_tar_path, "r:gz") as tar:
            log_member = None
            for m in tar.getmembers():
                if m.name.endswith("HDFS.log") or m.name.endswith(".log"):
                    log_member = m
                    break
            if not log_member:
                raise FileNotFoundError("HDFS.log not found inside archive")
            
            f = tar.extractfile(log_member)
            line_idx = 0
            # Target event limits
            target_limit = self.max_train_events if split_name.upper() == "TRAIN" else self.max_val_events
            offset = 0 if split_name.upper() == "TRAIN" else self.max_train_events

            for raw_line in f:
                line_idx += 1
                if split_name.upper() == "VAL" and line_idx <= offset:
                    continue

                total_scanned += 1
                line_str = raw_line.decode("utf-8", errors="replace")
                event, reject_reason = self.parse_raw_line(line_str, line_idx)

                if event is not None:
                    events.append(event)
                    if len(events) >= target_limit:
                        break
                else:
                    rejected_counts[reject_reason] = rejected_counts.get(reject_reason, 0) + 1

        # Sort strictly by canonical tie-breaking key: (event_timestamp_utc, raw_line_index)
        events.sort(key=lambda e: (e["event_timestamp_utc"], e["raw_line_index"]))

        # Build vocabulary strictly on Train
        if split_name.upper() == "TRAIN":
            sizes = []
            for e in events:
                src, s_type = e["source_node"], e["source_type"]
                dst, d_type = e["dest_node"], e["dest_type"]
                if src not in self.node_to_id:
                    self.node_to_id[src] = len(self.node_to_id)
                    self.node_to_type[src] = s_type
                if dst not in self.node_to_id:
                    self.node_to_id[dst] = len(self.node_to_id)
                    self.node_to_type[dst] = d_type
                if e["size_bytes"] > 0:
                    sizes.append(e["size_bytes"])
            if sizes:
                self.train_mean_size_bytes = float(sum(sizes) / len(sizes))

        return {
            "split": split_name.upper(),
            "raw_scanned": total_scanned,
            "materialized_events": len(events),
            "rejected_counts": rejected_counts,
            "total_rejected": sum(rejected_counts.values()),
            "events": events
        }

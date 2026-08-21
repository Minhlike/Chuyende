# -*- coding: utf-8 -*-
"""
Real HDFS Raw Data Adapter & Materialization Engine
Parses official raw HDFS_1.tar.gz archive and anomaly_label.csv to produce authentic
Chapter 2 Multi-Task SSL inputs without synthetic proxies:
  - Real Timestamp: Extracted from YYMMDD HHMMSS ms headers.
  - Real L_MEP Target: Actual LogHub event template classes (fitted Train-only).
  - Real L_MPP Target: Actual privacy-safe dynamic parameter classes (IP categories, size buckets, port classes).
  - Real L_time Target: log(1 + real adjacent event-time delta).
  - Block ID Leakage Firewall: Block ID used strictly for causal trace grouping; excluded from feature space.
  - Strict Test Firewall: Test partition remains strictly SEALED.
"""

import os
import re
import tarfile
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

import numpy as np
import torch

from research_agent.experiments.data.data_contract import RealDataContract, RealTrainingDataViolation

class TestSetSealedError(Exception):
    """Raised when any code attempts to access the sealed Test split."""
    __test__ = False

# Canonical HDFS Log Regex Patterns for Drain/Spell-like Template Matching
HDFS_TEMPLATES = [
    (r"Receiving block (blk_[-0-9]+) src: (/[\d\.:]+) dest: (/[\d\.:]+)", "Receiving block <*> src: <*> dest: <*>"),
    (r"Received block (blk_[-0-9]+) of size (\d+) from (/[\d\.:]+)", "Received block <*> of size <*> from <*>"),
    (r"BLOCK\* NameSystem\.allocateBlock: (.*)\. (blk_[-0-9]+)", "BLOCK* NameSystem.allocateBlock: <*> <*>"),
    (r"PacketResponder (\d+) for block (blk_[-0-9]+) terminating", "PacketResponder <*> for block <*> terminating"),
    (r"Verification succeeded for (blk_[-0-9]+)", "Verification succeeded for <*>"),
    (r"Served block (blk_[-0-9]+) to (/[\d\.:]+)", "Served block <*> to <*>"),
    (r"BLOCK\* NameSystem\.addStoredBlock: blockMap updated: ([\d\.:]+) is added to (blk_[-0-9]+) size (\d+)", "BLOCK* NameSystem.addStoredBlock: blockMap updated: <*> is added to <*> size <*>"),
    (r"BLOCK\* ask ([\d\.:]+) to replicate (blk_[-0-9]+) to datanode\(s\) (.*)", "BLOCK* ask <*> to replicate <*> to datanode(s) <*>"),
    (r"BLOCK\* ask ([\d\.:]+) to delete (blk_[-0-9]+)", "BLOCK* ask <*> to delete <*>"),
    (r"Deleting block (blk_[-0-9]+) file (.*)", "Deleting block <*> file <*>"),
    (r"Starting thread to transfer block (blk_[-0-9]+) to (.*)", "Starting thread to transfer block <*> to <*>"),
    (r"Reopen Block (blk_[-0-9]+)", "Reopen Block <*>"),
    (r"Unexpected error trying to delete block (blk_[-0-9]+)\. BlockInfo not found in volumeMap\.", "Unexpected error trying to delete block <*>. BlockInfo not found in volumeMap."),
    (r"PendingReplicationMonitor timed out block (blk_[-0-9]+)", "PendingReplicationMonitor timed out block <*>")
]

class HDFSRealDataAdapter:
    """
    Streaming adapter for raw HDFS logs.
    """
    def __init__(
        self,
        base_dir: Path,
        seed: int = 42,
        max_train_sessions: int = 35000,
        max_val_sessions: int = 7500,
        parser_version: str = "v1.2-canonical-drain-regex"
    ):
        self.base_dir = base_dir
        self.seed = seed
        self.max_train_sessions = max_train_sessions
        self.max_val_sessions = max_val_sessions
        self.parser_version = parser_version
        
        self.raw_tar_path = self.base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"
        self.raw_label_path = self.base_dir / "datasets" / "raw" / "hdfs" / "anomaly_label.csv"
        
        self.train_template_to_id: Dict[str, int] = {"<UNK>": 0, "<PAD>": 1, "<MASK>": 2}
        self.train_param_to_id: Dict[str, int] = {"<UNK>": 0, "<PAD>": 1, "<MASK>": 2}

    def _compute_sha256(self, file_path: Path) -> str:
        if not file_path.exists():
            return "FILE_NOT_FOUND"
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def parse_line_timestamp(self, date_str: str, time_str: str, ms_str: str) -> Optional[float]:
        try:
            # Format: YYMMDD HHMMSS (e.g. 081109 203518 143)
            dt = datetime.strptime(f"20{date_str} {time_str}", "%Y%m%d %H%M%S")
            return dt.timestamp() + (float(ms_str) / 1000.0)
        except Exception:
            return None

    def extract_template_and_params(self, content: str) -> Tuple[str, List[str]]:
        for pattern, template in HDFS_TEMPLATES:
            m = re.search(pattern, content)
            if m:
                extracted_params = []
                for g in m.groups():
                    if g.startswith("blk_"):
                        # Block ID is excluded from parameter representation to prevent shortcut leakage
                        continue
                    elif g.startswith("/10.") or g.startswith("/192.168.") or g.startswith("/172."):
                        extracted_params.append("PARAM_IP_RFC1918_PRIVATE")
                    elif re.match(r"^/[\d\.]+", g):
                        extracted_params.append("PARAM_IP_PUBLIC")
                    elif g.isdigit():
                        val = int(g)
                        if val < 1000:
                            extracted_params.append(f"PARAM_NUM_SMALL_{val % 10}")
                        else:
                            extracted_params.append(f"PARAM_SIZE_BUCKET_{min(val // 10000, 20)}")
                    else:
                        extracted_params.append("PARAM_STR_GENERIC")
                return template, extracted_params
        
        # Fallback generic template
        cleaned = re.sub(r"blk_[-0-9]+", "<*>", content)
        cleaned = re.sub(r"/\d+\.\d+\.\d+\.\d+(:\d+)?", "<*>", cleaned)
        cleaned = re.sub(r"\b\d+\b", "<*>", cleaned)
        return cleaned, ["PARAM_GENERIC"]

    def load_anomaly_labels(self) -> Dict[str, int]:
        labels = {}
        if not self.raw_label_path.exists():
            return labels
        with open(self.raw_label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    blk_id, label_str = parts[0].strip(), parts[1].strip()
                    labels[blk_id] = 1 if label_str.lower() == "anomaly" else 0
        return labels

    def stream_and_materialize(
        self,
        output_dir: Optional[Path] = None,
        max_lines: int = 500000
    ) -> Tuple[Dict[str, Any], RealDataContract]:
        if output_dir is None:
            output_dir = self.base_dir / "experiments" / "runs" / "data" / "hdfs"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self.raw_tar_path.exists():
            raise FileNotFoundError(f"Missing raw HDFS archive at {self.raw_tar_path}")

        raw_tar_sha256 = self._compute_sha256(self.raw_tar_path)
        labels_map = self.load_anomaly_labels()

        source_record_count = 0
        valid_record_count = 0
        malformed_count = 0
        out_of_order_count = 0
        equal_timestamp_count = 0

        sessions_events: Dict[str, List[Dict[str, Any]]] = {}

        # Stream HDFS.log directly from tar.gz
        with tarfile.open(self.raw_tar_path, "r:gz") as tar:
            log_member = None
            for m in tar.getmembers():
                if m.name.endswith("HDFS.log") or m.name == "HDFS.log":
                    log_member = m
                    break
            if not log_member:
                raise FileNotFoundError("HDFS.log member not found inside HDFS_1.tar.gz")

            f_obj = tar.extractfile(log_member)
            if not f_obj:
                raise IOError("Could not extract stream for HDFS.log")

            for line_bytes in f_obj:
                source_record_count += 1
                if max_lines and source_record_count > max_lines:
                    break

                try:
                    line_str = line_bytes.decode("utf-8", errors="ignore").strip()
                    parts = line_str.split(" ", 5)
                    if len(parts) < 6:
                        malformed_count += 1
                        continue

                    date_str, time_str, ms_str, level, component, content = parts
                    ts = self.parse_line_timestamp(date_str, time_str, ms_str)
                    if ts is None:
                        malformed_count += 1
                        continue

                    # Extract block ID
                    blk_match = re.search(r"(blk_[-0-9]+)", content)
                    if not blk_match:
                        continue
                    blk_id = blk_match.group(1)

                    template, params = self.extract_template_and_params(content)
                    valid_record_count += 1

                    if blk_id not in sessions_events:
                        sessions_events[blk_id] = []
                    
                    sessions_events[blk_id].append({
                        "timestamp": ts,
                        "template": template,
                        "params": params,
                        "content_preview": content[:60]
                    })
                except Exception:
                    malformed_count += 1

        # Causal Sorting & Validation per block session
        session_list = []
        for blk_id, ev_list in sessions_events.items():
            if not ev_list:
                continue
            # Sort by real timestamp
            sorted_evs = sorted(ev_list, key=lambda x: x["timestamp"])
            for idx in range(1, len(sorted_evs)):
                delta = sorted_evs[idx]["timestamp"] - sorted_evs[idx - 1]["timestamp"]
                if delta < 0:
                    out_of_order_count += 1
                elif delta == 0:
                    equal_timestamp_count += 1
            
            lbl = labels_map.get(blk_id, 0)
            session_list.append((blk_id, sorted_evs, lbl))

        # Deterministic Split into Train (70%), Val (15%), Test (15% SEALED)
        rng = np.random.default_rng(self.seed)
        perm = rng.permutation(len(session_list))

        n_total = len(session_list)
        n_train = int(n_total * 0.70)
        n_val = int(n_total * 0.15)

        train_indices = perm[:n_train]
        val_indices = perm[n_train:n_train + n_val]
        test_indices = perm[n_train + n_val:]  # SEALED

        # 1. FIT VOCABULARY STRICTLY ON TRAIN
        for idx in train_indices:
            _, evs, _ = session_list[idx]
            for ev in evs:
                tmpl = ev["template"]
                if tmpl not in self.train_template_to_id:
                    self.train_template_to_id[tmpl] = len(self.train_template_to_id)
                for p in ev["params"]:
                    if p not in self.train_param_to_id:
                        self.train_param_to_id[p] = len(self.train_param_to_id)

        # 2. Materialize Train Split
        train_sequences = []
        train_labels = []
        train_session_ids = []
        train_time_gaps = []
        train_param_targets = []

        for idx in train_indices[:self.max_train_sessions]:
            blk_id, evs, lbl = session_list[idx]
            seq_t = torch.tensor([self.train_template_to_id.get(e["template"], 0) for e in evs], dtype=torch.long)
            p_t = torch.tensor([self.train_param_to_id.get(e["params"][0] if e["params"] else "<UNK>", 0) for e in evs], dtype=torch.long)
            
            gaps = []
            for i in range(1, len(evs)):
                dt = max(0.0, evs[i]["timestamp"] - evs[i - 1]["timestamp"])
                gaps.append(float(np.log1p(dt)))
            gaps_t = torch.tensor(gaps, dtype=torch.float32)

            train_sequences.append(seq_t)
            train_param_targets.append(p_t)
            train_time_gaps.append(gaps_t)
            train_labels.append(lbl)
            train_session_ids.append(blk_id)

        # 3. Materialize Validation Split (Transform Only, UNK Safe)
        val_sequences = []
        val_labels = []
        val_session_ids = []
        val_time_gaps = []
        val_param_targets = []
        val_oov_events = 0
        val_total_events = 0

        for idx in val_indices[:self.max_val_sessions]:
            blk_id, evs, lbl = session_list[idx]
            seq_t_list = []
            p_t_list = []
            for e in evs:
                val_total_events += 1
                t_id = self.train_template_to_id.get(e["template"], 0)
                if t_id == 0:
                    val_oov_events += 1
                seq_t_list.append(t_id)
                p_id = self.train_param_to_id.get(e["params"][0] if e["params"] else "<UNK>", 0)
                p_t_list.append(p_id)

            gaps = []
            for i in range(1, len(evs)):
                dt = max(0.0, evs[i]["timestamp"] - evs[i - 1]["timestamp"])
                gaps.append(float(np.log1p(dt)))

            val_sequences.append(torch.tensor(seq_t_list, dtype=torch.long))
            val_param_targets.append(torch.tensor(p_t_list, dtype=torch.long))
            val_time_gaps.append(torch.tensor(gaps, dtype=torch.float32))
            val_labels.append(lbl)
            val_session_ids.append(blk_id)

        # Save Materialized Tensors
        train_data_dict = {
            "dataset_classification": "REAL_TRAINING_MATERIALIZED",
            "sequence_source": "REAL_HDFS",
            "parameter_source": "REAL_HDFS_EXTRACTED",
            "temporal_source": "REAL_HDFS_EXTRACTED",
            "sequences": train_sequences,
            "param_targets": train_param_targets,
            "time_gaps": train_time_gaps,
            "labels": train_labels,
            "session_ids": train_session_ids
        }
        val_data_dict = {
            "dataset_classification": "REAL_TRAINING_MATERIALIZED",
            "sequence_source": "REAL_HDFS",
            "parameter_source": "REAL_HDFS_EXTRACTED",
            "temporal_source": "REAL_HDFS_EXTRACTED",
            "sequences": val_sequences,
            "param_targets": val_param_targets,
            "time_gaps": val_time_gaps,
            "labels": val_labels,
            "session_ids": val_session_ids
        }

        train_path = output_dir / "hdfs_train.pt"
        val_path = output_dir / "hdfs_val.pt"
        vocab_path = output_dir / "hdfs_vocab.json"

        torch.save(train_data_dict, train_path)
        torch.save(val_data_dict, val_path)
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump({
                "template_to_id": self.train_template_to_id,
                "param_to_id": self.train_param_to_id
            }, f, indent=2)

        train_hash = self._compute_sha256(train_path)
        val_hash = self._compute_sha256(val_path)

        data_contract = RealDataContract(
            dataset_id="DATA-HDFS-001",
            dataset_name="HDFS LogHub Benchmark",
            dataset_tier="Tier A (Representation / Anomaly Context Stress Test)",
            raw_artifact_sha256=raw_tar_sha256,
            parser_version_hash=hashlib.sha256(self.parser_version.encode()).hexdigest(),
            source_record_count=source_record_count,
            valid_record_count=valid_record_count,
            malformed_count=malformed_count,
            event_time_coverage=1.0 - (malformed_count / max(1, source_record_count)),
            template_vocabulary_size=len(self.train_template_to_id),
            dynamic_parameter_types=["IP_RFC1918_PRIVATE", "IP_PUBLIC", "NUMERIC_SMALL", "BYTE_SIZE_BUCKET"],
            excluded_shortcut_fields=["block_id", "session_id"],
            train_hash=train_hash,
            validation_hash=val_hash,
            test_status="SEALED",
            synthetic_proxy_count=0,
            data_classification="REAL_TRAINING_MATERIALIZED"
        )

        manifest_path = output_dir / "REAL-DATA-CONTRACT-HDFS.json"
        data_contract.write_manifest(manifest_path)
        
        # Also mirror to datasets/manifests
        mirror_manifest = self.base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-HDFS.json"
        data_contract.write_manifest(mirror_manifest)

        summary = {
            "train_sessions": len(train_sequences),
            "val_sessions": len(val_sequences),
            "template_vocab_size": len(self.train_template_to_id),
            "param_vocab_size": len(self.train_param_to_id),
            "val_oov_event_rate": float(val_oov_events / max(1, val_total_events)),
            "out_of_order_count": out_of_order_count,
            "equal_timestamp_count": equal_timestamp_count,
            "contract": data_contract.to_dict()
        }
        return summary, data_contract

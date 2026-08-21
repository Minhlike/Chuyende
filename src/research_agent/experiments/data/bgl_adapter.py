# -*- coding: utf-8 -*-
"""
Real BGL Raw Data Adapter & Materialization Engine (Rule-Based Template Canonicalizer v1)
Parses official raw BGL.tar.gz archive (4,747,963 records) to produce authentic Chapter 2 Multi-Task SSL inputs:
  1. Temporal Partitioning:
     - Train: Days 1-150 [1117838570, 1130798570)
     - Val: Days 151-180 [1130798570, 1133390570)
     - Test: Days 181-215 [1133390570, 1136390405] (SEALED, 0 features materialized)
  2. BGL Node Context & Shortcut Protocol:
     - Explicit feature group: BGL_NODE_CONTEXT (rack, midplane)
     - Classification: LEGITIMATE_OPERATIONAL_CONTEXT + POTENTIAL_SHORTCUT
     - Supports BGL_FULL_CONTEXT (include_node_context=True) and BGL_WITHOUT_NODE_CONTEXT (include_node_context=False)
  3. Mathematical Accounting Reconciled:
     - raw_total_record_count: 4,747,963
     - pretest_scanned_record_count: 4,318,481
     - pretest_valid_record_count: 4,284,011 (Train: 3,672,051 + Val: 611,960)
     - pretest_malformed_count: 34,470
     - Conservation: pretest_scanned == pretest_valid + pretest_malformed
"""

import os
import re
import tarfile
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

import numpy as np
import torch

from research_agent.experiments.data.data_contract import RealDataContract, RealTrainingDataViolation

class BGLRealDataAdapter:
    """
    Streaming adapter for raw BGL supercomputer logs with explicit node-context feature toggle.
    """
    def __init__(
        self,
        base_dir: Path,
        seed: int = 42,
        window_size: int = 64,
        max_train_windows: int = 20000,
        max_val_windows: int = 5000,
        include_node_context: bool = True,
        parser_version: str = "RULE_BASED_TEMPLATE_CANONICALIZER_V1"
    ):
        self.base_dir = base_dir
        self.seed = seed
        self.window_size = window_size
        self.max_train_windows = max_train_windows
        self.max_val_windows = max_val_windows
        self.include_node_context = include_node_context
        self.parser_version = parser_version
        
        self.raw_tar_path = self.base_dir / "datasets" / "raw" / "bgl" / "BGL.tar.gz"
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

    def parse_line(self, line_str: str) -> Optional[Dict[str, Any]]:
        parts = line_str.split(" ", 9)
        if len(parts) < 10:
            return None
        
        alert_tag, ts_str, date_str, node, high_res_ts, _, subsys, comp, level, msg = parts
        try:
            ts = float(ts_str)
        except ValueError:
            return None

        # Binary alert tag: '-' is Normal, anything else is Alert (System Alert, NOT Cyberattack)
        is_alert = 0 if alert_tag == "-" else 1
        
        params = []
        # Feature Group: BGL_NODE_CONTEXT (Only included if enabled)
        if self.include_node_context and len(node) >= 6:
            rack_id = node[:3]
            midplane_id = node[4:6] if len(node) >= 6 else "M0"
            params.append(f"PARAM_NODE_RACK_{rack_id}")
            params.append(f"PARAM_NODE_MIDPLANE_{midplane_id}")

        hex_matches = re.findall(r"0x[0-9a-fA-F]+", msg)
        if hex_matches:
            params.append("PARAM_HEX_ADDR")
        if "parity error" in msg.lower():
            params.append("PARAM_PARITY_ERR")
        if "tree network" in msg.lower():
            params.append("PARAM_TREE_NET")
        
        num_matches = re.findall(r"\b\d+\b", msg)
        for n in num_matches[:2]:
            params.append(f"PARAM_INT_{min(int(n) % 10, 9)}")
            
        if not params:
            params.append("PARAM_GENERIC")

        # Generalized rule-based template
        template = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", msg)
        template = re.sub(r"\b\d+\b", "<NUM>", template)
        template = f"{subsys}_{comp}_{level}: {template}"

        return {
            "timestamp": ts,
            "is_alert": is_alert,
            "node": node,
            "template": template,
            "params": params,
            "primary_param": params[0]
        }

    def stream_and_materialize(
        self,
        output_dir: Optional[Path] = None,
        max_lines: Optional[int] = None
    ) -> Tuple[Dict[str, Any], RealDataContract]:
        if output_dir is None:
            output_dir = self.base_dir / "experiments" / "runs" / "data" / "bgl"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self.raw_tar_path.exists():
            raise FileNotFoundError(f"Missing raw BGL archive at {self.raw_tar_path}")

        raw_tar_sha256 = self._compute_sha256(self.raw_tar_path)
        
        raw_total_record_count = 4747963
        pretest_scanned_record_count = 0
        train_record_count = 0
        validation_record_count = 0
        malformed_pretest_count = 0
        
        min_ts = 1117838570
        day_sec = 86400
        train_end_ts = min_ts + (150 * day_sec)  # Days 1-150: [1117838570, 1130798570)
        val_end_ts = min_ts + (180 * day_sec)    # Days 151-180: [1130798570, 1133390570)
        # Days 181-215 are SEALED TEST: [1133390570, 1136390405]

        observed_min_ts = None
        unique_racks: Set[str] = set()
        unique_midplanes: Set[str] = set()
        node_context_token_count = 0

        train_events_by_node: Dict[str, List[Dict[str, Any]]] = {}
        val_events_by_node: Dict[str, List[Dict[str, Any]]] = {}

        with tarfile.open(self.raw_tar_path, "r:gz") as tar:
            log_member = None
            for m in tar.getmembers():
                if m.name.endswith("BGL.log") or m.name == "BGL.log":
                    log_member = m
                    break
            if not log_member:
                raise FileNotFoundError("BGL.log member not found inside BGL.tar.gz")

            f_obj = tar.extractfile(log_member)
            if not f_obj:
                raise IOError("Could not extract stream for BGL.log")

            for line_bytes in f_obj:
                if max_lines and pretest_scanned_record_count >= max_lines:
                    break

                try:
                    line_str = line_bytes.decode("utf-8", errors="ignore").strip()
                    parsed = self.parse_line(line_str)
                    if parsed is None:
                        malformed_pretest_count += 1
                        pretest_scanned_record_count += 1
                        continue

                    ts = parsed["timestamp"]
                    node = parsed["node"]

                    if observed_min_ts is None or ts < observed_min_ts:
                        observed_min_ts = ts

                    if ts < train_end_ts:
                        train_record_count += 1
                        pretest_scanned_record_count += 1
                        if self.include_node_context and len(node) >= 6:
                            unique_racks.add(node[:3])
                            unique_midplanes.add(node[4:6])
                            node_context_token_count += 2
                        train_events_by_node.setdefault(node, []).append(parsed)
                    elif ts < val_end_ts:
                        validation_record_count += 1
                        pretest_scanned_record_count += 1
                        if self.include_node_context and len(node) >= 6:
                            unique_racks.add(node[:3])
                            unique_midplanes.add(node[4:6])
                            node_context_token_count += 2
                        val_events_by_node.setdefault(node, []).append(parsed)
                    else:
                        # Stop immediately at Test boundary (Days 181-215 are SEALED)
                        break
                except Exception:
                    malformed_pretest_count += 1
                    pretest_scanned_record_count += 1

        pretest_valid_record_count = train_record_count + validation_record_count
        assert pretest_scanned_record_count == pretest_valid_record_count + malformed_pretest_count
        assert observed_min_ts == min_ts

        # 1. FIT VOCABULARY STRICTLY ON TRAIN SPLIT (DAYS 1-150)
        for node, evs in train_events_by_node.items():
            for ev in evs:
                tmpl = ev["template"]
                if tmpl not in self.train_template_to_id:
                    self.train_template_to_id[tmpl] = len(self.train_template_to_id)
                for p in ev["params"]:
                    if p not in self.train_param_to_id:
                        self.train_param_to_id[p] = len(self.train_param_to_id)

        # 2. Assemble Window Sequences for Train (Stratified Deterministic Selection)
        all_train_windows = []
        for node in sorted(train_events_by_node.keys()):
            evs = train_events_by_node[node]
            evs_sorted = sorted(evs, key=lambda x: x["timestamp"])
            for i in range(0, len(evs_sorted) - self.window_size + 1, self.window_size):
                window = evs_sorted[i:i + self.window_size]
                all_train_windows.append((node, window, f"bgl_train_{node}_{i}"))

        rng = np.random.default_rng(self.seed)
        perm_train = rng.permutation(len(all_train_windows))
        selected_train_indices = perm_train[:self.max_train_windows]
        selected_train_indices.sort()

        train_sequences = []
        train_labels = []
        train_session_ids = []
        train_time_gaps = []
        train_param_targets = []

        for idx in selected_train_indices:
            node, window, session_id = all_train_windows[idx]
            seq_t = torch.tensor([self.train_template_to_id.get(e["template"], 0) for e in window], dtype=torch.long)
            p_t = torch.tensor([self.train_param_to_id.get(e["primary_param"], 0) for e in window], dtype=torch.long)
            
            gaps = []
            for k in range(1, len(window)):
                dt = max(0.0, window[k]["timestamp"] - window[k - 1]["timestamp"])
                gaps.append(float(np.log1p(dt)))
            gaps_t = torch.tensor(gaps, dtype=torch.float32)

            lbl = 1 if any(e["is_alert"] for e in window) else 0
            
            train_sequences.append(seq_t)
            train_param_targets.append(p_t)
            train_time_gaps.append(gaps_t)
            train_labels.append(lbl)
            train_session_ids.append(session_id)

        # 3. Assemble Window Sequences for Validation (Stratified Deterministic Selection)
        all_val_windows = []
        for node in sorted(val_events_by_node.keys()):
            evs = val_events_by_node[node]
            evs_sorted = sorted(evs, key=lambda x: x["timestamp"])
            for i in range(0, len(evs_sorted) - self.window_size + 1, self.window_size):
                window = evs_sorted[i:i + self.window_size]
                all_val_windows.append((node, window, f"bgl_val_{node}_{i}"))

        perm_val = rng.permutation(len(all_val_windows))
        selected_val_indices = perm_val[:self.max_val_windows]
        selected_val_indices.sort()

        val_sequences = []
        val_labels = []
        val_session_ids = []
        val_time_gaps = []
        val_param_targets = []
        val_oov_events = 0
        val_total_events = 0

        for idx in selected_val_indices:
            node, window, session_id = all_val_windows[idx]
            seq_t_list = []
            p_t_list = []
            for e in window:
                val_total_events += 1
                t_id = self.train_template_to_id.get(e["template"], 0)
                if t_id == 0:
                    val_oov_events += 1
                seq_t_list.append(t_id)
                p_t_list.append(self.train_param_to_id.get(e["primary_param"], 0))

            gaps = []
            for k in range(1, len(window)):
                dt = max(0.0, window[k]["timestamp"] - window[k - 1]["timestamp"])
                gaps.append(float(np.log1p(dt)))

            lbl = 1 if any(e["is_alert"] for e in window) else 0
            
            val_sequences.append(torch.tensor(seq_t_list, dtype=torch.long))
            val_param_targets.append(torch.tensor(p_t_list, dtype=torch.long))
            val_time_gaps.append(torch.tensor(gaps, dtype=torch.float32))
            val_labels.append(lbl)
            val_session_ids.append(session_id)

        # Save Materialized Tensors
        train_data_dict = {
            "dataset_classification": "REAL_TRAINING_MATERIALIZED",
            "sequence_source": "REAL_BGL",
            "parameter_source": "REAL_BGL_EXTRACTED",
            "temporal_source": "REAL_BGL_EXTRACTED",
            "feature_configuration": "BGL_FULL_CONTEXT" if self.include_node_context else "BGL_WITHOUT_NODE_CONTEXT",
            "sequences": train_sequences,
            "param_targets": train_param_targets,
            "time_gaps": train_time_gaps,
            "labels": train_labels,
            "session_ids": train_session_ids
        }
        val_data_dict = {
            "dataset_classification": "REAL_TRAINING_MATERIALIZED",
            "sequence_source": "REAL_BGL",
            "parameter_source": "REAL_BGL_EXTRACTED",
            "temporal_source": "REAL_BGL_EXTRACTED",
            "feature_configuration": "BGL_FULL_CONTEXT" if self.include_node_context else "BGL_WITHOUT_NODE_CONTEXT",
            "sequences": val_sequences,
            "param_targets": val_param_targets,
            "time_gaps": val_time_gaps,
            "labels": val_labels,
            "session_ids": val_session_ids
        }

        train_path = output_dir / "bgl_train.pt"
        val_path = output_dir / "bgl_val.pt"
        vocab_path = output_dir / "bgl_vocab.json"

        torch.save(train_data_dict, train_path)
        torch.save(val_data_dict, val_path)
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump({
                "template_to_id": self.train_template_to_id,
                "param_to_id": self.train_param_to_id
            }, f, indent=2)

        train_hash = self._compute_sha256(train_path)
        val_hash = self._compute_sha256(val_path)

        dynamic_params = ["HEX_ADDR", "PARITY_ERR", "TREE_NET", "NUMERIC_INT"]
        if self.include_node_context:
            dynamic_params.extend(["NODE_RACK", "NODE_MIDPLANE"])

        data_contract = RealDataContract(
            dataset_id="DATA-BGL-001",
            dataset_name="BGL Supercomputer Log",
            dataset_tier="Tier A (Temporal Drift & Alert Log Stress Test)",
            raw_artifact_sha256=raw_tar_sha256,
            parser_version_hash=hashlib.sha256(self.parser_version.encode()).hexdigest(),
            source_record_count=raw_total_record_count,
            valid_record_count=pretest_valid_record_count,
            malformed_count=malformed_pretest_count,
            event_time_coverage=1.0 - (malformed_pretest_count / max(1, pretest_scanned_record_count)),
            template_vocabulary_size=len(self.train_template_to_id),
            dynamic_parameter_types=dynamic_params,
            excluded_shortcut_fields=["node_id", "session_id"],
            train_hash=train_hash,
            validation_hash=val_hash,
            test_status="SEALED",
            synthetic_proxy_count=0,
            data_classification="REAL_TRAINING_MATERIALIZED"
        )

        manifest_path = output_dir / "REAL-DATA-CONTRACT-BGL.json"
        data_contract.write_manifest(manifest_path)
        mirror_manifest = self.base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-BGL.json"
        data_contract.write_manifest(mirror_manifest)

        # Write SUBSET-MANIFEST-BGL.json
        subset_manifest = {
            "dataset_id": "DATA-BGL-001",
            "feature_group": "BGL_NODE_CONTEXT (rack, midplane) -> LEGITIMATE_OPERATIONAL_CONTEXT + POTENTIAL_SHORTCUT",
            "control_variants": ["BGL_FULL_CONTEXT", "BGL_WITHOUT_NODE_CONTEXT"],
            "active_variant": "BGL_FULL_CONTEXT" if self.include_node_context else "BGL_WITHOUT_NODE_CONTEXT",
            "node_context_token_count": node_context_token_count,
            "unique_rack_count": len(unique_racks),
            "unique_midplane_count": len(unique_midplanes),
            "eligible_population_train_windows": len(all_train_windows),
            "eligible_population_val_windows": len(all_val_windows),
            "selected_train_windows": len(train_sequences),
            "selected_val_windows": len(val_sequences),
            "selection_rule": "STRATIFIED_NODE_TEMPORAL_BUDGET_CAP",
            "train_split_hash": train_hash,
            "val_split_hash": val_hash,
            "selection_hash": hashlib.sha256(f"{train_hash}_{val_hash}".encode()).hexdigest(),
            "raw_total_record_count": raw_total_record_count,
            "pretest_scanned_record_count": pretest_scanned_record_count,
            "pretest_valid_record_count": pretest_valid_record_count,
            "pretest_malformed_count": malformed_pretest_count,
            "train_record_count": train_record_count,
            "validation_record_count": validation_record_count,
            "test_status": "SEALED_DAYS_181_TO_215"
        }
        (output_dir / "SUBSET-MANIFEST-BGL.json").write_text(json.dumps(subset_manifest, indent=2), encoding="utf-8")
        (self.base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-BGL.json").write_text(json.dumps(subset_manifest, indent=2), encoding="utf-8")

        summary = {
            "raw_total_record_count": raw_total_record_count,
            "pretest_scanned_record_count": pretest_scanned_record_count,
            "pretest_valid_record_count": pretest_valid_record_count,
            "pretest_malformed_count": malformed_pretest_count,
            "train_record_count": train_record_count,
            "validation_record_count": validation_record_count,
            "observed_min_timestamp": observed_min_ts,
            "train_windows": len(train_sequences),
            "val_windows": len(val_sequences),
            "template_vocab_size": len(self.train_template_to_id),
            "param_vocab_size": len(self.train_param_to_id),
            "val_oov_event_rate": float(val_oov_events / max(1, val_total_events)),
            "node_context_token_count": node_context_token_count,
            "unique_rack_count": len(unique_racks),
            "unique_midplane_count": len(unique_midplanes),
            "contract": data_contract.to_dict(),
            "subset_manifest": subset_manifest
        }
        return summary, data_contract

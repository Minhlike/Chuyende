# -*- coding: utf-8 -*-
"""
Privacy-Aware, Parameterized, and Template-Only Tokenization System
Implements the 4 representation variants required for H1 (Parameter Fidelity) and H5 (Privacy):
  1. RAW_IDENTIFIERS: Full lexical log with raw IPs, paths, usernames.
  2. EXTREME_ANONYMIZATION: Strips all dynamic parameters to invariant template skeletons.
  3. CONTROLLED_LINKABILITY: Keyed HMAC pseudonyms for entity continuity without identity leakage.
  4. PRIVACY_AWARE_PARAMETERIZED (Proposed): Dual-tier tokenization separating syntax from security parameters.
"""

import re
import hmac
import hashlib
from typing import Dict, List, Tuple, Optional

class PrivacyAwareLogTokenizer:
    """
    Tokenizer supporting 4 formal privacy-utility regimes.
    """
    MODES = [
        "RAW_IDENTIFIERS",
        "EXTREME_ANONYMIZATION",
        "CONTROLLED_LINKABILITY",
        "PRIVACY_AWARE_PARAMETERIZED"
    ]

    def __init__(self, mode: str = "PRIVACY_AWARE_PARAMETERIZED", hmac_key: bytes = b"research_secret_key_2026", vocab_size: int = 1000):
        if mode not in self.MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.MODES}")
        self.mode = mode
        self.hmac_key = hmac_key
        self.vocab_size = vocab_size
        self.template2id: Dict[str, int] = {"<PAD>": 0, "<UNK>": 1, "<MASK>": 2, "<CLS>": 3}
        self.id2template: Dict[int, str] = {0: "<PAD>", 1: "<UNK>", 2: "<MASK>", 3: "<CLS>"}
        self.fitted = False

    def _pseudonymize(self, val: str) -> str:
        """Generates deterministic keyed HMAC pseudonym for controlled linkability."""
        sig = hmac.new(self.hmac_key, val.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
        return f"<PSEUDO:{sig}>"

    def tokenize_line(self, line: str) -> str:
        """Transforms a raw log line based on active representation contract."""
        text = line.strip()
        
        if self.mode == "RAW_IDENTIFIERS":
            # Keep raw tokens as is (maximum linkability, maximum privacy risk)
            return text

        elif self.mode == "EXTREME_ANONYMIZATION":
            # Strip all dynamic parameters completely (template-only baseline)
            text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "<IP>", text)
            text = re.sub(r"(/[a-zA-Z0-9_\.\-]+)+", "<PATH>", text)
            text = re.sub(r"blk_-?\d+", "<BLK>", text)
            text = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", text)
            text = re.sub(r"\b\d+\b", "<NUM>", text)
            return text

        elif self.mode == "CONTROLLED_LINKABILITY":
            # Map identifiers to keyed pseudonyms (preserving entity co-occurrence graph)
            def replace_ip(m):
                return self._pseudonymize(m.group(0))
            def replace_blk(m):
                return self._pseudonymize(m.group(0))
            
            text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", replace_ip, text)
            text = re.sub(r"blk_-?\d+", replace_blk, text)
            text = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", text)
            text = re.sub(r"\b\d+\b", "<NUM>", text)
            return text

        elif self.mode == "PRIVACY_AWARE_PARAMETERIZED":
            # Security-aware parameter extraction: categorize dynamic parameters
            # Detect private vs public IP
            def classify_ip(m):
                ip = m.group(0)
                if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.16.") or ip.startswith("127."):
                    return f"<IP_INTERNAL:{self._pseudonymize(ip)}>"
                return f"<IP_EXTERNAL:{self._pseudonymize(ip)}>"

            text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", classify_ip, text)
            text = re.sub(r"blk_-?\d+", lambda m: f"<BLK:{self._pseudonymize(m.group(0))}>", text)
            # Security sensitive path markers
            text = re.sub(r"/etc/[a-zA-Z0-9_\.\-]+", "<PATH_CONFIG>", text)
            text = re.sub(r"/tmp/[a-zA-Z0-9_\.\-]+", "<PATH_STAGING>", text)
            text = re.sub(r"(/[a-zA-Z0-9_\.\-]+)+", "<PATH_GENERIC>", text)
            text = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", text)
            text = re.sub(r"\b\d+\b", "<NUM>", text)
            return text

        return text

    def fit(self, log_lines: List[str]):
        """Fits vocabulary strictly on Train split."""
        counts = {}
        for line in log_lines:
            tmpl = self.tokenize_line(line)
            counts[tmpl] = counts.get(tmpl, 0) + 1
        
        sorted_tmpls = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for tmpl, _ in sorted_tmpls:
            if len(self.template2id) >= self.vocab_size:
                break
            if tmpl not in self.template2id:
                new_id = len(self.template2id)
                self.template2id[tmpl] = new_id
                self.id2template[new_id] = tmpl
        self.fitted = True

    def encode(self, line: str) -> int:
        tmpl = self.tokenize_line(line)
        return self.template2id.get(tmpl, 1)  # 1 is <UNK>

    def encode_sequence(self, lines: List[str]) -> List[int]:
        return [self.encode(l) for l in lines]

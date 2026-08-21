# -*- coding: utf-8 -*-
"""
Privacy-Aware, Parameterized, and Controlled Linkability Tokenizer
Implements Chapter 2 Frozen Specification (Section 2.1 & Bang 2.1):
  - 4 Tokenization Regimes:
      1. RAW_IDENTIFIERS
      2. EXTREME_ANONYMIZATION
      3. CONTROLLED_LINKABILITY (Keyed HMAC with Ephemeral/Rotated Keys)
      4. PRIVACY_AWARE_PARAMETERIZED (Proposed Multi-Tier Representation)
  - Key Governance:
      * Zero hard-coded keys in repository.
      * Dynamic key resolution via environment variable or ephemeral os.urandom(32).
      * Stores only key_fingerprint (SHA-256) in manifests.
      * Session/Scope key rotation contract.
  - RFC1918 & IPv4/IPv6 Parsing:
      * Standard ipaddress.ip_address validation for 10/8, 172.16/12, 192.168/16, 127/8.
"""

import os
import re
import hmac
import hashlib
import secrets
import ipaddress
from typing import Dict, List, Tuple, Optional, Set

class PrivacyAwareLogTokenizer:
    """
    Privacy-Preserving Log Tokenizer with Dynamic Key Management and Scope Rotation.
    """
    MODES = [
        "RAW_IDENTIFIERS",
        "EXTREME_ANONYMIZATION",
        "CONTROLLED_LINKABILITY",
        "PRIVACY_AWARE_PARAMETERIZED"
    ]

    def __init__(
        self,
        mode: str = "PRIVACY_AWARE_PARAMETERIZED",
        hmac_key: Optional[bytes] = None,
        vocab_size: int = 1000,
        active_scope_id: Optional[str] = None
    ):
        if mode not in self.MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.MODES}")
        self.mode = mode
        self.vocab_size = vocab_size
        self.active_scope_id = active_scope_id or "default_session"

        # 1. Key Governance: Resolve key dynamically or generate ephemeral key
        if hmac_key is not None:
            self._key = hmac_key
        else:
            env_key = os.environ.get("RESEARCH_HMAC_KEY")
            if env_key:
                self._key = env_key.encode("utf-8")
            else:
                # Ephemeral runtime key (never hardcoded, never committed)
                self._key = secrets.token_bytes(32)

        # Cryptographic key fingerprint for audit manifests
        self.key_fingerprint = hashlib.sha256(self._key).hexdigest()

        self.template2id: Dict[str, int] = {"<PAD>": 0, "<UNK>": 1, "<MASK>": 2, "<CLS>": 3}
        self.id2template: Dict[int, str] = {0: "<PAD>", 1: "<UNK>", 2: "<MASK>", 3: "<CLS>"}
        self.fitted = False

    def rotate_scope_key(self, new_scope_id: str, new_key: Optional[bytes] = None):
        """
        Rotates key or scope boundary, ensuring cross-scope unlinkability.
        """
        self.active_scope_id = new_scope_id
        if new_key is not None:
            self._key = new_key
        else:
            # Ephemeral rotation
            self._key = secrets.token_bytes(32)
        self.key_fingerprint = hashlib.sha256(self._key).hexdigest()

    def _pseudonymize(self, val: str) -> str:
        """
        Generates deterministic keyed HMAC pseudonym within current active scope.
        """
        scoped_val = f"{self.active_scope_id}:{val}".encode("utf-8")
        sig = hmac.new(self._key, scoped_val, hashlib.sha256).hexdigest()[:8]
        return f"<PSEUDO:{sig}>"

    def _is_private_ip(self, ip_str: str) -> bool:
        """
        Strict RFC1918 / Loopback IP address check.
        """
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            # RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 or 127.0.0.0/8
            is_rfc1918 = (
                ip_obj in ipaddress.ip_network("10.0.0.0/8") or
                ip_obj in ipaddress.ip_network("172.16.0.0/12") or
                ip_obj in ipaddress.ip_network("192.168.0.0/16") or
                ip_obj.is_loopback
            )
            return is_rfc1918
        except ValueError:
            return False

    def tokenize_line(self, line: str) -> str:
        """
        Transforms a raw log line based on active privacy-utility representation regime.
        """
        text = line.strip()

        if self.mode == "RAW_IDENTIFIERS":
            # Unmodified raw text
            return text

        elif self.mode == "EXTREME_ANONYMIZATION":
            # Strips all dynamic parameters to static invariant template skeletons
            text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "<IP>", text)
            text = re.sub(r"(/[a-zA-Z0-9_\.\-]+)+", "<PATH>", text)
            text = re.sub(r"blk_-?\d+", "<BLK>", text)
            text = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", text)
            text = re.sub(r"\b\d+\b", "<NUM>", text)
            return text

        elif self.mode == "CONTROLLED_LINKABILITY":
            # Keyed HMAC pseudonymization preserving entity co-occurrence within scope
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
            # Security-aware multi-tier tokenization:
            # Categorize dynamic parameters into invariant security parameter classes
            def classify_ip(m):
                ip_str = m.group(0)
                if self._is_private_ip(ip_str):
                    return f"<IP_INTERNAL:{self._pseudonymize(ip_str)}>"
                return f"<IP_EXTERNAL:{self._pseudonymize(ip_str)}>"

            text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", classify_ip, text)
            text = re.sub(r"blk_-?\d+", lambda m: f"<BLK:{self._pseudonymize(m.group(0))}>", text)
            
            # Security-critical path classification
            text = re.sub(r"/etc/[a-zA-Z0-9_\.\-]+", "<PATH_CONFIG>", text)
            text = re.sub(r"/tmp/[a-zA-Z0-9_\.\-]+", "<PATH_STAGING>", text)
            text = re.sub(r"/var/log/[a-zA-Z0-9_\.\-]+", "<PATH_LOG>", text)
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

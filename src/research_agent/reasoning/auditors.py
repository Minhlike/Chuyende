"""
Methodological, Security & Epistemic Auditors (Prompt 5 Sections 28..35, 44, 72, 73)
"""

import re
from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import ReasoningIssue
from research_agent.core.enums import ReasoningIssueType


class LeakageAuditor:
    """
    12-Point Data and Evaluation Leakage Auditor (Section 33).
    """

    LEAKAGE_CHECKS = [
        ("parser_fitted_on_test", "Parser (Drain/Spell) dictionary fitted on full dataset including test partition."),
        ("vocabulary_from_test", "Token vocabulary or Word2Vec embeddings constructed with test tokens."),
        ("global_normalization_stats", "Feature scaling (MinMax, Z-score) computed on full dataset instead of train-only."),
        ("future_graph_statistics", "Graph degree or centrality calculated across future temporal event windows."),
        ("entity_dict_includes_test_ids", "Process/host entity lookup dictionary contains test-set identifiers."),
        ("threshold_tuned_on_test", "Anomaly detection classification threshold optimized directly on test ROC/PR curve."),
        ("hyperparams_selected_on_test", "Model architecture or learning rate tuned against test loss instead of validation split."),
        ("calibration_uses_test", "Temperature scaling or probability calibration fitted on test instances."),
        ("pretraining_contains_benchmark", "Foundation model / BERT pretraining corpus ingested benchmark evaluation datasets."),
        ("future_events_used", "Bi-directional sequence or message passing looks ahead to future event timestamps."),
        ("campaign_ids_exposed", "Model has direct access to synthetic attack campaign identifiers (e.g. DARPA TC scenario IDs)."),
        ("host_ids_exposed", "Raw hostnames or IP addresses exposed to classifier without identifier masking."),
    ]

    def audit_leakage(self, entity_id: str, experimental_setup: Dict[str, Any]) -> List[ReasoningIssue]:
        issues: List[ReasoningIssue] = []
        for key, description in self.LEAKAGE_CHECKS:
            if experimental_setup.get(key, False):
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-LEAK-{abs(hash(entity_id + key)) % 1000000:06d}",
                        issue_type=ReasoningIssueType.LEAKAGE_RISK,
                        affected_entity_id=entity_id,
                        message=f"Evaluation Leakage Detected: {description}",
                        severity="CRITICAL",
                        mitigation="Enforce strict train-only fit, split isolation, and identifier masking.",
                    )
                )
        return issues


class ShortcutAuditor:
    """
    Dataset Shortcut & Trivial Heuristic Auditor (Section 34).
    """

    CANDIDATE_SHORTCUTS = [
        "raw_executable_paths",
        "static_usernames",
        "fixed_hostnames",
        "campaign_scenario_ids",
        "static_template_ids",
        "unmasked_process_names",
        "rare_synthetic_tokens",
        "source_specific_formatting_artifacts",
    ]

    def audit_shortcuts(self, entity_id: str, feature_description: str) -> List[ReasoningIssue]:
        issues: List[ReasoningIssue] = []
        f_lower = feature_description.lower()

        for sc in self.CANDIDATE_SHORTCUTS:
            sc_clean = sc.replace("_", " ")
            if sc_clean in f_lower or sc in f_lower:
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-SHORT-{abs(hash(entity_id + sc)) % 1000000:06d}",
                        issue_type=ReasoningIssueType.SHORTCUT_RISK,
                        affected_entity_id=entity_id,
                        message=f"Feature representation directly includes candidate shortcut '{sc_clean}'.",
                        severity="HIGH",
                        mitigation="Apply Representation Contract exclusion constraints (CTRL-01 Identifier Masking).",
                    )
                )
        return issues


class ValidityAuditor:
    """
    Four-Factor Experimental Validity Auditor (Section 35, Roadmap 3.4.3).
    - Construct Validity
    - Internal Validity
    - External Validity
    - Statistical Validity
    """

    def audit_validity(self, entity_id: str, setup_info: Dict[str, Any]) -> List[ReasoningIssue]:
        issues: List[ReasoningIssue] = []

        # Construct Validity: Anomaly vs Cyberattack
        if setup_info.get("dataset_family") in ["HDFS", "BGL"] and setup_info.get("claims_attack_detection", False):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-VAL-CONSTRUCT-{abs(hash(entity_id + 'construct')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.ATTACK_ANOMALY_CONFLATION,
                    affected_entity_id=entity_id,
                    message="Construct Validity Threat: System crash/performance anomalies in HDFS/BGL do not represent multi-stage cyberattacks.",
                    severity="HIGH",
                    mitigation="Re-scope claim to system anomaly detection or evaluate on dedicated attack benchmarks (DARPA TC, LANL).",
                )
            )

        # External Validity: Single dataset evaluation
        if setup_info.get("datasets_evaluated_count", 1) == 1:
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-VAL-EXT-{abs(hash(entity_id + 'ext')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.BENCHMARK_LIMITATION,
                    affected_entity_id=entity_id,
                    message="External Validity Threat: Evaluation restricted to a single benchmark dataset.",
                    severity="MEDIUM",
                    mitigation="Validate findings across at least two heterogeneous telemetry environments (LANL and DARPA TC).",
                )
            )

        return issues


class SecurityGuards:
    """
    Security and Epistemic Risk Guards (Sections 28..31, 72, 73).
    """

    def audit_security_guards(self, entity_id: str, statement: str) -> List[ReasoningIssue]:
        issues: List[ReasoningIssue] = []
        s_lower = statement.lower()

        # Unusual != Malicious (Section 30)
        if any(tool in s_lower for tool in ["powershell", "psexec", "nmap", "wmic", "remote administration"]):
            if "malicious" in s_lower and "context" not in s_lower and "privilege" not in s_lower:
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-UNUSUAL-{abs(hash(entity_id + 'admin')) % 1000000:06d}",
                        issue_type=ReasoningIssueType.ATTACK_ANOMALY_CONFLATION,
                        affected_entity_id=entity_id,
                        message="Unusual administrative commands (PowerShell/PsExec) are not inherently malicious without contextual process lineage and credential role analysis.",
                        severity="HIGH",
                        mitigation="Incorporate session role, user privileges, and multi-instance context before classifying as attack.",
                    )
                )

        # Representation != Detector Performance (Section 31)
        if "detector" in s_lower and "representation" in s_lower and "proves" in s_lower:
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-REP-DET-{abs(hash(entity_id + 'detector')) % 1000000:06d}",
                    issue_type=ReasoningIssueType.REPRESENTATION_DETECTOR_CONFOUND,
                    affected_entity_id=entity_id,
                    message="High end-to-end detector accuracy does not prove feature representation superiority unless measured via a frozen linear probe under identical information budgets.",
                    severity="HIGH",
                    mitigation="Execute Intrinsic Probe with frozen feature extractor (DQ-01 Probe Operational Order).",
                )
            )

        # Pseudonymization != Privacy (Section 72)
        if "pseudonym" in s_lower or "masking" in s_lower:
            if "privacy-preserving" in s_lower or "guarantees privacy" in s_lower:
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-PRIV-{abs(hash(entity_id + 'priv')) % 1000000:06d}",
                        issue_type=ReasoningIssueType.PRIVACY_OVERCLAIM,
                        affected_entity_id=entity_id,
                        message="Pseudonymization alone is vulnerable to auxiliary linkage and frequency reconstruction attacks (Shokri et al. 2017).",
                        severity="HIGH",
                        mitigation="Evaluate representation under formal Membership Inference Attack and Differential Privacy bounds.",
                    )
                )

        # Offline Benchmark != SOC Deployable (Section 73)
        if "deployable" in s_lower or "production ready" in s_lower:
            if not any(w in s_lower for w in ["throughput", "eps", "latency", "backpressure"]):
                issues.append(
                    ReasoningIssue(
                        issue_id=f"ISS-OPER-{abs(hash(entity_id + 'oper')) % 1000000:06d}",
                        issue_type=ReasoningIssueType.OPERATIONAL_OVERCLAIM,
                        affected_entity_id=entity_id,
                        message="Offline batch benchmark results cannot claim production SOC deployability without streaming throughput (EPS) and memory boundedness metrics.",
                        severity="HIGH",
                        mitigation="Measure streaming throughput under 100k EPS load (H4 evaluation).",
                    )
                )

        return issues


class BaselineFairnessAuditor:
    """
    Baseline Comparison Fairness Auditor (Section 44).
    """

    def audit_baseline_fairness(self, comparison_setup: Dict[str, Any]) -> List[ReasoningIssue]:
        issues: List[ReasoningIssue] = []
        if not comparison_setup.get("same_dataset", True):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-FAIR-DS-{abs(hash(str(comparison_setup))) % 1000000:06d}",
                    issue_type=ReasoningIssueType.BASELINE_UNFAIR,
                    affected_entity_id="BASELINE_COMPARISON",
                    message="Unfair Comparison: Models evaluated on disjoint datasets.",
                    severity="CRITICAL",
                    mitigation="Rerun all baselines on identical verified datasets.",
                )
            )
        if not comparison_setup.get("same_probe_capacity", True):
            issues.append(
                ReasoningIssue(
                    issue_id=f"ISS-FAIR-PROBE-{abs(hash(str(comparison_setup))) % 1000000:06d}",
                    issue_type=ReasoningIssueType.BASELINE_UNFAIR,
                    affected_entity_id="BASELINE_COMPARISON",
                    message="Unfair Comparison: Baselines used different downstream probe architectures.",
                    severity="HIGH",
                    mitigation="Standardize on frozen linear probe across all feature representations.",
                )
            )
        return issues

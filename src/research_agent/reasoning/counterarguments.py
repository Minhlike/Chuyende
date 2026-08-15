"""
Steelman Counterargument Generator & Dialectic Builder (Prompt 5 Sections 22, 23)
"""

from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import CounterargumentRecord


class CounterargumentBuilder:
    """
    Constructs steelman counterarguments against research claims and candidate inferences.
    Distinguishes agent-derived objections (OUR_COUNTERARGUMENT) from literature-backed criticisms.
    """

    def build_counterargument(
        self,
        claim_id: str,
        claim_statement: str,
        topic: str = "general",
    ) -> CounterargumentRecord:
        """
        Builds the strongest plausible objection against the given claim.
        """
        c_lower = claim_statement.lower()
        seq = abs(hash(claim_id + topic)) % 1000000
        counter_id = f"CTR-ARG-{seq:06d}"

        if "graph" in c_lower or "provenance" in c_lower:
            objection = "Observed performance improvements in graph neural models may result entirely from host/process identifier leakage in synthetic test splits rather than genuine multi-hop structural reasoning."
            basis = "Provenance graphs in benchmarks like DARPA TC exhibit repetitive process lineage paths where trivial baseline classifiers match GNN accuracy when node identifiers are exposed (Bilot et al. 2025)."
            test_resp = ["Apply node identifier masking", "Conduct host holdout validation", "Benchmark against lexical bag-of-words baseline"]
            severity = "FATAL"
        elif "parser" in c_lower or "template" in c_lower:
            objection = "Continuous parser-free token embeddings increase computational memory footprint and latency during streaming ingestion, risking backpressure in production SIEM pipelines."
            basis = "High event velocity in enterprise environments (e.g. >100k events/sec) demands sub-millisecond per-event processing, which heavy transformer or continuous embedding extractors may exceed."
            test_resp = ["Measure streaming throughput on 100k EPS benchmark", "Implement parameter dictionary caching"]
            severity = "SERIOUS"
        elif "privacy" in c_lower or "membership" in c_lower:
            objection = "Adding differential privacy noise or feature perturbation to protect log privacy significantly degrades intrusion detection recall on stealthy low-and-slow APT attacks."
            basis = "Subtle malicious anomalies occupy representation boundaries that noise perturbation easily obfuscates into benign distributions."
            test_resp = ["Plot Empirical Privacy-Utility Frontier (AUC vs Epsilon)", "Run Membership Inference Attack (Shokri et al.)"]
            severity = "SERIOUS"
        else:
            objection = f"The stated claim '{claim_statement[:60]}...' lacks cross-environment generalization evidence and may fail under domain shift."
            basis = "Evaluation confined to single benchmark dataset family without heterogeneous enterprise validation."
            test_resp = ["Evaluate on secondary telemetry dataset (LANL/BGL)", "Conduct domain shift stress test"]
            severity = "MODERATE"

        return CounterargumentRecord(
            counter_id=counter_id,
            objection=objection,
            basis=basis,
            evidence_ids=[],
            affected_claim_id=claim_id,
            severity=severity,
            is_steelman=True,
            origin="OUR_COUNTERARGUMENT",
            response_options=test_resp,
            is_resolved=False,
        )

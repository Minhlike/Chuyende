"""
Assumption Extraction & Challenge Auditor (Prompt 5 Sections 16, 17)
"""

from typing import List, Dict, Any, Optional
from research_agent.schemas.reasoning import AssumptionRecord


class AssumptionAuditor:
    """
    Identifies and challenges explicit and implicit methodological assumptions.
    Evaluates empirical testability and downstream consequences if assumptions fail.
    """

    # Domain-specific canonical implicit assumptions
    KNOWN_IMPLICIT_ASSUMPTIONS = {
        "gnn": [
            ("Audit graph edges reflect observable causality rather than mere coincidence.", "TESTABLE_BY_AUDIT", "Spurious edges induce over-smoothing and noisy representations."),
            ("Entity resolution and process-tree stitching are error-free.", "TESTABLE_BY_EXPERIMENT", "Broken links fragment provenance chains into disconnected subgraphs."),
            ("Graph degree distribution does not cause extreme over-squashing in hub nodes.", "TESTABLE_BY_EXPERIMENT", "High degree hubs lose multi-hop information rapidly (Alon & Yahav 2021)."),
        ],
        "mil": [
            ("A malicious bag contains at least one truly anomalous instance event.", "AXIOMATIC", "Violating this causes bag-level label noise and misattribution."),
            ("Instance pooling attention weights correlate with ground truth attack steps.", "TESTABLE_BY_EXPERIMENT", "Attention weights can focus on benign high-frequency background activities."),
        ],
        "log": [
            ("Log event timestamps reflect true causal ordering across distributed nodes.", "TESTABLE_BY_AUDIT", "Clock skew disrupts sequential and temporal message passing."),
            ("Log schemas remain stable over the evaluation timeframe (no template drift).", "TESTABLE_BY_EXPERIMENT", "Schema drift results in out-of-vocabulary representation collapse."),
        ],
        "privacy": [
            ("Adversary possesses auxiliary knowledge bounded by the declared threat model.", "AXIOMATIC", "Stronger auxiliary knowledge enables higher membership inference success."),
            ("Pseudonymization or noise perturbation preserves downstream intrusion utility.", "TESTABLE_BY_EXPERIMENT", "Excessive noise reduces detection precision and increases false positives."),
        ],
    }

    def audit_assumptions(self, entity_id: str, text: str) -> List[AssumptionRecord]:
        """
        Extract explicit and implicit assumptions for an architecture or claim.
        """
        assumptions: List[AssumptionRecord] = []
        t_lower = text.lower()
        seq = 1

        # Check for matching implicit domain assumptions
        for key, assumed_list in self.KNOWN_IMPLICIT_ASSUMPTIONS.items():
            if key in t_lower or (key == "log" and any(w in t_lower for w in ["template", "drain", "bert", "parser"])):
                for statement, testability, consequence in assumed_list:
                    ass_id = f"ASM-{abs(hash(entity_id + statement)) % 1000000:06d}"
                    assumptions.append(
                        AssumptionRecord(
                            assumption_id=ass_id,
                            statement=statement,
                            is_explicit=False,
                            required_by=[entity_id],
                            evidence_or_basis="Domain methodological invariant",
                            testability=testability,
                            violation_consequence=consequence,
                            status="UNTESTED",
                        )
                    )
                    seq += 1

        # Check for explicit condition words in text
        if "assuming" in t_lower or "provided that" in t_lower or "relies on" in t_lower:
            ass_id = f"ASM-{abs(hash(entity_id + 'explicit')) % 1000000:06d}"
            assumptions.append(
                AssumptionRecord(
                    assumption_id=ass_id,
                    statement=f"Explicit dependency stated in {entity_id}: '{text[:100]}...'",
                    is_explicit=True,
                    required_by=[entity_id],
                    evidence_or_basis="Explicit author statement",
                    testability="TESTABLE_BY_EXPERIMENT",
                    violation_consequence="Invalidates stated performance bounds.",
                    status="UNTESTED",
                )
            )

        return assumptions

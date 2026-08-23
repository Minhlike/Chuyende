# CHAPTER 3 — EVIDENCE INDEX FOR THESIS DOCUMENTATION (WORD-EVIDENCE-INDEX)

**Document Identifier:** `EVIDENCE-INDEX-CH3-V1.0`  
**Status:** **ACTIVE & AUDITED**  
**Purpose:** Canonical directory mapping experimental claims to verified machine artifacts, logs, and screenshot candidates for inclusion in Chapter 3 of the dissertation.

---

## 1. Pre-Execution & Protocol Verification Evidence

| Evidence Item ID | Description | Source Artifact Path | Checksum (SHA-256) | Screenshot Candidate |
| :--- | :--- | :--- | :--- | :--- |
| `EVID-CH3-PRE-001` | Raw HDFS LogHub Tarball Integrity Checksum | `datasets/raw/hdfs/HDFS_1.tar.gz` | `6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169` | `NO` |
| `EVID-CH3-PRE-002` | Canonical Split Definition (SPL-HDFS-001) | `datasets/manifests/SPL-HDFS-001.json` | `375d03831b143a531e21b106292b0c360dfab9cff2eb98b049d56221c97a514d` | `NO` |
| `EVID-CH3-PRE-003` | Causal Session Boundary & Purge Accounting | `datasets/manifests/SUBSET-MANIFEST-HDFS.json` | `5e888628469a5a54be66a01d51a99571be9c4b7ec3b7b80a6d25244b4da3cb00` | `YES` (Figure: Boundary Purges) |
| `EVID-CH3-PRE-004` | Stage A2 Pre-Registration Protocol (V1.3) | `experiments/protocol/STAGE-A2-PREREGISTRATION.md` | *Computed upon lock* | `NO` |
| `EVID-CH3-PRE-005` | Machine-Readable Graph Contract (V1.3) | `experiments/schemas/STAGE-A2-GRAPH-CONTRACT.json` | *Computed upon lock* | `NO` |
| `EVID-CH3-PRE-006` | Raw-to-Graph Extraction Mapping Contract | `experiments/schemas/STAGE-A2-RAW-TO-GRAPH-MAPPING.json` | *Computed upon lock* | `YES` (Table: Extraction Rules) |
| `EVID-CH3-PRE-007` | Empirical Relation Grounding Audit | `experiments/evidence/stage-a2/preexecution/RELATION-GROUNDING-AUDIT.json` | *Computed upon lock* | `YES` (Table: Relation Match Counts) |
| `EVID-CH3-PRE-008` | Full Population Graph Materialization Audit | `experiments/evidence/stage-a2/preexecution/HDFS-GRAPH-MATERIALIZATION-AUDIT.json` | *Computed upon lock* | `YES` (Table: Population Conservation) |
| `EVID-CH3-PRE-009` | Authorized Execution Subset Audit (35k/7.5k) | `experiments/evidence/stage-a2/preexecution/HDFS-EXECUTION-SUBSET-AUDIT.json` | *Computed upon lock* | `YES` (Table: Execution Conservation) |
| `EVID-CH3-PRE-010` | Pre-Execution Verification Gate Log | `scripts/verify_stage_a2_implementation_readiness.py` | Terminal stdout log | `YES` (Figure: Gate Pass Output) |

---

## 2. Test Firewall & Scientific Integrity Evidence

| Evidence Item ID | Description | Source Artifact / Method | Invariant Status | Screenshot Candidate |
| :--- | :--- | :--- | :--- | :--- |
| `EVID-CH3-FIREWALL-001` | Test Set Sealed Firewall Guarantee | `TestSetSealedError` fail-closed exception | `TEST_OPENED = false` (0 reads) | `YES` (Console exception test) |
| `EVID-CH3-FIREWALL-002` | Zero Stage A2 Optimizer Steps Pre-Execution | `STAGE-A2-PREEXECUTION-LOCK.json` | `OPTIMIZER_STEPS = 0` | `NO` |
| `EVID-CH3-FIREWALL-003` | Single Source of Truth Split Authority | `HDFSSplitAuthority` (SPL-HDFS-001) | `train_max_end < val_min_start` | `NO` |
| `EVID-CH3-FIREWALL-004` | Millisecond Epoch Timestamp Parity | `tests/test_stage_a2_graph_contract.py` | `max delta = 0.0` | `NO` |

# DATASET PROTOCOL & CANONICAL DATASET CARDS

**Document Identifier:** `CARD-DATA-20260821-V1.1`  
**Protocol Version:** 1.1.0  
**Status:** **LOCKED & CANONICAL**  

---

## 1. Two-Tier Dataset Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TWO-TIER BENCHMARK SUITE                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ TIER A: System Log Benchmarks        │ TIER B: Cyberattack Provenance Logs  │
│ - HDFS (LogHub, Xu et al., SOSP 09)  │ - DARPA TC Engagements E3 & E5       │
│ - BGL (LogHub, Oliner et al., DSN 07)│ - LANL Enterprise Cyber Security 2015│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Purpose:                             │ Purpose:                             │
│ - Parsing & template novelty stress  │ - Multi-host causal provenance graph │
│ - Dynamic parameter retention        │ - Multi-stage APT campaign context   │
│ - Unseen template drift & OOV tests  │ - MITRE ATT&CK tactical attribution  │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Boundary Restriction:                │ Boundary Restriction:                │
│ STRICTLY PROHIBITED from claiming    │ Ground truth strictly locked to      │
│ cyberattack semantics (B-01).        │ official engagement reports (B-02).  │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Detailed Dataset Cards

### Dataset Card 1: HDFS (Hadoop Distributed File System)
- **Official Source:** LogHub Repository / Xu et al., ACM SOSP 2009; Zhu et al., IEEE ISSRE 2023.
- **Version / Release:** `HDFS_v1` (LogHub release).
- **Acquisition State:** `PLANNED` (Record counts and raw checksums to be verified upon acquisition).
- **Observation Unit:** Event tuple $e_i$, Block session sequence $\mathcal{L}_{	ext{blk}}$, sliding window.
- **Label Granularity:** Block ID binary label (`Normal` vs `Anomaly`).
- **Permitted Claims:** Parameter retention (Block ID, IP, byte count), parsing robustness, template abstraction.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack semantics or provenance graph reasoning (`BOUNDARY-01`).

---

### Dataset Card 2: BGL (Blue Gene/L Supercomputer)
- **Official Source:** LogHub Repository / Oliner & Stearley, IEEE/IFIP DSN 2007; Zhu et al., ISSRE 2023.
- **Version / Release:** `BGL_v1` (Lawrence Livermore National Laboratory release).
- **Acquisition State:** `PLANNED`.
- **Observation Unit:** Event message, Node temporal sequence, fixed time window $\Delta t$.
- **Label Granularity:** RAS alert category flag (`-` = non-alert, non-`-` = alert).
- **Permitted Claims:** Robustness against template drift, long-term temporal shift, OOV log templates.
- **Prohibited Overclaims:** Strictly prohibited from claiming cyberattack defense or lateral movement detection (`BOUNDARY-01`).

---

### Dataset Card 3: DARPA Transparent Computing (TC) Engagements E3 & E5

| Parameter | Official Release Specification | Our Pre-Registered Experimental Subset |
| :--- | :--- | :--- |
| **Engagements** | Engagement 3 (E3, April 2018) & Engagement 5 (E5, May 2019). | E3 and E5 official releases. |
| **Performer Universe** | **E3:** CADETS, ClearScope, FiveDirections, THEIA, TRACE.<br>**E5:** CADETS, ClearScope, FiveDirections, MARPLE, THEIA, TRACE. | **Selected Subset:**<br>1) **THEIA** (Linux LSM kernel audit);<br>2) **CADETS** (FreeBSD DTrace/Audit);<br>3) **FiveDirections** (Windows Sysmon/ETW). |
| **Subset Selection Rationale** | Diverse instrumentation paradigms across multiple OS kernels. | Pre-registered prior to test evaluation to provide multi-platform OS diversity with stable process-socket bindings. |
| **Schema Versions** | **E3: CDM18** (Common Data Model release 18).<br>**E5: CDM20** (Common Data Model release 20). | Strictly **CDM18** for E3 and **CDM20** for E5 (CDM19 count = 0). |
| **Ground Truth Reports** | *DARPA Transparent Computing Engagement 3 / 5 Evaluation Ground Truth Reports* (SPAWAR / MIT Lincoln Laboratory / BAE Systems). | Ground truth event mapping status: `PENDING_ARTIFACT_PARSE`. |
| **Acquisition State** | `PLANNED` | `PLANNED` |
| **Permitted Claims** | Kernel-level provenance graph representation, cross-view sequential-graph alignment, multi-stage APT attribution. | Evaluated with capacity-controlled frozen probes. |
| **Prohibited Overclaims** | Causal physical reality claims without explicit causal identification assumptions (`BOUNDARY-03`). | Arbitrary post-hoc performer selection. |

---

### Dataset Card 4: LANL Enterprise Multi-Source Cyber-Security Events

- **Official Source:** Los Alamos National Laboratory / Alexander D. Kent, 2015. DOI: 10.17021/1110439.
- **Version / Release:** `LANL_CyberSecurity_2015_v1` (`auth.txt.gz`, `proc.txt.gz`, `flows.txt.gz`, `redteam.txt.gz`).
- **Acquisition State:** `PLANNED`.
- **Red Team Record Count:** `PENDING_VERIFICATION` (Exact valid record count and file checksum verified upon physical archive acquisition).
- **Exact Red Team Label Invariant:**
  > **Hard Invariant:** The `redteam.txt` file contains known compromised authentication events only. Each entry is strictly an authentication 4-tuple: `(Time, User@Domain, SourceHost, DestHost)`.
- **Prohibited Label Propagation:**
  - Strictly **NO** propagation to `proc.txt` (processes are not automatically labeled malicious).
  - Strictly **NO** propagation to `flows.txt` or DNS telemetry.
  - Strictly **NO** expansion to arbitrary temporal windows, whole hosts, or whole user sessions without pre-registered uncertainty modeling.
- **Pre-Registered Weak Evidence Attribution Rule:**
  Coarse bag labels for Stage B MIL are formed over fixed host-day authentication bags $\mathcal{B}_{h, d}$. A bag is positive ($\mathcal{Y}_{\mathcal{B}} = 1$) if and only if it contains $\ge 1$ exact match in `redteam.txt`. All instances within the bag remain weakly labeled, and attention attribution uncertainty is reported.

# CHAPTER 3 — REAL TRAINING DESIGN & DATASET-ROLE SPECIFICATION
**Protocol Status:** FROZEN PRE-EXECUTION DESIGN SPECIFICATION  
**Execution Status:** DESIGN ONLY (NO TRAINING INITIATED / TEST SEALED)  
**Document ID:** `SPEC-REAL-TRAINING-CH3-V1.1`  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `data/ch3-real-materialization`

---

## 1. Scientific Principles & Dataset-Role Boundary (Claim Hygiene)

1. **Strict Test Set Firewall:** The Test partition for all datasets remains SEALED throughout architecture design, training stage implementation, hyperparameter selection, and threshold tuning.
2. **Tier-A vs. Tier-B Evidential Boundary:**
   - **Tier A (HDFS LogHub & BGL):** Serves strictly as representation, template/parameter fidelity, and system-log anomaly context stress tests.
   - **CRITICAL HYGIENE:** HDFS/BGL logs **MUST NOT** independently establish cyberattack semantic fidelity, provenance attack semantics, or the final confirmatory claim for Hypothesis $H1$.
   - **Confirmatory Security Claims:** Any final security-semantic conclusion for $H1$ requires supporting Tier B evidence (DARPA TC E3) where ground-truth cyberattack and security behaviors are natively present.
3. **Role-Purity Invariant:** Synthetic proxy events from smoke tests MUST NEVER be reused in confirmatory experiments. Real multi-view experiments require genuine registered sequence $\leftrightarrow$ graph correspondence from native telemetry.
4. **Multi-Seed Protocol:** All empirical models must be evaluated across 5 canonical random seeds: `42`, `1337`, `2024`, `7`, `999`.

---

## 2. Dataset-Role Matrix

| Dataset | Tier | Canonical Role | Input Views | Evidential Boundary & Forbidden Usages |
| :--- | :---: | :--- | :--- | :--- |
| **HDFS LogHub** | Tier A | Sequence Representation ($z_{\text{seq}}$), Parameter Fidelity, System-Log Anomaly Detection Stress Test | Sequence View Only | MUST NOT be used as provenance graph or standalone security attack ground truth |
| **BGL Supercomputer** | Tier A | Long-Horizon Temporal Drift, Out-of-Vocabulary Robustness, Alert Log Stress Test | Sequence View Only | Alert tags are system alerts, MUST NOT be relabeled as cyberattacks |
| **DARPA TC E3** | Tier B | Temporal GNN ($z_{\text{graph}}$), Multi-View Alignment ($H2$), Provenance Graph Robustness, Real Attack Attribution ($H1$ Security) | Sequence + Provenance Graph Views | MUST NOT use synthetic event proxies; CDM18 raw ingestion required |
| **LANL Cyber** | Tier B | Identity & Authentication Linkability ($H5$), Controlled Linkability | Auth Event Sequences & Graph | MUST NOT fabricate ground-truth attack labels |

---

## 3. Real Training Stages Pipeline (Design Only)

```mermaid
graph TD
    subgraph "Stage A1: Sequence Pretraining"
        A1_Data["Tier A Train Partition (HDFS / BGL)"] --> A1_Trans["Sequence Transformer"]
        A1_Trans --> A1_Loss["L_seq = L_MEP + L_MPP + L_time"]
    end

    subgraph "Stage A2: Provenance Graph Pretraining"
        A2_Data["Tier B Train Partition (DARPA TC E3 CDM18)"] --> A2_TGNN["Temporal GNN (Msg + Agg + Update)"]
        A2_TGNN --> A2_Loss["L_graph = L_mask_node + L_mask_edge + L_time_gap"]
    end

    subgraph "Stage A3: Multi-View Latent Alignment"
        A3_Pair["Real Paired Telemetry (DARPA CDM18)"] --> A1_Trans
        A3_Pair --> A2_TGNN
        A1_Trans --> A3_VICReg["VICReg Loss (Invariance + Variance + Covariance)"]
        A2_TGNN --> A3_VICReg
        A3_VICReg --> A3_Fuse["L_fuse_rec (Gated Multi-View Fusion)"]
    end

    subgraph "Stage B: Multiple Instance Learning & Readout"
        A3_Fuse --> B_MIL["MIL Gated Attention Aggregator"]
        B_MIL --> B_Loss["L_MIL (Coarse-to-Fine Bag Loss)"]
    end

    subgraph "Validation Gate & Model Selection"
        B_Loss --> Val_Gate["Validation Partition Only (5 Canonical Seeds)"]
    end
```

---

## 4. Hardware Resource & Memory Optimization Plan (RTX 3050 Ti Laptop GPU)

> [!NOTE]
> **CLASSIFICATION:** `PLANNING_ESTIMATE`  
> **STATUS:** `NOT_EMPIRICAL_RESULT` / `NOT_SLO_EVIDENCE`  
> Actual operational metrics are determined exclusively by post-run benchmark logs.

- **Dedicated VRAM Ceiling:** 4096 MB (4.0 GB)
- **Host RAM Budget:** 16.0 GB
- **Micro-Batch Size:**
  - Sequence Transformer: `batch_size = 16`, `max_seq_len = 128`
  - Temporal GNN: `batch_size = 8`, `window_size = 200` causal interaction events
- **Gradient Accumulation:** 4 micro-steps (effective batch size = 32–64)
- **Entity Memory Bank Management:**
  - `max_entities = 5000` per active stream with LRU eviction.
  - Active state payload bytes $\le 2.5 \text{ MB}$.
- **Estimated Resource Profile (Planning Estimates Only):**
  - Estimated Peak VRAM: $\approx 2.8 \text{ GB}$ (Planning target $\le 70\%$ of physical VRAM)
  - Estimated Peak Host RAM: $\approx 4.8 \text{ GB}$ (Planning target $\le 35\%$ of host RAM)

---

## 5. Prerequisites for Real Confirmatory Training
1. Acquisition and checksum verification of raw DARPA TC E3 CDM18 archives on drive `D:\Research\datasets\raw\darpa\e3\`.
2. Validation of ground-truth attack manifest mapping without looking at sealed Test events.
3. Execution of full Validation-only hyperparameter tuning across seeds `[42, 1337, 2024, 7, 999]`.

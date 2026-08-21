# THREE-LAYER EVALUATION METRIC CONTRACT & VALIDATION-ONLY CALIBRATION

**Document Identifier:** `CON-METRIC-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-08`, `RC-10`), Roadmap Boundary (`BOUNDARY-04`, `BOUNDARY-08`).  

---

## 1. Three-Layer Evaluation Architecture

To prevent downstream detector artifacts from masquerading as representation quality (`BOUNDARY-04`), the evaluation suite is organized into three strictly decoupled layers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THREE-LAYER EVALUATION HIERARCHY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: INTRINSIC REPRESENTATION METRICS                                   │
│ - Representation Variance & Collapse Diagnostics (Var, Cov, Effective Rank)│
│ - Cross-View Latent Alignment & Mutual Information Proxy                    │
│ - Temporal & Entity Continuity Preservation                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: CAPACITY-CONTROLLED FROZEN PROBE BENCHMARKS                        │
│ - Extractor Weights Completely Frozen (theta*)                              │
│ - Fixed Probes: Linear Probe, Logistic Regression, Distance/kNN, Shallow MLP│
│ - Supervised MITRE ATT&CK Tactic/Technique Multi-Label Classification       │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: OPERATIONAL & STREAMING DEPLOYABILITY METRICS                      │
│ - Precision, Recall, Macro-F1, PR-AUC, ROC-AUC, FPR                         │
│ - Recall @ Fixed FPR (0.1%, 1.0%) & Recall @ Alert Budget (e.g. 10/day)     │
│ - Detection Delay, Ingestion Throughput (events/s), Latency (p50/p95/p99)   │
│ - Peak RAM, Steady-State RAM, VRAM, and Bounded State Size |S_t|            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer 1 — Intrinsic Representation Metrics

These metrics assess geometry, diversity, and alignment of the latent manifold $\mathbf{z} \in \mathbb{R}^d$ without requiring downstream class labels:

1. **Representation Variance (Collapse Indicator):**
   $$\text{Var}(\mathbf{Z}) = \frac{1}{d} \sum_{j=1}^d \text{Var}(\mathbf{z}_{:, j}) = \frac{1}{d} \sum_{j=1}^d \left( \frac{1}{N} \sum_{i=1}^N (z_{i, j} - \bar{z}_j)^2 \right)$$
   *Threshold:* $\text{Var}(\mathbf{Z}) \ge \tau_{\text{var}} = 0.05$ (Fail if $< 0.01$, indicating dimensional collapse).

2. **Effective Dimensional Rank (Covariance Condition):**
   $$\text{erank}(\mathbf{Z}) = \exp\left( - \sum_{k=1}^d p_k \ln p_k \right), \quad p_k = \frac{\sigma_k(\mathbf{Z})}{\sum_{j=1}^d \sigma_j(\mathbf{Z})}$$
   Where $\sigma_k(\mathbf{Z})$ are the singular values of the centered feature matrix $\mathbf{Z}$. Measures the effective number of utilized orthogonal dimensions (Fail if $< 0.20 \times d$).

3. **Cross-View Latent Alignment Consistency:**
   $$\text{Align}(\mathbf{z}^{(\text{seq})}, \mathbf{z}^{(\text{graph})}) = \frac{1}{N} \sum_{i=1}^N \frac{\langle \mathbf{z}_i^{(\text{seq})}, \mathbf{z}_i^{(\text{graph})} \rangle}{\|\mathbf{z}_i^{(\text{seq})}\|_2 \|\mathbf{z}_i^{(\text{graph})}\|_2}$$

4. **Temporal Stability Invariance:**
   $$\text{Stab}(\mathbf{z}) = \frac{1}{N-1} \sum_{t=1}^{N-1} \|\mathbf{z}_{t+1} - \mathbf{z}_t\|_2$$

---

## 3. Layer 2 — Capacity-Controlled Frozen Probes

To evaluate representation utility independently of downstream detector learning capacity:

1. **Extractor Freezing Contract:**
   $$\theta^* = \text{freeze}(f_\theta), \quad \nabla_{\theta} \mathcal{L}_{\text{probe}} \equiv \mathbf{0}$$
   The extractor parameters $\theta^*$ are immutable during all Layer 2 evaluations.

2. **Probe Architectures:**
   - **Linear / Logistic Probe:** $\hat{\mathbf{y}} = \sigma(\mathbf{W}^\top \mathbf{z} + \mathbf{b})$ (Zero hidden layers, parameter budget $\le d \times C$).
   - **Non-Parametric Distance Probe / kNN:** $k=5$, cosine distance to normal support library.
   - **Shallow MLP Probe (Optional Pre-Registered):** 1 hidden layer ($h=128$), ReLU activation, strictly bounded capacity.

---

## 4. Layer 3 — Operational & Security Performance Metrics

1. **Core Classification Metrics:**
   $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
   $$\text{PR-AUC} = \int_0^1 P(R) \, dR, \quad \text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

2. **Security SOC Constraints:**
   - **Recall@Fixed-FPR:** $\text{Recall}_{\text{FPR} \le 0.1\%}$ (Crucial for minimizing alert fatigue in high-volume enterprise streams).
   - **Recall@Alert-Budget:** Recall achieved when daily alert generation is constrained to $\le K_{\text{budget}}$ alerts/host-day (e.g. $K=10$).

3. **Operational Streaming Metrics:**
   - **Detection Delay ($\Delta t_{\text{detect}}$):** Time delta between the first malicious event $e_{\text{first}}$ in an APT campaign and the first generated alert $\hat{y} \ge \tau$.
   - **Throughput:** Processed events per wall-clock second ($\text{events/s}$).
   - **Processing Latency:** Per-event processing time percentiles: p50, p95, p99 (measured in milliseconds).
   - **State Memory Consumption:** Peak RAM, Steady-State RAM, and GPU VRAM (MB) over long-horizon streaming ($> 72$ hours).

---

## 5. Validation-Only Decision Threshold & Calibration Contract

To eliminate threshold peeking and optimistic performance inflation:

1. **Threshold Fitting Protocol:**
   $$\tau^* = \arg\max_{\tau \in [0, 1]} F_1(\tau; \mathcal{D}_{\text{val}}) \quad \text{or} \quad \tau^* = \min \{ \tau \mid \text{FPR}(\tau; \mathcal{D}_{\text{val}}) \le \alpha_{\text{target}} \}$$
   The optimal decision threshold $\tau^*$ is selected strictly on the Validation split.

2. **Probability Calibration:**
   Platt scaling (logistic regression on logits) or Isotonic Regression parameters are fit strictly on $\mathcal{D}_{\text{val}}$.

3. **Sealed Test Evaluation:**
   $$\hat{y}_{\text{test}} = \mathbb{I}[\text{Calibrate}(\text{Score}(\mathbf{z}_{\text{test}})) \ge \tau^*]$$
   The threshold $\tau^*$ is applied unconditionally to $\mathcal{D}_{\text{test}}$ without any post-hoc adjustment.

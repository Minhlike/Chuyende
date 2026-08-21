# CHAPTER 3 PROTOCOL AMENDMENT RECORD (PRE-TEST LOCK)
**Timestamp:** 2026-08-22T03:30:00+07:00  
**Execution State:** ANY_MODEL_TRAINED = NO, ANY_TEST_OPENED = NO, RESULTS_SEEN = NO  

---

### Amendment 1: Statistical Decision Semantics (Replacing Binary Accept H0)
- **Previous Language:** Verdict returned binary "REJECT_H0" vs "ACCEPT_H0".
- **Amended Language:** Formally split into three epistemic states:
  1. `SUPPORTED`: Pre-registered effect direction/margin satisfied AND family-wise adjusted significance gate passes ($p \le \alpha_{\text{adj}}$ with positive CI lower bound).
  2. `INCONCLUSIVE`: Observed effect is statistically insufficient ($p > \alpha_{\text{adj}}$ or confidence interval spans zero), without crossing the falsification boundary.
  3. `FALSIFIED`: Observed effect crosses explicit opposite-direction falsification boundary, suffers variance collapse ($< 0.01$), or drops to positive prevalence chance level.
- **Rationale:** Avoids the standard fallacy of affirming the null ($ACCEPT\_H_0$) upon non-significance and establishes clear falsification criteria.

---

### Amendment 2: Primary Confirmatory Anomaly Metric — Average Precision (AP)
- **Previous Language:** Inconsistently used "PR-AUC" and "Average Precision" interchangeably.
- **Amended Language:** The primary confirmatory ranking metric for class-imbalanced log anomaly detection across H1, H2, and H3 is formally locked as **Average Precision (AP)**:
  $$\text{AP} = \sum_{n} (R_n - R_{n-1}) P_n$$
  matching `sklearn.metrics.average_precision_score`. Trapezoidal PR-AUC is retained only as an auxiliary descriptive statistic.
- **Prevalence Baseline:** The chance reference level for AP is locked to positive sample prevalence $\pi = \frac{N_{\text{pos}}}{N_{\text{total}}}$.

---

### Amendment 3: H2 Non-Oracle Multi-View Baseline Evaluation
- **Previous Language:** Unaligned baseline or single-view baseline allowed post-hoc max oracle.
- **Amended Language:** H2 evaluates three separate, pre-registered pairwise comparisons against the Aligned Multi-View model ($z_{\text{mv}}$):
  1. $z_{\text{mv}}$ vs $z^{(\text{seq})}$ (Sequence-Only)
  2. $z_{\text{mv}}$ vs $z^{(\text{graph})}$ (Graph-Only)
  3. $z_{\text{mv}}$ vs $z^{(\text{unaligned})}$ (Unaligned Fusion)
  Multiple testing correction applies Bonferroni adjustment with family size $m=3$ ($\alpha_{\text{adj}} = 0.0167$).

---

### Amendment 4: H5 Proposed Candidate and Adversary Advantage Metrics
- **Previous Language:** Informal reference to Controlled Linkability regime as H5 candidate.
- **Amended Language:** `PRIVACY_AWARE_PARAMETERIZED` is formally designated as the proposed representation candidate for H5 Pareto frontier evaluation, evaluated against `RAW_IDENTIFIERS`, `EXTREME_ANONYMIZATION`, and `CONTROLLED_LINKABILITY`.
- **Adversary Risk Metric:** For Linkage and Membership Inference (MIA), attack advantage is locked to:
  $$\text{Advantage}_{\text{AUC}} = 2 \cdot |\text{AUC} - 0.5| \in [0, 1]$$
  Defense score is locked to $1 - \text{Advantage}_{\text{AUC}}$, preventing inverted classifier evasion from masquerading as privacy defense.

---

### Amendment 5: Removal of Stale Split Bounds & Reconciled Raw Data Provenance (Pre-Test Amendment)
- **Previous Language:** Speculative split day ranges were listed for DARPA (Days 1..14 / 15..21) and LANL (Days 1..89), while HDFS manifest contained a stale line count (11,750,692).
- **Amended Language:**
  1. **DARPA TC E3:** Split boundaries are formally locked as **`PENDING_RAW_CDM18_ALIGNMENT`** until official DARPA TC E3 CDM18 raw artifacts and scenario timelines are materialized and verified.
  2. **LANL Cyber 1:** Split boundaries are formally locked as **`PENDING_ACQUISITION`** (the official LANL Cyber 1 dataset comprises 58 days total, removing the invalid 89-day specification).
  3. **HDFS Provenance & Causal Split:** Corrects official raw HDFS count to exact empirical value **`11,175,629`** lines (satisfying exact conservation $11175629 = 11175629 + 0 + 0$). Replaces random session shuffling with strictly deterministic causal sorting by `(session_start_time, block_id_tiebreak)` where $\max(\text{Train}) \le \min(\text{Val}) \le \min(\text{Test})$.
  4. **BGL Provenance:** Reconciles official raw record count **`4,747,963`** lines and observed minimum timestamp **`1117838570`** across temporal partitions (Days 1-150 Train, Days 151-180 Val, Days 181-215 Sealed Test).

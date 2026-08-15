# CANONICAL RESEARCH ROADMAP & SPECIFICATION

**Title:** Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công  
**Central Research Object:** Feature representation vector / manifold \( \mathbf{z} \in \mathbb{R}^d \)  
**Core Abstraction:** \( f_\theta : \mathcal{L}_{1:t} \to \mathbf{z}_t \)  
**Version:** 1.0.0  
**Status:** CANONICAL & INVIOLABLE RESEARCH SPECIFICATION  

---

## 0. RESEARCH FOUNDATION & CANONICAL BOUNDARY

### 0.1 Object of Research
The central subject of this study is exclusively the **feature representation** \( \mathbf{z} \), not the downstream detector \( g \) and not an end-to-end intrusion detection system (IDS).
```text
Logs L ──► Feature Extractor fθ ──► Representation z ──► Downstream Probe/Detector g ──► Evaluation
```
Downstream detectors and evaluation probes shall not perform hidden representation learning during independent representation evaluations.

### 0.2 Three-Tier Representation Contract
1. **PRESERVE:**
   - Temporal order
   - Security-relevant parameters (IP, path, user, privilege, command arguments)
   - Entity linkage across log streams
   - Dependency context and information flows
2. **INVARIANT:**
   - Benign formatting variations
   - Template renaming and syntactic noise
   - Non-semantic identifiers
3. **EXCLUDE:**
   - Dataset IDs and environment artifacts
   - Campaign IDs and scenario identifiers
   - Split-specific identifiers
   - Leakage-derived signals and dataset shortcuts

---

## 1. FIVE RESEARCH AXES

- **AXIS A1 — REPRESENTATION FIDELITY:**  
  *Problem:* Security-semantic information loss during dynamic parameter abstraction.  
  *Path:* `1.3.1 ──► 2.2.1 / 2.3 ──► 3.2.1 / 3.3.1`  
  *Core Question:* Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?

- **AXIS A2 — MULTI-VIEW REPRESENTATION:**  
  *Problem:* Cross-view misalignment, representation collapse, and negative transfer.  
  *Path:* `1.3.2 ──► 2.4 ──► 3.3.1`  
  *Core Risks:* Collapse, negative transfer, missing views, partial correspondence.

- **AXIS A3 — VALIDITY UNDER SHIFT:**  
  *Problem:* Pipeline leakage, shortcut learning, and non-stationary distribution drift.  
  *Path:* `1.3.3 ──► 2.1 / 2.2 ──► 3.1.2 / 3.3.2 / 3.3.3`  
  *Core Risks:* Leakage, shortcuts, unseen templates, unseen entities, unseen campaigns, adversarial telemetry.

- **AXIS A4 — WEAK EVIDENCE ATTRIBUTION:**  
  *Problem:* Coarse labels, credit assignment ambiguity, and admin-noise confusion.  
  *Path:* `1.3.4 ──► 2.4.2 / 2.4.3 ──► 3.2.3 / 3.4.1`  
  *Core Risks:* Coarse labels, incorrect credit assignment, benign administration confused with attack.

- **AXIS A5 — PRIVACY-AWARE OPERATIONAL STREAMING:**  
  *Problem:* Entity continuity vs privacy leakage under bounded streaming budgets.  
  *Path:* `1.3.5 ──► 2.1.2 / 2.2.2 ──► 3.3.4 / 3.4.2`  
  *Core Trade-offs:* Utility vs linkability, bounded state, latency, peak memory, long-horizon context.

---

## 2. CANONICAL RESEARCH QUESTIONS (RQ1–RQ5)

- **RQ1 — REPRESENTATION FIDELITY:**  
  *English:* Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?  
  *Vietnamese:* Có thể xây dựng representation loại bỏ nhiễu cú pháp nhưng vẫn bảo toàn các dynamic parameters có ý nghĩa an toàn quan trọng hay không?

- **RQ2 — CROSS-VIEW ALIGNMENT:**  
  *English:* Can heterogeneous views be aligned without representation collapse or negative transfer while preserving useful view-specific information?  
  *Vietnamese:* Có thể căn chỉnh các view dị thể mà không gây representation collapse, negative transfer, đồng thời vẫn bảo toàn thông tin hữu ích đặc thù của từng view hay không?

- **RQ3 — VALIDITY WITHOUT SHORTCUTS:**  
  *English:* Does the representation remain useful after removing dataset shortcuts and under distribution shift?  
  *Vietnamese:* Representation có còn hữu ích sau khi loại bỏ shortcut của dataset và khi phân phối dữ liệu thay đổi hay không?

- **RQ4 — WEAK EVIDENCE ATTRIBUTION:**  
  *English:* Can attack evidence be assigned under coarse labels without learning benign administrative behavior as inherently malicious?  
  *Vietnamese:* Có thể gán đúng attack evidence dưới coarse labels mà không học nhầm các hành vi quản trị hợp pháp thành malicious hay không?

- **RQ5 — PRIVACY–SECURITY TRADE-OFF:**  
  *English:* What balance between entity continuity and privacy leakage yields useful security representations?  
  *Vietnamese:* Đâu là sự cân bằng chấp nhận được giữa entity continuity và privacy leakage để representation vẫn hữu ích cho phân tích an toàn?

---

## 3. CANONICAL HYPOTHESES (H1–H5)

- **H1 — FIDELITY:** Parameter-aware representation provides greater security-semantic fidelity than template-only representation.
- **H2 — MULTI-VIEW:** Controlled cross-view alignment improves representation quality without inducing collapse or destructive negative transfer.
- **H3 — ROBUSTNESS:** The proposed representation retains useful performance after shortcut removal and under distribution shift.
- **H4 — OPERATIONAL:** Any representation-quality improvement must remain within explicit latency, throughput, memory and bounded-state constraints.
- **H5 — PRIVACY:** Controlled linkability can yield a superior Utility–Privacy trade-off compared with both raw identifiers and extreme anonymization.

---

## CHAPTER 1. TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG DỮ LIỆU LOG VÀ THÁCH THỨC BẢO TOÀN NGỮ CẢNH AN TOÀN

**Mục tiêu:** Thiết lập bài toán biểu diễn log, tiêu chí đối với đặc trưng có giá trị an toàn, hệ thống hóa các phương pháp và hình thành các RQ mà Chương 2 phải trả lời.

### 1.1. Bài toán biểu diễn log trong phát hiện tấn công đa giai đoạn
- **1.1.1. Không gian dữ liệu log doanh nghiệp: tốc độ cao, mất cân bằng cực đoan và phân phối biến đổi**
  - **1.1.1.1. Nguồn log, đơn vị quan sát và tính dị thể**  
    *Nguồn log:* System, Audit, Application, Authentication, Network, Provenance.  
    *Đơn vị quan sát:* message, event, sequence/session, entity, edge/subgraph.
  - **1.1.1.2. Phụ thuộc thời gian, mất cân bằng và các dạng drift**
    - **1.1.1.2.1. Phân biệt:** Concept Drift, Template Drift, Population Drift, Representation Drift.
- **1.1.2. Hành vi tấn công đa giai đoạn và ánh xạ đa nhãn MITRE ATT&CK tactic/technique**
  - **1.1.2.1. ATT&CK như không gian bằng chứng hành vi, không phải chuỗi trạng thái tuyến tính**
  - **1.1.2.2. Ground truth, quy tắc ánh xạ và bất định chú thích**
- **1.1.3. Các mức Token–Event–Sequence/Session–Entity–Graph và Representation Contract**
  - **1.1.3.1. Preserve / Invariant / Exclude** (Bảo toàn temporal, parameters, linkage; bất biến format; loại bỏ shortcuts).
  - **1.1.3.2. Phân biệt:** feature extraction, representation learning, detection. Output nghiên cứu là representation \( \mathbf{z} \).

### 1.2. Phân tích so sánh các nhóm phương pháp hiện đại
- **1.2.1. Phương pháp thống kê/cú pháp: Event Count / Frequency / Entropy / Template Features**
  - **1.2.1.1. Cơ chế, ưu điểm và độ phức tạp**
  - **1.2.1.2. Mất thông tin do abstraction và phụ thuộc parser** (parameter loss, template collision, parser instability, unseen templates).
- **1.2.2. Phương pháp semantic–sequential: embeddings, self-supervised, Transformer, parsing-free**
  - **1.2.2.1. DeepLog/LSTM, semantic embedding, masked/self-supervised learning, Transformer, LogBERT và các phương pháp kế tiếp**
  - **1.2.2.2. So sánh parser-based, parser-free, pretrained; kiểm soát external information và pretraining-data advantage**
- **1.2.3. Provenance graph và graph representation learning**
  - **1.2.3.1. Các thực thể (process, file, socket, user, host) và edge type, direction, time**
  - **1.2.3.2. Các thách thức:** dependency explosion, false dependency, long-range dependency, over-smoothing, over-squashing (*Nguyên tắc bắt buộc: dependency \(\neq\) causal effect*).

### 1.3. Các khoảng trống nghiên cứu cốt lõi
- **1.3.1. Mất thông tin security-semantic khi abstraction dynamic parameters**
  - **1.3.1.1. Template equivalence không đồng nghĩa với security semantic equivalence** (IP, path, user, privilege, command arguments).
  - **1.3.1.2. RQ1:** Có thể loại bỏ syntactic noise nhưng vẫn bảo toàn security-critical dynamic parameters hay không?
- **1.3.2. Cross-view alignment**
  - **1.3.2.1. Các vấn đề:** identifiability, representation collapse, negative transfer.
  - **1.3.2.2. Missing-view và partial correspondence**
  - **1.3.2.3. RQ2:** Có thể align các view mà không collapse/negative transfer, đồng thời giữ thông tin hữu ích đặc thù từng view hay không?
- **1.3.3. Pipeline/Temporal/Identity Leakage, Shortcut Learning và Representation Drift**
  - **1.3.3.1. Các leakage paths:** parser/vocabulary, normalization/statistics, host/entity/campaign, threshold/hyperparameter, pretraining, future information.
  - **1.3.3.2. Dataset shortcut:** executable, path, host, template IDs vô tình trở thành attack labels.
  - **1.3.3.3. RQ3:** Representation có còn hữu ích sau khi loại bỏ shortcut hay không?
- **1.3.4. Coarse labels, credit assignment và admin-noise**
  - **1.3.4.1. Label/evidence granularity mismatch**
  - **1.3.4.2. Benign-but-risky administrative activity:** PowerShell, privilege escalation, remote admin, scanning không tự thân đồng nghĩa malicious.
  - **1.3.4.3. RQ4:** Có thể assign evidence mà không học benign administrative activity thành malicious hay không?
- **1.3.5. Privacy–Security trade-off**
  - **1.3.5.1. Controlled linkability versus re-identification**
  - **1.3.5.2. Threats:** membership inference, representation/model inversion.
  - **1.3.5.3. RQ5:** Đâu là cân bằng chấp nhận được giữa entity continuity và privacy leakage?

---

## CHAPTER 2. ĐỀ XUẤT PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG ĐA VIEW BẢO TOÀN NGỮ CẢNH VÀ NHẬN THỨC QUYỀN RIÊNG TƯ

**Mục tiêu:** Định nghĩa extractor contract, bounded streaming, bảo toàn semantics và xuất representation \( \mathbf{z} \) tương đối độc lập với downstream detector.

### 2.1. Phát biểu bài toán và giới hạn streaming
- **2.1.1. Multi-view representation, Representation Contract và extractor–detector boundary**
  - **2.1.1.1. Canonical abstraction:** \( f_\theta : \mathcal{L}_{1:t} \to \mathbf{z}_t \). Định nghĩa input history, output granularity, allowed state, allowed supervision.
  - **2.1.1.2. Hypotheses:** H1 (Fidelity), H2 (Multi-view), H3 (Robustness), H4 (Operational), H5 (Privacy).
- **2.1.2. Bounded-State Streaming Complexity**
  - **2.1.2.1. State lifecycle:** TTL, eviction, compaction/sketching, maximum memory.
  - **2.1.2.2. Event-time:** late events, out-of-order events, missing events, backpressure.
  - **2.1.2.3. Trade-off:** long-horizon APT context \(\leftrightarrow\) bounded state.
- **2.1.3. Kiến trúc và I/O**
  - **2.1.3.1. Pipeline:** Raw logs \(\to\) Parsing/Canonicalization \(\to\) Temporal/Entity Context \(\to\) Sequential View + Provenance View \(\to\) Alignment \(\to\) \( \mathbf{z} \).
  - **2.1.3.2. Phân biệt Training Plane và Inference Plane** (Không cho phép future/test information vào streaming inference).

### 2.2. Tiền xử lý và bảo vệ dynamic parameters
- **2.2.1. Parsing, Typed Canonicalization, Entity Resolution và Security-aware Parameter Retention**
  - **2.2.1.1. Typed schema:** timestamp, event type, actor/entity, object, action, dynamic parameters.
  - **2.2.1.2. Giữ security-semantic parameters, chuẩn hóa formatting noise**
  - **2.2.1.3. Leakage-safe preprocessing:** fit chỉ trên Train/Validation theo causal-time order.
- **2.2.2. Privacy Threat Model + Controlled Linkability**
  - **2.2.2.1. Data/entity adversary:** linkage, re-identification.
  - **2.2.2.2. Model adversary:** membership inference, representation/model inversion.
  - **2.2.2.3. Mechanism contract:** pseudonymization, tokenization, controlled linkability (Không tuyên bố privacy nếu chưa có attack-based evaluation).
- **2.2.3. Đồng bộ thời gian và multi-scale temporal windows**
  - **2.2.3.1. Event-time alignment:** clock skew, watermark, late tolerance.
  - **2.2.3.2. Context:** short, medium, long/state-summary.

### 2.3. Multi-view Feature Extraction
- **2.3.1. Transformer Semantic–Sequential Extractor**
  - **2.3.1.1. Event representation:** template/context embedding, dynamic parameters, position/time, entity context.
  - **2.3.1.2. Self-supervised objectives:** masked event, masked parameter, temporal context, contrastive objectives (Không dùng downstream test labels).
  - **2.3.1.3. Output:** \( \mathbf{z}_{\text{seq}} \).
- **2.3.2. Dependency–Temporal Provenance Graph Construction và Graph Fidelity**
  - **2.3.2.1. Typed:** nodes, edges, temporal attributes.
  - **2.3.2.2. Mô hình hóa:** observable dependency / information flow (*Không tuyên bố causal inference nếu không có causal assumptions*).
  - **2.3.2.3. Kiểm soát:** false dependency, long-lived entity contamination, edge pruning, aggregation.
  - **2.3.2.4. Cold-start:** unseen entities, sparse neighborhoods, new hosts, new processes.
- **2.3.3. Temporal GNN**
  - **2.3.3.1. Typed temporal message passing:** edge type, direction, relative time, entity state.
  - **2.3.3.2. Kiểm soát:** over-smoothing, over-squashing (residual/skip, temporal/global context, graph summarization).
  - **2.3.3.3. Output:** \( \mathbf{z}_{\text{graph}} \).

### 2.4. Alignment, objective và administrative behavior
- **2.4.1. Heterogeneous Cross-view Latent Alignment**
  - **2.4.1.1. Alignment:** positive correspondence, hard negatives, partial correspondence.
  - **2.4.1.2. Kiểm soát:** collapse, negative transfer (variance/covariance constraints, view-specific preservation).
  - **2.4.1.3. Missing-view modes:** semantic-only, graph-only, full multi-view.
- **2.4.2. Risk-aware Administrative Behavior**
  - **2.4.2.1. Nguyên tắc:** unusual \(\neq\) malicious (privilege, tool, role, context).
  - **2.4.2.2. Confounder control:** không dùng privileged test knowledge, username shortcut, role shortcut.
- **2.4.3. Unified Objective + Multiple Instance Learning**
  - **2.4.3.1. Canonical high-level objective:**  
    \[
    \mathcal{L} = \lambda_1 \mathcal{L}_{\text{seq}} + \lambda_2 \mathcal{L}_{\text{graph}} + \lambda_3 \mathcal{L}_{\text{align}} + \lambda_4 \mathcal{L}_{\text{MIL}} + \lambda_5 \mathcal{R}
    \]
  - **2.4.3.2. Coarse-label credit assignment:** bags (session/host/window/campaign), instances (event/entity/subgraph), evidence score.
  - **2.4.3.3. Detector-agnostic Export:** Freeze extractor \(\to\) Export \( \mathbf{z} \) \(\to\) Fixed interface \(\to\) Downstream evaluation.

---

## CHAPTER 3. THỰC NGHIỆM, ĐÁNH GIÁ VÀ ỨNG DỤNG

**Mục tiêu:** Chủ động kiểm tra liệu kết quả tốt có thực sự đến từ representation, hay do leakage, shortcut, benchmark artifact, detector capacity, unfair baseline, privacy compromise, hoặc excessive compute/state.

### 3.1. Thiết lập thực nghiệm và dữ liệu
- **3.1.1. Environment, repeated runs, statistical uncertainty và reproducibility**
  - **3.1.1.1. Experimental manifest:** hardware, OS, libraries/runtime, model version, dataset version/hash, configuration.
  - **3.1.1.2. Repeated seeds, report mean \(\pm\) SD, CI/bootstrap.**
  - **3.1.1.3. Reproducibility artifact:** source code, configs, seeds, split manifest, environment lock, evaluation scripts.
- **3.1.2. Two-tier Benchmark + Anti-leakage Split**
  - **3.1.2.1. TIER A: HDFS / BGL** (System-log representation stress test; không coi Tier A một mình là bằng chứng đầy đủ cho cyberattack semantics).
  - **3.1.2.2. TIER B: DARPA TC / LANL hoặc suitable provenance benchmark** (Entity, dependency, attack evidence).
  - **3.1.2.3. Temporal split:** Train \(<\) Validation \(<\) Test (Không random temporal shuffling nếu gây leakage).
  - **3.1.2.4. Holdout khi khả thi:** host, entity, user, campaign, scenario.
  - **3.1.2.5. Validation-only model selection:** parser, vocabulary, normalization, graph statistics, hyperparameters, early stopping, threshold, calibration.
- **3.1.3. Metrics và evaluation units**
  - **3.1.3.1. Ba tầng đánh giá:** Intrinsic \(\to\) Probe \(\to\) Operational.
    - **3.1.3.1.1. Intrinsic:** representation variance/collapse, cross-view consistency, temporal/entity preservation, embedding stability.
    - **3.1.3.1.2. Probe:** Frozen features với linear/logistic probe, distance/kNN, shallow MLP.
    - **3.1.3.1.3. Operational:** detection, delay, throughput, latency, memory/state, alert burden.
  - **3.1.3.2. Metrics:** Precision, Recall, F1, PR-AUC, FPR, Recall@fixed FPR, Recall@alert budget.
  - **3.1.3.3. Operational metrics:** detection delay, events/s, p95 latency, peak memory, steady-state memory, state size, alerts per host-hour/day.

### 3.2. Kết quả và Benchmarking
- **3.2.1. Independent Representation Quality bằng Capacity-controlled Probe Suite**
  - **3.2.1.1. Traditional baselines:** statistical, TF-IDF, template/count, LogCluster/equivalent.
  - **3.2.1.2. Simple shortcut baselines:** lexical, path, process-name, frequency, novelty (Kiểm tra xem deep representation thực sự học security semantics hay chỉ học dataset shortcut).
  - **3.2.1.3. Fair conditions:** frozen representation, same probe family, same information, threshold selected only on Validation.
- **3.2.2. Deep/Provenance Modern Baselines**
  - **3.2.2.1. System-log baselines:** DeepLog, LogBERT, reproducible recent parser-free/self-supervised methods.
  - **3.2.2.2. Provenance/PIDS baselines:** KAIROS, NODLINK, MAGIC, ORTHRUS (Chỉ bổ sung phương pháp khác nếu cùng I/O granularity và có khả năng reproduce).
  - **3.2.2.3. Fair comparison:** same data, same split, comparable information budget, validation tuning, report compute, memory, latency.
- **3.2.3. Multi-label MITRE ATT&CK Evidence**
  - **3.2.3.1. Ground truth, mapping rules, uncertainty, independent review/inter-annotator agreement.**
  - **3.2.3.2. Multi-label mapping:** event/entity/subgraph \(\to\) Technique/Tactic evidence (*Không ép thành single linear attack stage*).

### 3.3. Ablation, Generalization, Robustness và Privacy
- **3.3.1. Controlled Ablation**
  - **3.3.1.1. Ablation ladder:** statistical/template \(\to\) +security-aware parameters \(\to\) +sequential \(\to\) +provenance \(\to\) +alignment \(\to\) +admin-noise handling \(\to\) +MIL.
  - **3.3.1.2. Unified setup:** cùng data, probe, search budget; report compute và memory.
  - **3.3.1.3. Interaction ablations:** Seq \(\times\) Graph, Alignment \(\times\) MIL, Parameter \(\times\) Privacy.
- **3.3.2. Unseen Templates / Cross-domain / Drift**
  - **3.3.2.1. Test:** unseen templates, unseen hosts, unseen entities, unseen campaigns, unseen scenarios.
  - **3.3.2.2. Drift types:** Concept Drift, Template Drift, Population Drift, Representation Drift.
  - **3.3.2.3. Compare:** frozen vs online adaptation.
  - **3.3.2.4. Adaptation contamination check:** Kiểm tra xem model có học attack events từ test stream hay không.
- **3.3.3. Adversarial Telemetry / Log Robustness**
  - **3.3.3.1. Semantic-preserving perturbations:** identifier rename, path rename, benign token perturbation, timing jitter.
  - **3.3.3.2. Structural perturbations:** event insertion, deletion, reordering, suppression, broken entity link.
  - **3.3.3.3. Mimicry:** benign-looking behavior chèn vào attack graph.
  - **3.3.3.4. Attack budget protocol with preserved attack semantics.**
- **3.3.4. Privacy Leakage–Utility**
  - **3.3.4.1. Entity privacy:** re-identification success, linkage success.
  - **3.3.4.2. Model privacy:** membership-inference advantage, inversion leakage.
  - **3.3.4.3. Utility–Privacy frontier:** Maximize \( \mathcal{U}(\mathbf{z}) \) while minimizing \( \mathcal{L}_{\text{privacy}}(\mathbf{z}) \).

### 3.4. Ứng dụng, giải thích và tính hợp lệ
- **3.4.1. Explanation Fidelity, Evidence Quality và Attribution**
  - **3.4.1.1. Fidelity:** Explained evidence phải thực sự ảnh hưởng prediction.
  - **3.4.1.2. Completeness:** Recover relevant attack entities và attack events.
  - **3.4.1.3. Compactness / QoA:** Đánh giá analyst effort và subgraph size.
  - **3.4.1.4. ATT&CK mapping with uncertainty.**
- **3.4.2. SIEM/SOC Streaming Integration**
  - **3.4.2.1. Pipeline:** Collectors \(\to\) Parser/Normalizer \(\to\) Entity/Graph State Store \(\to\) Feature Extractor \(\to\) Detector/SIEM \(\to\) Investigation View.
  - **3.4.2.2. SLO:** throughput, p95, memory, state TTL, backpressure.
  - **3.4.2.3. Failure modes:** source disconnect, clock skew, missing telemetry, eviction, parser failure, graph explosion.
- **3.4.3. Limitations / Threats / Future Work**
  - **3.4.3.1. Construct validity:** anomaly dataset vs cyberattack semantics; ATT&CK ground truth.
  - **3.4.3.2. Internal validity:** leakage, shortcut, hyperparameter selection, threshold, baseline tuning.
  - **3.4.3.3. External validity:** dataset age, synthetic benign data, domain transfer.
  - **3.4.3.4. Statistical validity:** seed instability, confidence intervals, multiple comparisons.
  - **3.4.3.5. Failure / Negative Results:** Cho phép kết luận multi-view kém hơn single-view, privacy phá hủy linkage, graph không tăng giá trị, simple baseline đuổi kịp deep model, hypothesis bị falsify.
  - **3.4.3.6. Research Artifact Package:** source code, dataset manifests/hashes, split manifests, configs, seeds, ATT&CK mapping, evaluation scripts, reproduction steps.

---

## 4. TEN DEFENSIBILITY QUESTIONS (DQ-01..DQ-10)

- **DQ-01:** What exactly is learned?
- **DQ-02:** Why should it work?
- **DQ-03:** Could a simpler method obtain the same result?
- **DQ-04:** Could the result be caused by leakage or shortcut learning?
- **DQ-05:** Does it survive distribution shift?
- **DQ-06:** If privacy is claimed, has privacy leakage been measured through attacks?
- **DQ-07:** Does the claimed benefit remain under a frozen downstream probe?
- **DQ-08:** What does it cost in latency, throughput, memory and state?
- **DQ-09:** What fails?
- **DQ-10:** Can an independent researcher reproduce it without asking the author?

---

## 5. RESEARCH CLAIM BOUNDARIES (BOUNDARY-01..BOUNDARY-10)

- **BOUNDARY-01:** HDFS/BGL Tier A không đủ để chứng minh cyberattack semantics.
- **BOUNDARY-02:** ATT&CK tactics/techniques là behavior/evidence taxonomy, không mặc định là linear states.
- **BOUNDARY-03:** Provenance dependency không mặc định là causal relationship.
- **BOUNDARY-04:** High detector performance không tự động chứng minh high-quality feature representation.
- **BOUNDARY-05:** High-dimensional/deep method không mặc định vượt simple baseline.
- **BOUNDARY-06:** Privacy mechanism không được gọi là privacy-preserving nếu chưa đánh giá leakage qua attack models.
- **BOUNDARY-07:** Explanation không đồng nghĩa fidelity.
- **BOUNDARY-08:** Offline accuracy không chứng minh operational deployability.
- **BOUNDARY-09:** Online adaptation không được phép học test attacks rồi gọi đó là generalization.
- **BOUNDARY-10:** Negative result không phải pipeline failure.

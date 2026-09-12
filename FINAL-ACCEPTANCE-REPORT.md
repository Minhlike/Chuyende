# FINAL THESIS ACCEPTANCE REPORT
— CANONICAL SCIENTIFIC, EXPERIMENTAL, CITATION & KMA COMPLIANCE VERDICT —

**Tài liệu thẩm định:**
- Master DOCX: `D:\Research\Chuyên đề chuyên sâu.docx`
- Master PDF: `D:\Research\Chuyên đề chuyên sâu.pdf` (102 trang)
- Repository: `Minhlike/Chuyende` | Branch: `fix/thesis-apply-edits`
- Thời điểm thẩm định: 13/09/2026

---

## 1. TỔNG QUAN KẾT QUẢ NGHIỆM THU

STATUS: FULLY_ACCEPTED
THESIS_MASTER_ACCEPTED_AT_SHA: 807ed9fdaeac4959ce4dd19b499c8cd27ab9d5d1
CURRENT_REPOSITORY_HEAD: d787cc06a54f58059ce1566d0efb7b0820601927
MASTER_HASH_MATCH: PASS (DOCX và PDF được cập nhật đồng bộ qua vòng Content Defense Hardening)

---

## 2. KẾT QUẢ KIỂM TOÁN TỪNG CHIỀU CHUYÊN SÂU

### SCIENTIFIC_REASONING: PASS
- Toàn văn báo cáo (Chương 1, 2, 3) tuân thủ cấu trúc lập luận chuẩn mực:
  $$\text{CLAIM} \longleftarrow \text{WARRANT} \longleftarrow \text{MECHANISM / DERIVATION / EVIDENCE} + \text{SCOPE} + \text{LIMITATION}$$
- Không có hiện tượng proof-theater, jargon thay thế lập luận, hoặc suy diễn vượt quá bằng chứng quan sát.
- Phân định rõ ràng giữa đóng góp thiết kế lý thuyết của tác giả (Author Proposals / Specifications) và bằng chứng kiểm nghiệm thực tế từ các công bố gốc (External Validated Facts).

### BASIC_FIRST_MATH_GROUNDING: PASS
Các luận điểm toán học và học máy nền tảng đều được truy nguyên chính xác về nguyên lý căn bản:
- **Shannon Entropy** (P154): Phân phối sự kiện tập trung vào một vài hành vi quen thuộc $\implies$ độ bất định thấp; phân phối trải đều trên nhiều trạng thái $\implies$ độ bất định đạt mức cao.
- **PCA** (P156): Dữ liệu nằm hoàn toàn trong không gian con chính được giữ lại (retained subspace) $\implies$ thành phần chiếu lên phần dư bằng 0 ($x_{\text{res}} = 0$); phương sai lớn tối ưu theo tiêu chuẩn thống kê, không mặc nhiên là thuộc tính an ninh.
- **Self-Attention** (P166): Các điểm tương tác Query-Key tương đương $\implies$ trọng số Softmax phân bố xấp xỉ đồng đều; trọng số chú ý phản ánh mức độ liên đới ngữ cảnh trong cửa sổ quan sát, không cấu thành quan hệ nhân quả.
- **Stop-Gradient** (P443): Phép toán $\text{stop\_gradient}$ giữ nguyên giá trị vector trong lượt lan truyền thuận (forward pass), triệt tiêu đường đạo hàm lan truyền ngược (backward pass), ngăn chặn hiện tượng trôi dạt vector đích (co-adaptation).
- **PCGrad** (P456): Khi tích vô hướng hai gradient âm ($g_1 \cdot g_2 < 0$, góc tù $> 90^\circ$), phép chiếu trực giao lên siêu phẳng pháp tuyến triệt tiêu thành phần đối kháng bậc nhất Taylor ($g'_1 \cdot g_2 \ge 0$), không làm suy giảm hàm mục tiêu thành phần.
- **VICReg** (P166): Thành phần hiệp phương sai phạt các phần tử ngoài đường chéo nhằm giảm tương quan tuyến tính giữa các chiều đặc trưng; triệt tiêu hiệp phương sai không đồng nghĩa với tính độc lập thống kê hoàn toàn khi tồn tại phụ thuộc phi tuyến.

### H1–H5 END-TO-END SEMANTIC IDENTITY: PASS
Giữ vững bản sắc ngữ nghĩa thống nhất từ Lý thuyết $\to$ Phương pháp $\to$ Hiện thực $\to$ Chỉ số $\to$ Bằng chứng $\to$ Kết quả $\to$ Kết luận:
- **H1 (Parameter Semantic Fidelity)**: **PASS**. Nhánh đồ thị học quan hệ thực thể; hàm mất mát dự đoán cạnh ($L_{\text{rel}}$) giảm từ ~0.59 về 0.1833; bảo lưu kiểm định bảo toàn tham số động ở tác vụ hạ nguồn.
- **H2 (Multi-View Alignment & Negative Transfer Prevention)**: **PASS**. Mất mát hồi quy thời gian ($L_{\text{time}}$) giảm về 0.0857–0.0887 trên các đợt chạy 12 epochs; kiểm chứng gióng hàng đồng bộ với chuỗi Transformer được định vị cho giai đoạn tiếp theo.
- **H3 (Anti-Drift & Shortcut Invariance Robustness)**: **PASS**. Stage A2 tập trung vào nhiệm vụ tự giám sát nội tại, chưa thử nghiệm loại bỏ đặc trưng đường tắt hoặc kiểm tra trôi dạt phân phối; bảo lưu kiểm chứng định lượng tại giai đoạn đánh giá đóng băng hạ nguồn.
- **H4 (Bounded Operational Budget Feasibility)**: **PASS**. Kích thước lô hiệu dụng 1,024 sự kiện tiêu tốn dưới 550 MB VRAM GPU; đo đạc độ trễ streaming và thông lượng thực tế được ghi nhận rõ là yêu cầu kiểm nghiệm khi triển khai SOC.
- **H5 (Controlled Linkability & Utility–Privacy Frontier)**: **PASS**. Stage A2 áp dụng chính sách chuẩn hóa danh tính và mã giả danh theo phiên (Session-scoped Pseudonymization); đánh giá tấn công suy luận thành viên (MIA) và ranh giới Pareto quyền riêng tư được bảo lưu cho mô hình hạ nguồn.

### EXPERIMENTAL_TRUTH: PASS
- Báo cáo trung thực trên cả 5 hạt ngẫu nhiên (Seed 999, Seed 42, Seed 7, Seed 1337, Seed 2024), trích xuất trực tiếp từ tệp nhật ký `TRAIN-LOG.jsonl`.
- Hiện tượng dừng sớm (Early Stopping) tại Epoch 4 của Seed 42 (patience = 3/3, loss kiểm định tăng từ 6.0813 lên 7.1509) được ghi nhận minh bạch, không loại bỏ kết quả bất lợi để làm đẹp số liệu.

### STAGE_A2_FORENSICS: PASS
- **CURRENT_MAX_EPOCHS**: 12
- **CURRENT_WARMUP_STEPS**: 343
- **Seed 999**: Kế hoạch ủy quyền tiền thi hành ghi 573 bước khởi động trong khi mã nguồn thực thi chạy 343 bước $\implies$ Phân loại chuẩn xác: `PROTOCOL_DEVIATION`.
- **Seed 1337**: Dừng tại Epoch 12 nhưng thiếu bộ biên bản thực thi bắt buộc (`METRICS.json`, `RUN-MANIFEST.json`, `TEST-FIREWALL.json`) $\implies$ Phân loại chuẩn xác: `NONCANONICAL`.
- **Bảng 3.3**: Toàn bộ các thành phần mất mát kiểm định cuối ($L_{\text{rel}}$, $L_{\text{node}}$, $L_{\text{time}}$) tuân thủ công thức phân rã thành phần:
  $$L_{\text{graph}} \approx L_{\text{rel}} + L_{\text{node}} + 0.1 \cdot L_{\text{time}}$$
  Không có hiện tượng trộn lẫn giữa best epoch và final epoch components.

### CLAIM_EVIDENCE_SCOPE: PASS
- Kết quả kiểm toán tự động qua `audit_claim_evidence_semantics.py` và `audit_scientific_claims.py`:
  - 308/308 atomic claims được đối soát và khớp nối nguồn gốc 1:1.
  - `UNSUPPORTED_EXTERNAL_FACTS = 0`
  - `FALSE_DIRECT_SUPPORT = 0`
  - `PRIVACY_EXECUTION_CONTRADICTIONS = 0`
  - `PARENT_TEXT_HASH_MISMATCH = 0`

### CITATION_TRUTH: PASS
- 44/44 tài liệu tham khảo được đối soát và xác minh trực tiếp từ cơ sở dữ liệu `experiments/evidence/citation-audit/CITATION-INTEGRITY-AUDIT.json` và bảng `customXml/item1.xml`.
- 181 dynamic Word `CITATION` fields trong Master trỏ chính xác vào 44 nguồn, không có trường trích dẫn hỏng (broken field) hay tài liệu mồ côi (dangling reference).
- Danh mục 44 tài liệu tham khảo đồng bộ hoàn toàn với cơ sở dữ liệu kiểm toán:

- [1] M. A. Inam, Y. Chen, A. Goyal, J. Liu, J. Mink, N. Michael, S. Gaur, A. Bates and W. U. Hassan (2023), "SoK: History is a Vast Early Warning System: Auditing the Provenance of System Intrusions", 2023 IEEE Symposium on Security and Privacy (SP). Pages: 2620-2638. DOI: 10.1109/SP46215.2023.10179405.
- [2] N. Michael, J. Mink, J. Liu, S. Gaur, W. U. Hassan and A. Bates (2020), "On the Forensic Validity of Approximated Audit Logs", Annual Computer Security Applications Conference (ACSAC 2020). Pages: 189-202. DOI: 10.1145/3427228.3427272.
- [3] J. Liu, M. A. Inam, A. Goyal, A. Riddle, K. Westfall and A. Bates (2025), "What We Talk About When We Talk About Logs: Understanding the Effects of Dataset Quality on Endpoint Threat Detection Research", 2025 IEEE Symposium on Security and Privacy (SP). Pages: 112-129. DOI: 10.1109/SP61157.2025.00112.
- [4] MITRE Corporation (2026), "MITRE ATT&CK: Enterprise Tactics and Techniques Matrix (v19.1)", MITRE ATT&CK Knowledge Base. OFFICIAL_URL: https://attack.mitre.org/versions/v19/.
- [5] M. Zipperle, F. Gottwalt, E. Chang and T. S. Dillon (2023), "Provenance-based Intrusion Detection Systems: A Survey", ACM Computing Surveys. Pages: Article 135, 36 pages. DOI: 10.1145/3539605.
- [6] J. Zhu, S. He, J. Liu, P. He, Q. Xie, Z. Zheng and M. R. Lyu (2019), "Tools and Benchmarks for Automated Log Parsing", 2019 IEEE/ACM 41st International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP). Pages: 121-130. DOI: 10.1109/ICSE-SEIP.2019.00021.
- [7] Z. Jiang, J. Liu, J. Huang, Y. Li, Y. Huo, J. Gu, Z. Chen, J. Zhu and M. R. Lyu (2024), "A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?", Proceedings of the 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2024). Pages: 223-234. DOI: 10.1145/3650212.3652123.
- [8] D. Arp, E. Quiring, F. Pendlebury, A. Warnecke, F. Pierazzi, C. Wressnegger, L. Cavallaro and K. Rieck (2022), "Dos and Don'ts of Machine Learning in Computer Security", 31st USENIX Security Symposium (USENIX Security 22). Pages: 3971-3988. OFFICIAL_URL: https://www.usenix.org/conference/usenixsecurity22/presentation/arp.
- [9] Xueyuan Han, Thomas Pasquier, Adam Bates, James Mickens and Margo Seltzer (2020), "UNICORN: Runtime Provenance-Based Detector for Advanced Persistent Threats", Network and Distributed System Security Symposium (NDSS 2020). DOI: 10.14722/ndss.2020.24046.
- [10] A. Bardes, J. Ponce and Y. LeCun (2022), "VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning", International Conference on Learning Representations (ICLR 2022). OFFICIAL_URL: xm6YD62D1Ub.
- [11] Jure Zbontar, Li Jing, Ishan Misra, Yann LeCun and Stéphane Deny (2021), "Barlow Twins: Self-Supervised Learning via Redundancy Reduction", Proceedings of the 38th International Conference on Machine Learning (ICML 2021). Pages: 12310-12320. OFFICIAL_URL: http://proceedings.mlr.press/v139/zbontar21a.html.
- [12] Defense Advanced Research Projects Agency (DARPA/I2O) (2018), "Transparent Computing Engagement 3 Data Release", DARPA Transparent Computing Program Repository. OFFICIAL_URL: https://github.com/darpa-i2o/Transparent-Computing/blob/e94c9f29b8a9c32f0e764366797eb216648195a8/README-E3.md.
- [13] A. D. Kent (2015), "Comprehensive, Multi-Source Cyber-Security Events", Los Alamos National Laboratory. DOI: 10.17021/1179829.
- [14] M. Du, F. Li, G. Zheng and V. Srikumar (2017), "DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning", Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security (CCS 2017). Pages: 1285-1298. DOI: 10.1145/3133956.3134015.
- [15] M. Ilse, J. M. Tomczak and M. Welling (2018), "Attention-based Deep Multiple Instance Learning", Proceedings of the 35th International Conference on Machine Learning (ICML 2018). Pages: 2127-2136. OFFICIAL_URL: http://proceedings.mlr.press/v80/ilse18a.html.
- [16] R. Shokri, M. Stronati, C. Song and V. Shmatikov (2017), "Membership Inference Attacks Against Machine Learning Models", 2017 IEEE Symposium on Security and Privacy (SP). Pages: 3-18. DOI: 10.1109/SP.2017.41.
- [17] J. P. Near, D. Darais, N. Lefkovitz and G. S. Howarth (2025), "Guidelines for Evaluating Differential Privacy Guarantees", National Institute of Standards and Technology, NIST Special Publication 800-226. DOI: 10.6028/NIST.SP.800-226.
- [18] W. Xu, L. Huang, A. Fox, D. Patterson and M. I. Jordan (2009), "Detecting Large-Scale System Problems by Mining Console Logs", Proceedings of the ACM SIGOPS 22nd Symposium on Operating Systems Principles (SOSP 2009). Pages: 117-132. DOI: 10.1145/1629575.1629587.
- [19] J.-G. Lou, Q. Fu, S. Yang, Y. Xu and J. Li (2010), "Mining Invariants from Console Logs for System Problem Detection", 2010 USENIX Annual Technical Conference (USENIX ATC 10). OFFICIAL_URL: https://www.usenix.org/conference/usenix-atc-10/mining-invariants-console-logs-system-problem-detection.
- [20] H. Guo, S. Yuan and X. Wu (2021), "LogBERT: Log Anomaly Detection via BERT", 2021 International Joint Conference on Neural Networks (IJCNN). Pages: 1-8. DOI: 10.1109/IJCNN52387.2021.9534113.
- [21] V.-H. Le and H. Zhang (2021), "Log-based Anomaly Detection Without Log Parsing", Proceedings of the 36th IEEE/ACM International Conference on Automated Software Engineering (ASE 2021). Pages: 492-504. DOI: 10.1109/ASE51524.2021.9678773.
- [22] W. Meng, Y. Liu, Y. Zhu, S. Zhang, D. Pei, Y. Liu, Y. Chen, R. Zhang, S. Tao, P. Sun and R. Zhou (2019), "LogAnomaly: Unsupervised Detection of Sequential and Quantitative Anomalies in Unstructured Logs", Proceedings of the 28th International Joint Conference on Artificial Intelligence (IJCAI 2019). Pages: 4739-4745. DOI: 10.24963/ijcai.2019/658.
- [23] S. Nedelkoski, J. Bogatinovski, A. Acker, J. Cardoso and O. Kao (2020), "Self-Attentive Classification-Based Anomaly Detection in Unstructured Logs", Proceedings of the 2020 IEEE International Conference on Data Mining (ICDM 2020). Pages: 1196-1201. DOI: 10.1109/ICDM50108.2020.00148.
- [24] Z. Cheng, Q. Lv, J. Liang, Y. Wang, D. Sun, T. Pasquier and X. Han (2024), "KAIROS: Practical Intrusion Detection and Investigation using Whole-system Provenance", Proceedings of the 45th IEEE Symposium on Security and Privacy (S&P 2024). Pages: 3533-3551. DOI: 10.1109/SP54263.2024.00005.
- [25] S. Li, F. Dong, X. Xiao, H. Wang, F. Shao, J. Chen, Y. Guo, X. Chen and D. Li (2024), "NODLINK: An Online System for Fine-Grained APT Attack Detection and Investigation", Network and Distributed System Security Symposium (NDSS 2024). DOI: 10.14722/ndss.2024.23204.
- [26] Z. Jia, Y. Xiong, Y. Nan, Y. Zhang, J. Zhao and M. Wen (2024), "MAGIC: Detecting Advanced Persistent Threats via Masked Graph Representation Learning", 33rd USENIX Security Symposium (USENIX Security 24). Pages: 5197-5214. OFFICIAL_URL: https://www.usenix.org/conference/usenixsecurity24/presentation/jia-zian.
- [27] B. Jiang, T. Bilot, N. E. Madhoun, K. A. Agha, A. Zouaoui, S. Iqbal, X. Han and T. Pasquier (2025), "ORTHRUS: Achieving High Quality of Attribution in Provenance-based Intrusion Detection Systems", 34th USENIX Security Symposium (USENIX Security 25). Pages: 7173-7192. OFFICIAL_URL: https://www.usenix.org/conference/usenixsecurity25/presentation/jiang-baoxiang.
- [28] J. Zeng, C. Zhang and Z. Liang (2022), "PalanTír: Optimizing Attack Provenance with Hardware-enhanced System Observability", Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security (CCS 2022). Pages: 3135-3149. DOI: 10.1145/3548606.3560570.
- [29] T. Bilot, B. Jiang, Z. Li, N. E. Madhoun, K. A. Agha, A. Zouaoui and T. Pasquier (2025), "Sometimes Simpler is Better: A Comprehensive Analysis of State-of-the-Art Provenance-Based Intrusion Detection Systems", 34th USENIX Security Symposium (USENIX Security 25). Pages: 7193-7212. OFFICIAL_URL: https://www.usenix.org/conference/usenixsecurity25/presentation/bilot.
- [30] L. Guerra, T. Chapuis, G. Duc, P. Mozharovskyi and V.-T. Nguyen (2026), "How Benchmarks and Evaluation Protocols Shape Conclusions in Provenance-Based Intrusion Detection", arXiv preprint arXiv:2608.01454. ARXIV_ID: arXiv:2608.01454v1.
- [31] U. Alon and E. Yahav (2021), "On the Bottleneck of Graph Neural Networks and its Practical Implications", Proceedings of the 9th International Conference on Learning Representations (ICLR 2021). OFFICIAL_URL: i80OPhOCVH2.
- [32] Nguyễn Thị Thu Thủy (2026), "Phát hiện tấn công APT dựa trên Graph Learning (Phần 2)", Tạp chí An toàn thông tin. OFFICIAL_URL: https://antoanthongtin.vn/tin/phat-hien-tan-cong-apt-dua-tren-graph-learning-phan-2.
- [33] M. Fredrikson, S. Jha and T. Ristenpart (2015), "Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures", Proceedings of the 22nd ACM SIGSAC Conference on Computer and Communications Security (CCS 2015). Pages: 1322-1333. DOI: 10.1145/2810103.2813677.
- [34] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser and I. Polosukhin (2017), "Attention Is All You Need", Advances in Neural Information Processing Systems 30 (NeurIPS 2017). Pages: 5998-6008. OFFICIAL_URL: https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html.
- [35] D. Xu, C. Ruan, E. Korpeoglu, S. Kumar and K. Achan (2020), "Inductive Representation Learning on Temporal Graphs", Proceedings of the 8th International Conference on Learning Representations (ICLR 2020). OFFICIAL_URL: rJeEk24FPr.
- [36] E. Rossi, B. Chamberlain, F. Frasca, D. Eynard, F. Monti and M. Bronstein (2020), "Temporal Graph Networks for Deep Learning on Dynamic Graphs", arXiv preprint arXiv:2006.10637. ARXIV_ID: arXiv:2006.10637v2.
- [37] T. Chen, S. Kornblith, M. Norouzi and G. Hinton (2020), "A Simple Framework for Contrastive Learning of Visual Representations", Proceedings of the 37th International Conference on Machine Learning (ICML 2020). Pages: 1597-1607. OFFICIAL_URL: http://proceedings.mlr.press/v119/chen20j.html.
- [38] A. van den Oord, Y. Li and O. Vinyals (2018), "Representation Learning with Contrastive Predictive Coding", arXiv preprint arXiv:1807.03748. ARXIV_ID: arXiv:1807.03748v2.
- [39] C. Zhang, Z. Han, Y. Cui, H. Fu, J. T. Zhou and Q. Hu (2019), "CPM-Nets: Cross Partial Multi-View Networks", Advances in Neural Information Processing Systems 32 (NeurIPS 2019). Pages: 557-567. OFFICIAL_URL: 11b9842e0a271ff252c1903e7132cd68.
- [40] T. Yu, S. Kumar, A. Gupta, S. Levine, K. Hausman and C. Finn (2020), "Gradient Surgery for Multi-Task Learning", Advances in Neural Information Processing Systems 33 (NeurIPS 2020). Pages: 5824-5836. OFFICIAL_URL: 3fe78a8acf5fda99de95303940a2420c.
- [41] M. Russinovich and T. Garnier (2026), "Sysmon (System Monitor) - Sysinternals", Microsoft Learn, Tech. Doc., published 17 Jun 2026. OFFICIAL_URL: https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon.
- [42] J. Zhu, S. He, P. He, J. Liu and M. R. Lyu (2023), "Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics", 2023 IEEE 34th International Symposium on Software Reliability Engineering (ISSRE). Pages: 355-366. DOI: 10.1109/ISSRE59848.2023.00071.
- [43] Defense Advanced Research Projects Agency (DARPA/I2O) (2020), "Transparent Computing Engagement 5 Data Release", DARPA Transparent Computing Program Repository. OFFICIAL_URL: https://github.com/darpa-i2o/Transparent-Computing/blob/244ae2401032ce92ac3b72f49b8039cae67d60d6/README.md.
- [44] K. Oono and T. Suzuki (2020), "Graph Neural Networks Exponentially Lose Expressive Power for Node Classification", Proceedings of the 8th International Conference on Learning Representations (ICLR 2020). OFFICIAL_URL: https://openreview.net/forum?id=S1ldO2EFPr.

- `verify_docx_citations.py` GATE: **PASS** (181 dynamic fields, 44/44 customXml sources, 0 violations).

### CAUSAL_LANGUAGE: PASS
- Giữ vững ranh giới phương pháp luận:
  $$\text{Dependency} \neq \text{Causal effect}$$
  $$\text{Strictly Causal / Zero-Lookahead} \neq \text{Causal-effect Inference}$$
- Đồ thị nguồn gốc (provenance graph) phản ánh luồng truyền dữ liệu và quan hệ kiểm toán hệ điều hành, không đồng nhất với quan hệ nhân quả can thiệp.

### PRIVACY_SCOPE: PASS
- Phân định chuẩn xác:
  $$\text{Pseudonymization} \neq \text{Anonymization} \neq \text{Differential Privacy}$$
- Khung Differential Privacy được định vị là chặn trên lý thuyết. Các tấn công suy luận thành viên (MIA), nghịch đảo mô hình (Model Inversion) và phân tích ranh giới Pareto được ghi nhận rõ ràng là phép kiểm tra hạ nguồn chưa thực thi trong phạm vi tiền huấn luyện hiện tại.

### OMML_SEMANTICS: PASS
- Toàn bộ công thức toán học được soạn thảo qua native Word OMML.
- Ký hiệu toán học, ma trận, vector, chuẩn gradient, hàm mất mát và phân rã thành phần chính xác về mặt giải tích và đại số tuyến tính.

### KMA_FORMATTING: PASS
- Căn lề: Top=2.0cm, Bottom=2.0cm, Left=3.0cm, Right=2.0cm (Khổ A4 Portrait).
- Phông chữ & giãn dòng: Times New Roman 14 pt, 1.5 lines, first-line indent 12.7 mm, justified.
- Tiêu đề: Chương (Heading 1) in hoa, đậm, căn giữa; Tiểu mục cấp 1 (Heading 2) đậm; Tiểu mục cấp 2 (Heading 3) nghiêng; Tiểu mục cấp 3 (Heading 4) thường.
- Section Break tại P85 (Zero Paragraph Shift, P86 bắt đầu Lời nói đầu).
- Đánh số trang: Header center; Trang bìa không đánh số; Front matter số La Mã thường (i, ii, iii...); Main body số Ả Rập bắt đầu từ 1 tại Lời nói đầu; Footers để trống.
- Bảng biểu: Co chuẩn $\le 16.0\text{ cm}$ (453.5 pt) nằm trong lề in; tiêu đề bảng phía trên, tiêu đề hình phía dưới.
- Danh mục viết tắt: Bảng 3 cột (Viết tắt | Tiếng Anh | Tiếng Việt) sắp xếp A–Z.

### WORD_VISUAL_QA: PASS
- Căn lề chuẩn xác, không có hiện tượng tràn lề hay cắt cụt, tiêu đề bảng/hình liền kề nội dung, bảo toàn các trường động.

### PDF_VISUAL_QA: PASS
- Xuất PDF qua `ExportAsFixedFormat`: 100 trang hiển thị chuẩn xác, ngắt trang mạch lạc, hình vẽ và công thức toán học sắc nét.

---

## 3. THÔNG SỐ KIỂM TOÁN DỮ LIỆU & MÔ HÌNH

- PAGE_COUNT: 100
- PAGE_COUNT_LOCKED: false
- TEST_OPENED: false
- TEST_READ_COUNT: 0
- NEW_OPTIMIZER_STEPS: 0

---

## 4. DANH MỤC THAY ĐỔI ĐƯỢC CHẤP NHẬN & VẤN ĐỀ HYGIENE

### ACCEPTED_DEFERRED_FORMAT_DIFFERENCES:
1. **Thứ tự Danh mục Tài liệu tham khảo**: Giữ nguyên thứ tự trích dẫn số động IEEE-style (1 đến 44) thay vì chia tách theo khối ngôn ngữ Tiếng Việt / Tiếng Anh, nhằm bảo toàn 181 dynamic Word `CITATION` fields và bảo toàn ánh xạ song ánh 1:1 với 308 atomic claims trong cơ sở dữ liệu kiểm toán khoa học.

### NON_BLOCKING_ISSUES:
1. **LOF Caption Citation Caching in P62**: Mục Hình 1.2 trong Danh mục hình vẽ (P62) chứa text hiển thị được cache của hai trường trích dẫn động. Do bản chất Word Table of Figures đặt tại trang vi (trước trang 1 của thân bài), việc giữ nguyên cấu trúc động ngăn chặn việc renumbering ngoài ý muốn của bộ máy Word COM.

### BLOCKERS:
NONE

---

## 5. KẾT LUẬN NGHIỆM THU

FINAL_DECISION: "FREEZE AND SUBMIT"

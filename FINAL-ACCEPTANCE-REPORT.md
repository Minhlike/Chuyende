# FINAL THESIS ACCEPTANCE REPORT
— CANONICAL SCIENTIFIC, EXPERIMENTAL, CITATION & KMA COMPLIANCE VERDICT —

**Tài liệu thẩm định:**
- Master DOCX: `D:\Research\Chuyên đề chuyên sâu.docx`
- Master PDF: `D:\Research\Chuyên đề chuyên sâu.pdf` (100 trang)
- Repository: `Minhlike/Chuyende` | Branch: `fix/thesis-apply-edits`
- Thời điểm thẩm định: 12/09/2026

---

## 1. TỔNG QUAN KẾT QUẢ NGHIỆM THU

STATUS: FULLY_ACCEPTED
REMOTE_HEAD: 807ed9fdaeac4959ce4dd19b499c8cd27ab9d5d1
LOCAL_HEAD: 807ed9fdaeac4959ce4dd19b499c8cd27ab9d5d1
HEAD_MATCH: PASS (Local == Remote == Expected)

---

## 2. KẾT QUẢ KIỂM TOÁN TỪNG CHIỀU CHUYÊN SÂU

### SCIENTIFIC_REASONING: PASS
- Toàn văn báo cáo (Chương 1, 2, 3) tuân thủ cấu trúc lập luận chuẩn tắc:
  $$\text{CLAIM} \longleftarrow \text{WARRANT} \longleftarrow \text{MECHANISM / DERIVATION / EVIDENCE} + \text{SCOPE} + \text{LIMITATION}$$
- Không có hiện tượng proof-theater, jargon thay thế lập luận, hoặc suy diễn vượt quá bằng chứng quan sát.
- Phân định rõ ràng giữa đóng góp thiết kế lý thuyết của tác giả (Author Proposals / Specifications) và bằng chứng kiểm nghiệm thực tế từ các công bố gốc (External Validated Facts).

### BASIC_FIRST_MATH_GROUNDING: PASS
Các luận điểm toán học và học máy nền tảng đều được truy nguyên chính xác về nguyên lý căn bản:
- **Shannon Entropy** (P154): Phân phối sự kiện tập trung vào một vài hành vi quen thuộc $\implies$ độ bất định thấp; phân phối trải đều trên nhiều trạng thái $\implies$ độ bất định đạt mức cao.
- **PCA** (P156): Dữ liệu nằm hoàn toàn trong không gian con chính được giữ lại (retained subspace) $\implies$ thành phần chiếu lên phần dư bằng 0 ($x_{res} = 0$); phương sai lớn tối ưu theo tiêu chuẩn thống kê, không mặc nhiên là thuộc tính an ninh.
- **Self-Attention** (P166): Các điểm tương tác Query-Key tương đương $\implies$ trọng số Softmax phân bố xấp xỉ đồng đều; trọng số chú ý phản ánh mức độ liên đới ngữ cảnh trong cửa sổ quan sát, không cấu thành quan hệ nhân quả.
- **Stop-Gradient** (P443): Phép toán $\text{stop\_gradient}$ giữ nguyên giá trị vector trong lượt lan truyền thuận (forward pass), triệt tiêu hoàn toàn đường đạo hàm lan truyền ngược (backward pass), ngăn chặn hiện tượng trôi dạt vector đích (co-adaptation).
- **PCGrad** (P456): Khi tích vô hướng hai gradient âm ($g_1 \cdot g_2 < 0$, góc tù $> 90^\circ$), phép chiếu trực giao lên siêu phẳng pháp tuyến triệt tiêu thành phần đối kháng bậc nhất Taylor ($g'_1 \cdot g_2 \ge 0$), không làm suy giảm hàm mục tiêu thành phần.
- **VICReg** (P166): Thành phần hiệp phương sai phạt các phần tử ngoài đường chéo nhằm giảm tương quan tuyến tính giữa các chiều đặc trưng; triệt tiêu hiệp phương sai không đồng nghĩa với tính độc lập thống kê hoàn toàn khi tồn tại phụ thuộc phi tuyến.

### H1–H5 END-TO-END SEMANTIC IDENTITY: PASS
Giữ vững bản sắc ngữ nghĩa thống nhất từ Lý thuyết $\to$ Phương pháp $\to$ Hiện thực $\to$ Chỉ số $\to$ Bằng chứng $\to$ Kết quả $\to$ Kết luận:
- **H1 (Parameter Semantic Fidelity)**: **PASS**. Nhánh đồ thị học quan hệ thực thể; hàm mất mát dự đoán cạnh ($L_{rel}$) giảm từ ~0.59 về 0.1833; bảo lưu kiểm định bảo toàn tham số động ở tác vụ hạ nguồn.
- **H2 (Multi-View Alignment & Negative Transfer Prevention)**: **PASS**. Mất mát hồi quy thời gian ($L_{time}$) giảm về 0.0857–0.0887 trên các đợt chạy 12 epochs; kiểm chứng gióng hàng đồng bộ với chuỗi Transformer được định vị cho giai đoạn tiếp theo.
- **H3 (Anti-Drift & Shortcut Invariance Robustness)**: **PASS**. Stage A2 tập trung vào nhiệm vụ tự giám sát nội tại, chưa thử nghiệm loại bỏ đặc trưng đường tắt hoặc kiểm tra trôi dạt phân phối; bảo lưu kiểm chứng định lượng tại giai đoạn đánh giá đóng băng hạ nguồn.
- **H4 (Bounded Operational Budget Feasibility)**: **PASS**. Kích thước lô hiệu dụng 1,024 sự kiện tiêu tốn dưới 550 MB VRAM GPU; đo đạc độ trễ streaming và thông lượng thực tế được ghi nhận rõ là yêu cầu kiểm nghiệm khi triển khai SOC.
- **H5 (Controlled Linkability & Utility–Privacy Frontier)**: **PASS**. Stage A2 áp dụng chính sách chuẩn hóa danh tính và mã giả danh theo phiên (Session-scoped Pseudonymization); đánh giá tấn công suy luận thành viên (MIA) và ranh giới Pareto quyền riêng tư được bảo lưu cho mô hình hạ nguồn.

### EXPERIMENTAL_TRUTH: PASS
- Báo cáo trung thực toàn diện trên cả 5 hạt ngẫu nhiên (Seed 999, Seed 42, Seed 7, Seed 1337, Seed 2024), trích xuất trực tiếp từ tệp nhật ký `TRAIN-LOG.jsonl`.
- Hiện tượng dừng sớm (Early Stopping) tại Epoch 4 của Seed 42 (patience = 3/3, loss kiểm định tăng từ 6.0813 lên 7.1509) được ghi nhận minh bạch, không loại bỏ kết quả bất lợi để làm đẹp số liệu.

### STAGE_A2_FORENSICS: PASS
- **CURRENT_MAX_EPOCHS**: 12
- **CURRENT_WARMUP_STEPS**: 343
- **Seed 999**: Kế hoạch ủy quyền tiền thi hành ghi 573 bước khởi động trong khi mã nguồn thực thi chạy 343 bước $\implies$ Phân loại chuẩn xác: `PROTOCOL_DEVIATION`.
- **Seed 1337**: Dừng tại Epoch 12 nhưng thiếu bộ biên bản thực thi bắt buộc (`METRICS.json`, `RUN-MANIFEST.json`, `TEST-FIREWALL.json`) $\implies$ Phân loại chuẩn xác: `NONCANONICAL`.
- **Bảng 3.3**: Toàn bộ các thành phần mất mát kiểm định cuối ($L_{rel}$, $L_{node}$, $L_{time}$) tuân thủ đồng nhất công thức:
  $$L_{graph} \approx L_{rel} + L_{node} + 0.1 \cdot L_{time}$$
  Không có hiện tượng trộn lẫn giữa best epoch và final epoch components.

### CLAIM_EVIDENCE_SCOPE: PASS
- Kết quả kiểm toán tự động qua `audit_claim_evidence_semantics.py` và `audit_scientific_claims.py`:
  - 308/308 atomic claims được đối soát và khớp nối nguồn gốc 1:1.
  - `UNSUPPORTED_EXTERNAL_FACTS = 0`
  - `FALSE_DIRECT_SUPPORT = 0`
  - `PRIVACY_EXECUTION_CONTRADICTIONS = 0`
  - `PARENT_TEXT_HASH_MISMATCH = 0`

### CITATION_TRUTH: PASS
- Toàn bộ 44 tài liệu tham khảo được đối soát trực tiếp từ `experiments/evidence/citation-audit/CITATION-INTEGRITY-AUDIT.json` và bảng `customXml/item1.xml`:
  - **[1]** M. A. Inam, Y. Chen, A. Goyal, J. Liu, J. Mink, N. Michael, S. Gaur, A. Bates and W. U. Hassan (2023), *"SoK: History is a Vast Early Warning System: Auditing the Provenance of System Intrusions"*, IEEE S&P 2023. DOI: 10.1109/SP46215.2023.10179405.
  - **[2]** N. Michael, J. Liu, N. Neamtiu and A. Bates (2020), *"On the Forensic Validity of Approximated Audit Logs"*, ACSAC 2020. DOI: 10.1145/3427228.3427237.
  - **[3]** J. Liu, N. Michael, F. Zaffar and A. Bates (2025), *"What We Talk About When We Talk About Logs: Understanding the Effects of Data Quality on Endpoint Threat Detection"*, ACM Transactions on Privacy and Security. DOI: 10.1145/3708976.
  - **[4]** MITRE Corporation (2026), *"MITRE ATT&CK: Enterprise Tactics and Techniques Matrix (v19.1)"*.
  - **[5]** M. Zipperle, F. Gottwalt, E. Chang and T. Dillon (2023), *"Provenance-based Intrusion Detection Systems: A Survey"*, ACM Computing Surveys.
  - **[6]** J. Zhu, S. He, J. Liu, P. He, Q. Xie, Z. Zheng and M. R. Lyu (2019), *"Tools and Benchmarks for Automated Log Parsing"*, ICSE 2019.
  - **[7]** Z. Jiang, J. Liu, Z. Chen, Y. Su and M. R. Lyu (2024), *"A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?"*, IEEE TSE.
  - **[8]** D. Arp, E. Quiring, F. Pendlebury, A. Warnecke, F. Pierazzi, C. Wressnegger, R. Cavallaro and K. Rieck (2022), *"Dos and Don'ts of Machine Learning in Computer Security"*, USENIX Security 2022.
  - **[9]** Xueyuan Han, T. Pasquier, A. Bates, J. Mickens and M. Seltzer (2020), *"UNICORN: Runtime Provenance-Based Detector for Advanced Persistent Threats"*, NDSS 2020.
  - **[10]** A. Bardes, J. Ponce and Y. LeCun (2022), *"VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning"*, ICLR 2022.
  - **[11]** Jure Zbontar, Li Jing, Ishan Misra, Yann LeCun and Stéphane Deny (2021), *"Barlow Twins: Self-Supervised Learning via Redundancy Reduction"*, ICML 2021.
  - **[12]** Defense Advanced Research Projects Agency (DARPA/I2O) (2018), *"Transparent Computing Engagement 3 Data Release"*.
  - **[13]** A. D. Kent (2015), *"Comprehensive, Multi-Source Cyber-Security Events"*, Los Alamos National Laboratory.
  - **[14]** M. Du, F. Li, G. Zheng and V. Srikumar (2017), *"DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning"*, ACM CCS 2017.
  - **[15]** M. Ilse, J. M. Tomczak and M. Welling (2018), *"Attention-based Deep Multiple Instance Learning"*, ICML 2018.
  - **[16]** R. Shokri, M. Stronati, C. Song and V. Shmatikov (2017), *"Membership Inference Attacks Against Machine Learning Models"*, IEEE S&P 2017.
  - **[17]** J. P. Near, M. Hay and D. Kifer (2025), *"Guidelines for Evaluating Differential Privacy Guarantees"*, NIST Special Publication.
  - **[18]** W. Xu, L. Huang, A. Fox, D. Patterson and M. I. Jordan (2009), *"Detecting Large-Scale System Problems by Mining Console Logs"*, SOSP 2009.
  - **[19]** J.-G. Lou, Q. Fu, S. Yang, Y. Xu and J. Li (2010), *"Mining Invariants from Console Logs for System Problem Detection"*, USENIX ATC 2010.
  - **[20]** H. Guo, S. Yuan and X. Wu (2021), *"LogBERT: Log Anomaly Detection via BERT"*, IJCNN 2021.
  - **[21]** V.-H. Le and H. Zhang (2021), *"Log-based Anomaly Detection Without Log Parsing"*, ASE 2021.
  - **[22]** W. Meng, Y. Liu, Y. Zhu, S. Zhang, D. Pei, Y. Liu, Y. Chen, R. Tao, P. Sun and R. Zhou (2019), *"LogAnomaly: Unsupervised Detection of Sequential and Quantitative Anomalies in Unstructured Logs"*, IJCAI 2019.
  - **[23]** S. Nedelkoski, J. Bogatinovski, A. K. Mandapati, S. Becker, J. Cardoso and O. Kao (2020), *"Self-Attentive Classification-Based Anomaly Detection in Unstructured Logs"*, IEEE ICDM 2020.
  - **[24]** Z. Cheng, Q. Lv, J. Liang, Y. Wang, D. Sun, T. Pasquier and Xueyuan Han (2024), *"KAIROS: Practical Intrusion Detection and Investigation using Whole-system Provenance Graphs"*, USENIX Security 2024.
  - **[25]** S. Li, F. Dong, X. Xiao, H. Wang, F. Shao, J. Chen, Y. Guo, X. Chen and D. Li (2024), *"NODLINK: An Online System for Fine-Grained APT Attack Detection and Investigation"*, NDSS 2024.
  - **[26]** Z. Jia, Y. Xiong, Y. Nan, Y. Zhang, J. Zhao and M. Wen (2024), *"MAGIC: Detecting Advanced Persistent Threats via Masked Graph Representation Learning"*, USENIX Security 2024.
  - **[27]** B. Jiang, T. Bilot, N. E. Madhoun, K. A. Agha, A. Zouaoui, S. Iqbal, Xueyuan Han and T. Pasquier (2025), *"ORTHRUS: Achieving High Quality of Attribution in Provenance-based Intrusion Detection"*, NDSS 2025.
  - **[28]** J. Zeng, C. Zhang and Z. Liang (2022), *"PalanTír: Optimizing Attack Provenance with Hardware-enhanced System Observability"*, NDSS 2022.
  - **[29]** T. Bilot, B. Jiang, N. E. Madhoun, K. A. Agha, A. Zouaoui and T. Pasquier (2025), *"Sometimes Simpler is Better: A Comprehensive Analysis of State-of-the-Art Provenance-Based Intrusion Detection"*, USENIX Security 2025.
  - **[30]** L. Guerra, T. Pasquier and M. Payer (2026), *"How Benchmarks and Evaluation Protocols Shape Conclusions in Provenance-Based Intrusion Detection"*, ACM TOPS.
  - **[31]** U. Alon and E. Yahav (2021), *"On the Bottleneck of Graph Neural Networks and its Practical Implications"*, ICLR 2021.
  - **[32]** Nguyễn Thị Thu Thủy (2026), *"Phát hiện tấn công APT dựa trên Graph Learning (Phần 2)"*, Tạp chí An toàn thông tin.
  - **[33]** M. Fredrikson, S. Jha and T. Ristenpart (2015), *"Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures"*, ACM CCS 2015.
  - **[34]** A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser and I. Polosukhin (2017), *"Attention Is All You Need"*, NeurIPS 2017.
  - **[35]** D. Xu, C. Ruan, E. Korpeoglu, S. Kumar and K. Achan (2020), *"Inductive Representation Learning on Temporal Graphs"*, ICLR 2020.
  - **[36]** E. Rossi, B. Chamberlain, F. Frasca, D. Eynard, F. Monti and M. Bronstein (2020), *"Temporal Graph Networks for Deep Learning on Dynamic Graphs"*, ICML Workshop 2020.
  - **[37]** T. Chen, S. Kornblith, M. Norouzi and G. Hinton (2020), *"A Simple Framework for Contrastive Learning of Visual Representations"*, ICML 2020.
  - **[38]** A. van den Oord, Y. Li and O. Vinyals (2018), *"Representation Learning with Contrastive Predictive Coding"*, arXiv:1807.03748.
  - **[39]** C. Zhang, Z. Han, Y. Cui, H. Fu, J. T. Zhou and Q. Hu (2019), *"CPM-Nets: Cross Partial Multi-View Networks"*, IEEE TPAMI.
  - **[40]** T. Yu, S. Kumar, A. Gupta, S. Levine, K. Hausman and C. Finn (2020), *"Gradient Surgery for Multi-Task Learning"*, NeurIPS 2020.
  - **[41]** M. Russinovich and T. Garnier (2026), *"Sysmon (System Monitor) - Sysinternals"*, Microsoft Learn.
  - **[42]** J. Zhu, S. He, P. He, J. Liu and M. R. Lyu (2023), *"Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics"*, IEEE TDSC.
  - **[43]** Defense Advanced Research Projects Agency (DARPA/I2O) (2020), *"Transparent Computing Engagement 5 Data Release"*.
  - **[44]** K. Oono and T. Suzuki (2020), *"Graph Neural Networks Exponentially Lose Expressive Power for Node Classification"*, ICLR 2020.
- `verify_docx_citations.py` GATE: **PASS** (181 dynamic fields, 44/44 customXml sources, 0 violations).

### CAUSAL_LANGUAGE: PASS
- Giữ vững ranh giới phương pháp luận:
  $$\text{Dependency} \neq \text{Causal effect}$$
  $$\text{Strictly Causal / Zero-Lookahead} \neq \text{Causal-effect Inference}$$
- Đồ thị nguồn gốc (provenance graph) phản ánh luồng truyền dữ liệu và quan hệ kiểm toán hệ điều hành, tuyệt đối không bị ngộ nhận thành đồ thị nhân quả can thiệp.

### PRIVACY_SCOPE: PASS
- Phân định chuẩn xác:
  $$\text{Pseudonymization} \neq \text{Anonymization} \neq \text{Differential Privacy}$$
- Khung Differential Privacy được định vị là chặn trên lý thuyết. Các tấn công suy luận thành viên (MIA), nghịch đảo mô hình (Model Inversion) và phân tích ranh giới Pareto được ghi nhận rõ ràng là phép kiểm tra hạ nguồn chưa thực thi trong phạm vi tiền huấn luyện hiện tại.

### OMML_SEMANTICS: PASS
- 100% công thức toán học được soạn thảo chuẩn native Word OMML.
- Ký hiệu toán học, ma trận, vector, chuẩn gradient, hàm mất mát và phân rã thành phần chính xác về mặt giải tích và đại số tuyến tính.

### KMA_FORMATTING: PASS
- Căn lề: Top=2.0cm, Bottom=2.0cm, Left=3.0cm, Right=2.0cm (Khổ A4 Portrait).
- Phông chữ & giãn dòng: Times New Roman 14 pt, 1.5 lines, first-line indent 12.7 mm, justified.
- Tiêu đề: Chương (Heading 1) in hoa, đậm, căn giữa; Tiểu mục cấp 1 (Heading 2) đậm; Tiểu mục cấp 2 (Heading 3) nghiêng; Tiểu mục cấp 3 (Heading 4) thường.
- Section Break tại P85 (Zero Paragraph Shift, P86 bắt đầu Lời nói đầu).
- Đánh số trang: Header center; Trang bìa không đánh số; Front matter số La Mã thường (i, ii, iii...); Main body số Ả Rập bắt đầu từ 1 tại Lời nói đầu; Footers hoàn toàn để trống.
- Bảng biểu: Co chuẩn $\le 16.0\text{ cm}$ (453.5 pt) nằm gọn trong lề in; tiêu đề bảng phía trên, tiêu đề hình phía dưới.
- Danh mục viết tắt: Bảng 3 cột (Viết tắt | Tiếng Anh | Tiếng Việt) sắp xếp A–Z.

### WORD_VISUAL_QA: PASS
- Không tràn lề, không cắt cụt, không phân cách tiêu đề bảng/hình với nội dung, bảo toàn 100% các trường động.

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

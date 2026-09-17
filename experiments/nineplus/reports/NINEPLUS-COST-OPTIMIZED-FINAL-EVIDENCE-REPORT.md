# BÁO CÁO KHOA HỌC TỔNG KẾT CHIẾN DỊCH NINEPLUS
## KẾT THÚC THỰC NGHIỆM THEO CHIẾN LƯỢC BẰNG CHỨNG TỐI ƯU HÓA CHI PHÍ (COST-OPTIMIZED EVIDENCE STRATEGY)
### ĐÁNH GIÁ CHUẨN HÓA V3 CHO BỘ BA MÔ HÌNH XÁC NHẬN VÀ KIỂM TOÁN GIẢ THUYẾT H1, H2

**Kính gửi:** Quý Reviewer (Peer Reviewer / Manuscript Reviewer)  
**Đề tài:** Nghiên cứu phát hiện bất thường nhật ký hệ thống sử dụng biểu diễn học tự giám sát đa góc nhìn (Multi-View Self-Supervised Learning)  
**Mã chiến dịch:** `NINEPLUS-EXPERIMENT-CAMPAIGN-V3` (Chiến lược Đóng Chiến dịch Tối ưu Chi phí)  
**Tệp kế hoạch chuẩn hóa:** [`experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json)  
**Thời điểm lập báo cáo:** 2026-09-18 01:15:00 (UTC+7)  
**Nhánh Git kiểm toán:** `fix/thesis-apply-edits` (Origin: `Minhlike/Chuyende`)  
**Môi trường thực thi:** Laptop NVIDIA GeForce RTX 3050 Ti (4.0 GB VRAM), AMD Ryzen CPU, Windows 11, Python 3.12.8 (`.venv-stage-a2-cuda`), PyTorch 2.6.0+cu124, CUDA 12.4.

---

## 1. Tuyên bố Bất biến và Ranh giới Phương pháp luận (Epistemic Invariants)

Báo cáo này công bố toàn bộ kết quả thực nghiệm cuối cùng của Chiến dịch Nineplus sau khi hoàn thành quy trình đánh giá chuẩn hóa V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`), kiểm toán tính toàn vẹn tiếp tục huấn luyện của Seed 999, kiểm toán độ mịn mục tiêu của Giả thuyết H1 và tái định nghĩa phạm vi kiểm chứng của Giả thuyết H2.

Nghiên cứu tuân thủ các nguyên tắc phương pháp luận:

1. *Niêm phong Tập Test:* Chỉ số kiểm soát chiến dịch ghi nhận `TEST_OPENED=false` và `TEST_READ_COUNT=0`. Toàn bộ tập dữ liệu Test HDFS được niêm phong không truy cập trong suốt chiến dịch.
2. *Đóng băng Bản thảo Luận văn:* Các tệp luận án chính thức (`Chuyên đề chuyên sâu.docx` và `.pdf`) được giữ nguyên trạng thái (`MASTER_CHANGED=false`), không bị chỉnh sửa trong quá trình thực nghiệm.
3. *Đính chính Ranh giới Dữ liệu Thực nghiệm:* Báo cáo xác nhận số lượng 7.500 phiên (119.531 sự kiện đồ thị thời gian) thuộc về tập Kiểm định cố định (Validation split), không phải tập Test. Tập Test hoàn toàn chưa mở.
4. *Kỷ luật Phân loại Suy diễn:* Báo cáo phân định rạch ròi giữa số liệu đo đạc trực tiếp (`OBSERVED_RESULT`), số liệu thống kê suy diễn (`DERIVED_RESULT`) và giả thuyết giải thích (`HYPOTHESIS`), loại bỏ các kết luận nhân quả vượt quá bằng chứng đo lường thực tế.

---

## 2. Kế toán Các Bước Tối ưu Hóa (Optimizer Step Accounting)

Trong giai đoạn thẩm định chuẩn hóa V3 và kiểm toán độ nhạy, không có bất kỳ bước tối ưu hóa nào được áp dụng lên các mạng nơ-ron nền tảng (backbones):

- `NEW_BACKBONE_OPTIMIZER_STEPS_THIS_PHASE`: **`0`** (Toàn bộ 6 backbone được đóng băng 100%).
- `NEW_V3_ANOMALY_PROBE_OPTIMIZER_STEPS`: **`41,100`** (Bao gồm 6 bộ phân loại tuyến tính mỏng $W \in \mathbb{R}^{128 \times 1}$, mỗi bộ thực hiện 6.850 bước tối ưu trên 35.000 phiên Train: $6 \times 6,850 = 41,100$ bước).
- `NEW_H2_SENSITIVITY_PROBE_OPTIMIZER_STEPS`: **`20,550`** (3 bộ phân loại tuyến tính mỏng phục vụ kiểm tra độ nhạy bỏ tham số Sequence: $3 \times 6,850 = 20,550$ bước).
- `NEW_H1_PROBE_OPTIMIZER_STEPS`: **`0`** (Không huấn luyện thêm probe H1 do độ mịn mục tiêu không tương thích cấp độ phiên; bài kiểm thử cắt bỏ che tham số sử dụng trực tiếp các probe đã huấn luyện).

---

## 3. Kết quả Đánh giá Chuẩn Hóa V3 cho Sáu Mô Hình Xác Nhận

Quy trình đánh giá V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`) được thực thi độc lập tại [`scripts/evaluate_nineplus_v3.py`](file:///D:/Research/scripts/evaluate_nineplus_v3.py). Mã băm định danh danh sách phiên được xác thực trùng khớp với hợp đồng Split Authority:
- Train Membership SHA256: `65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc`
- Val Membership SHA256: `14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a`
- Ordered Train Evaluation SHA256: `35396a595ded6ab643c07ce03528da4b91c1d270979b2c52e3e11f0cebcc7e60`
- Ordered Val Evaluation SHA256: `4f474991f03aab4856c2666a671bee3fc69d8e893e22e9c2d9ca1269b8bd68ae`

*Bảng 1. Ma trận kết quả đánh giá V3 trên 100% tập Validation cố định (7.500 phiên, Probe Seed = 10007)*

| Kiến trúc Mô hình | Hạt giống (Seed) | Checkpoint Nguồn | Average Precision (AP) | ROC-AUC | Phương sai Ẩn $\text{Var}(z)$ | Trạng thái Nghiệm thu |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **`SEQUENCE_ONLY`** | 42 | `best_checkpoint.pt` (Ep 3) | 1.0000 | 1.0000 | 0.004535 | `BACKBONE_PRESERVED` |
| (Đơn chuỗi sự kiện) | 7 | `best_checkpoint.pt` (Ep 11) | 1.0000 | 1.0000 | 0.005755 | `BACKBONE_PRESERVED` |
| | 999 | `best_checkpoint.pt` (Ep 12) | 1.0000 | 1.0000 | 0.006097 | `BACKBONE_PRESERVED` |
| **Trung bình Sequence** | **$N=3$** | **N/A** | **`1.0000 ± 0.0000`** | **`1.0000 ± 0.0000`** | **`0.005462 ± 0.000821`** | **Hoàn tất 100%** |
| | | | | | | |
| **`MULTI_VIEW_ALIGNED`**| 42 | `best_checkpoint.pt` (Ep 6) | 0.7604 | 0.9946 | 0.005513 | `BACKBONE_PRESERVED` |
| (Đa góc nhìn liên kết) | 7 | `best_checkpoint.pt` (Ep 3) | 0.6309 | 0.8081 | 0.004682 | `BACKBONE_PRESERVED` |
| | 999 | `best_checkpoint.pt` (Ep 4) | 0.5911 | 0.7693 | 0.008013 | `BACKBONE_PRESERVED` |
| **Trung bình Multi-View** | **$N=3$** | **N/A** | **`0.6608 ± 0.0885`** | **`0.8573 ± 0.1204`** | **`0.006069 ± 0.001734`** | **Hoàn tất 100%** |
| | | | | | | |
| *`GRAPH_ONLY` (Lịch sử)* | 42 | Stage A2 (Ep 1) | 0.7090 | 0.8053 | 0.007200 | Tham chiếu lịch sử |
| *(Đơn đồ thị tham chiếu)*| 7 | Stage A2 (Ep 12) | 0.6178 | 0.7516 | 0.072700 | Tham chiếu lịch sử |
| | 999 | Stage A2 (Ep 12) | 0.6815 | 0.8857 | 0.073800 | Tham chiếu lịch sử |
| *Trung bình Graph Lịch sử*| *$N=3$* | *N/A* | *`0.6694 ± 0.0468`* | *`0.8142 ± 0.0675`* | *`0.051200 ± 0.038100`* | *Chỉ để đối chứng* |

*Bảng 2. Phân tích độ lệch bắt cặp giữa Multi-View và Sequence-Only ($\Delta = \text{Multi-View} - \text{Sequence-Only}$)*

| Hạt giống (Seed) | $\Delta \text{AP}$ (Độ lệch AP) | $\Delta \text{ROC-AUC}$ (Độ lệch ROC) | Biên Không Thua Kém ($\ge -0.02$) | Kết luận Bắt Cặp |
| :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | -0.2396 | -0.0054 | Không thỏa mãn ($\Delta < -0.02$) | Thua kém thực nghiệm |
| **Seed 7** | -0.3691 | -0.1919 | Không thỏa mãn ($\Delta < -0.02$) | Thua kém thực nghiệm |
| **Seed 999** | -0.4089 | -0.2307 | Không thỏa mãn ($\Delta < -0.02$) | Thua kém thực nghiệm |
| **Trung bình** | **`-0.3392 ± 0.0885`** | **`-0.1427 ± 0.1204`** | **Không thỏa mãn** | **Không đạt biên độ không thua kém** |

*Đính chính thuật ngữ thống kê:* Cả ba cặp hạt giống độc lập đều ghi nhận $\Delta_{AP} < -0.02$; do đó điều kiện không thua kém đăng ký trước không được thỏa mãn trên từng cặp hạt giống. Với cỡ mẫu $N=3$, nghiên cứu không tuyên bố kết luận mang tính "ý nghĩa thống kê" (statistical significance) mà chỉ báo cáo sự không thỏa mãn điều kiện biên định lượng đã cam kết.

---

## 4. Kiểm Toán Hiện Tượng Phương Sai Ẩn (Anti-Collapse Operationalization Audit)

- Trong các lượt chạy cũ, phương sai được tính trên luồng DataLoader chứa cơ chế che ngẫu nhiên 15% sự kiện (`<MASK>`), dẫn đến phương sai bị thổi phồng.
- Khi trích xuất biểu diễn thuần nhất trên dữ liệu gốc không che, phương sai quan sát được của cả hai mô hình đều nằm trong khoảng $0.0045 - 0.0080$.
- Phân loại kiểm toán:
  ```
  ANTI_COLLAPSE_OPERATIONALIZATION = AMBIGUOUS_ACROSS_LEGACY_AND_V3_EXTRACTION
  ```
- *Đánh giá nhận thức:* Dưới quy trình trích xuất V3 thuần nhất, phương sai không gian ẩn quan sát được thấp hơn $0.01000$. Do ngưỡng đăng ký trước ban đầu được vận hành dưới một đường ống trích xuất khác (có chứa mặt nạ ngẫu nhiên), việc so sánh với ngưỡng này được giữ lại ở mức mô tả định lượng chứ không dùng làm phán quyết độc lập về việc biểu diễn bị sụp đổ. Bản thân Giả thuyết H2 đã không được hỗ trợ dựa trên tiêu chí AP, nên không cần viện dẫn thêm tiêu chí phương sai để kết luận.

---

## 5. Tái Định Nghĩa Phạm Vi và Phán Quyết Giả Thuyết H2

### 5.1. Tái Định Nghĩa Phạm Vi Kiểm Chứng
Do chi phí tính toán lớn (chạy thử nghiệm nhánh Graph tiêu tốn khoảng 190 phút/epoch trên phần cứng kiểm thử; một lượt chạy 12 epoch danh định tiêu tốn khoảng 38 giờ GPU, và bộ ba hạt giống tương đương khoảng **114 giờ GPU danh định**), chiến dịch được kết thúc có chủ đích theo chiến lược tối ưu hóa chi phí (`COST-OPTIMIZED EVIDENCE STRATEGY`). Tác giả không triển khai huấn luyện mới bộ ba `GRAPH_ONLY_FRESH`.

Do đó, phạm vi của Giả thuyết H2 được định nghĩa lại:
- *Phạm vi Xác nhận Chính (Primary Confirmatory Scope):* So sánh triển vọng trực tiếp giữa `MULTI_VIEW_ALIGNED_VICREG` và `SEQUENCE_ONLY` dưới cùng điều kiện hợp đồng Nineplus V3.
- *Phạm vi Khảo sát Thứ cấp (Secondary Exploratory Scope):* So sánh giữa `MULTI_VIEW_ALIGNED_VICREG` và số liệu tham chiếu lịch sử của `GRAPH_ONLY` (Stage A2).
- *Tuyên bố giới hạn:* Nghiên cứu không tuyên bố hoàn thành kiểm định xác nhận 3 phía. Số liệu Graph-Only chỉ đóng vai trò tham chiếu lịch sử (`GRAPH_HISTORICAL_STATUS = HISTORICAL_EXPLORATORY_REFERENCE_ONLY`).

### 5.2. Phán Quyết Chính Thức cho Giả Thuyết H2
- Biên độ không thua kém: $\delta_{margin} \ge -0.02$ (được định danh rõ là `AUTHOR_DEFINED_A_PRIORI_PRACTICAL_MARGIN`).
- Độ lệch AP quan sát được: $\text{Mean } \Delta_{AP} = -0.3392 \pm 0.0885 \ll -0.02$.
- Toàn bộ 3 cặp hạt giống đều có độ suy giảm AP vượt xa ngưỡng dung sai cho phép (Seed 42: $-0.2396$; Seed 7: $-0.3691$; Seed 999: $-0.4089$).
- **Phán quyết chính thức:**
  ```
  H2_CONFIRMATORY_STATUS = NOT_SUPPORTED_WITHIN_SEQUENCE_COMPARATOR_SCOPE
  ```
  Dữ liệu thực nghiệm thực tế chứng minh rằng mô hình đa góc nhìn không đạt được tính không thua kém so với mô hình chuỗi đơn lẻ trên tập dữ liệu HDFS trong bài toán phát hiện bất thường hạ nguồn.

---

## 6. Kiểm Tra Độ Nhạy Giao Diện Tham Số Đầu Vào của H2 (H2 Sequence No-Param Sensitivity)

Do mô hình `SequenceViewExtractor` trong nhánh Sequence-Only nhận tham số `param_slots=params`, trong khi mô hình đa góc nhìn gọi `seq_extractor.forward_pool(seq_inputs)` bên trong `extract_representation()` mà không truyền `param_slots`, nghiên cứu thực hiện kiểm tra độ nhạy: trích xuất biểu diễn toàn bộ 35.000 phiên Train và 7.500 phiên Validation của Sequence-Only khi che hoàn toàn tham số (`param_slots=None`), sau đó huấn luyện lại probe mới trên Train và đánh giá trên Validation:

*Bảng 3. Kết quả kiểm tra độ nhạy bỏ tham số đầu vào của nhánh Sequence-Only*

| Hạt giống (Seed) | Seq Không Tham Số AP | Seq Không Tham Số ROC | Seq Không Tham Số $\text{Var}(z)$ | Multi-View AP Đối Chứng | $\Delta \text{AP}$ (MV - Seq NoParam) | Biên $\ge -0.02$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | 1.0000 | 1.0000 | 0.006487 | 0.7604 | -0.2396 | Không đạt |
| **Seed 7** | 1.0000 | 1.0000 | 0.008236 | 0.6309 | -0.3691 | Không đạt |
| **Seed 999** | 1.0000 | 1.0000 | 0.007036 | 0.5911 | -0.4089 | Không đạt |
| **Trung bình** | **`1.0000 ± 0.0000`** | **`1.0000 ± 0.0000`** | **`0.007253 ± 0.000895`** | **`0.6608 ± 0.0885`** | **`-0.3392 ± 0.0885`** | **Không đạt** |

- **Kết luận:**
  ```
  H2_NEGATIVE_RESULT_ROBUST_TO_SEQUENCE_PARAMETER_INPUT_REMOVAL = true
  ```
  Ngay cả khi loại bỏ hoàn toàn các khe tham số động khỏi nhánh Sequence-Only trong cả quá trình trích xuất và huấn luyện probe, mô hình Sequence-Only vẫn đạt AP = 1.0000 và ROC-AUC = 1.0000. Kết quả phủ định của Giả thuyết H2 hoàn toàn không phải do sự bất đối xứng về việc tiếp nhận tham số đầu vào giữa hai kiến trúc.

---

## 7. Kiểm Toán Tính Toàn Vẹn Tiếp Tục Huấn Luyện của MULTI_VIEW Seed 999

Tiến trình huấn luyện Seed 999 đã trải qua hai lần tạm dừng hành chính và được khôi phục thành công:

1. *Ranh giới Tiếp tục Huấn luyện:*
   - Lần dừng 1: Hoàn tất Epoch 2 (Global Step 1094), lưu `checkpoint_epoch2.pt`. Khôi phục tại Epoch 3 qua [`scripts/resume_seed999_confirmatory.py`](file:///D:/Research/scripts/resume_seed999_confirmatory.py).
   - Lần dừng 2: Hoàn tất Epoch 5 (Global Step 2735), lưu `checkpoint_epoch5.pt`. Khôi phục tại Epoch 6.
   - Kết thúc: Kích hoạt dừng sớm khoa học tại Epoch 7 (Global Step 3829).
2. *Tính Toàn vẹn của Trạng thái:*
   - Các từ điển trạng thái `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict` được nạp đầy đủ.
   - Các biến điều khiển `global_step` (547 bước/epoch, liên tục từ 1 đến 3829), `best_val_loss` (48.7659 tại Epoch 4), `best_epoch`, và `patience_counter` (đạt 3/3 tại Epoch 7) được bảo toàn chuẩn xác.
   - Quỹ đạo tốc độ học (learning-rate trajectory) được Cosine Annealing duy trì liên tục qua 3.829 bước.
3. *Phân loại Pháp chứng Chính xác:*
   - `SEED999_RESUME_INTEGRITY = PARTIAL_STATE_RESUME_WITH_DETERMINISTIC_RNG_RECONSTRUCTION`
   - `EXACT_SERIALIZED_RNG_STATE = false` (Trạng thái RNG PyTorch được tái tạo thông qua thiết lập lại seed cố định và tua vòng lặp bộ dữ liệu thay vì giải mã từ điển trạng thái nhị phân trực tiếp).
   - `SEED999_CONFIRMATORY_STATUS = CONFIRMATORY_WITH_DOCUMENTED_PROTOCOL_DEVIATION`.

---

## 8. Kiểm Toán Độ Mịn Mục Tiêu và Kiểm Thử Giả Thuyết H1

### 8.1. Kiểm Toán Độ Mịn Mục Tiêu
- Nhãn `param_targets` trong `hdfs_ssl_train.pt` có kích thước $[L_i, 4]$ (cấp độ token $\times$ slot).
- Biểu diễn hạ nguồn được trích xuất là vector gộp cấp độ phiên: $z_{session} \in \mathbb{R}^{128}$.
- Phân tích thống kê cho thấy: nếu ánh xạ sang đa nhãn cấp phiên (Multi-Label Presence), 2 danh mục (IP và Generic String) xuất hiện trong 100% số phiên (phương sai nhãn bằng 0), 5 danh mục xuất hiện trong >98% số phiên, và 18/25 danh mục hoàn toàn có 0 mẫu dương trong tập Validation.
- Phân loại độ mịn:
  ```
  H1_TARGET_ALIGNMENT = TOKEN_LEVEL_REQUIRES_TOKEN_REPRESENTATION
  H1_DIRECT_STATUS = NOT_DIRECTLY_EVALUABLE_WITH_CURRENT_SESSION_REPRESENTATION
  ```

### 8.2. Kiểm Thử Cắt Bỏ Đầu Vào Đóng Băng (`FROZEN_INPUT_MASKING_ABLATION`)
Được thực thi độc lập tại [`scripts/run_h1_masking_ablation.py`](file:///D:/Research/scripts/run_h1_masking_ablation.py) trên 3 mô hình `SEQUENCE_ONLY` đóng băng: trích xuất biểu diễn khi mở toàn bộ tham số (`param_slots = params`) so với khi che hoàn toàn tham số (`param_slots = None`):

*Bảng 4. Kết quả kiểm thử cắt bỏ che tham số đầu vào trên Sequence-Only đóng băng*

| Hạt giống (Seed) | Độ tương đồng Cosine trung bình | Khoảng cách Euclid ($L_2$) trung bình | AP khi có tham số | AP khi che tham số | Độ suy giảm $\Delta \text{AP}$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | 0.9581 | 3.2742 | 1.0000 | 1.0000 | +0.0000 |
| **Seed 7** | 0.8201 | 6.7778 | 1.0000 | 1.0000 | +0.0000 |
| **Seed 999** | 0.9546 | 3.4056 | 1.0000 | 1.0000 | +0.0000 |

- `H1_MASKING_ABLATION_STATUS = AUXILIARY_OBSERVATION_ONLY`
- *Kết luận được phép:* Các khe tham số động làm thay đổi có thể đo lường được vector biểu diễn ẩn $z$ (độ tương đồng cosine giảm xuống $0.8201 - 0.9581$, khoảng cách Euclid dịch chuyển $3.27 - 6.78$), trong khi việc loại bỏ chúng không làm giảm AP phát hiện bất thường hạ nguồn trên tập HDFS.
- *Kết luận bị cấm:* Không tuyên bố đây là bằng chứng độc lập chứng minh mô hình có hiểu biết ngữ nghĩa sâu xa hay vượt trội hơn một mô hình được huấn luyện hoàn toàn không có tham số.

---

## 9. Tổng Hợp Thẩm Định Vi Mô Dành Cho Reviewer (Final Reviewer Micro-Audit)

Bảng tổng hợp đối sánh các khóa chỉ số phương pháp luận then chốt trước khi tích hợp vào luận án:

```yaml
MICRO_AUDIT_VERIFICATION_MATRIX:
  H2_PRIMARY_SCOPE: "MULTI_VIEW_VS_SEQUENCE_ONLY"
  H2_STATUS: "NOT_SUPPORTED_WITHIN_SEQUENCE_COMPARATOR_SCOPE"
  H2_SEQUENCE_NOPARAM_SENSITIVITY:
    tested_seeds: [42, 7, 999]
    mean_delta_ap_mv_vs_seq_noparam: -0.3392
    h2_negative_result_robust_to_sequence_parameter_input_removal: true
  H1_DIRECT_STATUS: "NOT_DIRECTLY_EVALUABLE_WITH_CURRENT_SESSION_REPRESENTATION"
  H1_MASKING_ABLATION_STATUS: "AUXILIARY_OBSERVATION_ONLY"
  SEED999_RESUME_INTEGRITY: "PARTIAL_STATE_RESUME_WITH_DETERMINISTIC_RNG_RECONSTRUCTION"
  SEED999_CONFIRMATORY_STATUS: "CONFIRMATORY_WITH_DOCUMENTED_PROTOCOL_DEVIATION"
  ANTI_COLLAPSE_OPERATIONALIZATION: "AMBIGUOUS_ACROSS_LEGACY_AND_V3_EXTRACTION"
  GRAPH_ONLY_FRESH_EXECUTED: false
  GRAPH_TRIAD_MAX_NOMINAL_GPU_HOURS: 114
  TEST_OPENED: false
  TEST_READ_COUNT: 0
  MASTER_CHANGED: false
```

Tác giả kính trình Quý Reviewer bản báo cáo tổng kết toàn diện và nghiêm cẩn này để làm căn cứ thẩm tra độc lập trước khi tiến hành tích hợp số liệu vào bản thảo luận án.

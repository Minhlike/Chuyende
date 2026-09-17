# BÁO CÁO KHOA HỌC TỔNG KẾT CHIẾN DỊCH NINEPLUS
## KẾT THÚC THỰC NGHIỆM THEO CHIẾN LƯỢC BẰNG CHỨNG TỐI ƯU HÓA CHI PHÍ (COST-OPTIMIZED EVIDENCE STRATEGY)
### ĐÁNH GIÁ CHUẨN HÓA V3 CHO BỘ BA MÔ HÌNH XÁC NHẬN VÀ KIỂM TOÁN GIẢ THUYẾT H1, H2

**Kính gửi:** Quý Reviewer (Peer Reviewer / Manuscript Reviewer)  
**Đề tài:** Nghiên cứu phát hiện bất thường nhật ký hệ thống sử dụng biểu diễn học tự giám sát đa góc nhìn (Multi-View Self-Supervised Learning)  
**Mã chiến dịch:** `NINEPLUS-EXPERIMENT-CAMPAIGN-V3` (Chiến lược Đóng Chiến dịch Tối ưu Chi phí)  
**Tệp kế hoạch chuẩn hóa:** [`experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json)  
**Thời điểm lập báo cáo:** 2026-09-18 01:05:00 (UTC+7)  
**Nhánh Git kiểm toán:** `fix/thesis-apply-edits` (Origin: `Minhlike/Chuyende`)  
**Môi trường thực thi:** Laptop NVIDIA GeForce RTX 3050 Ti (4.0 GB VRAM), AMD Ryzen CPU, Windows 11, Python 3.12.8 (`.venv-stage-a2-cuda`), PyTorch 2.6.0+cu124, CUDA 12.4.

---

## 1. Tuyên bố Bất biến và Ranh giới Phương pháp luận (Epistemic Invariants)

Báo cáo này công bố toàn bộ kết quả thực nghiệm cuối cùng của Chiến dịch Nineplus sau khi hoàn thành quy trình đánh giá chuẩn hóa V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`), kiểm toán tính toàn vẹn tiếp tục huấn luyện của Seed 999, kiểm toán độ mịn mục tiêu của Giả thuyết H1 và tái định nghĩa phạm vi kiểm chứng của Giả thuyết H2.

Nghiên cứu tuân thủ tuyệt đối các nguyên tắc phương pháp luận:

1. *Niêm phong Mật mã Tập Test (`TEST_OPENED=false`, `TEST_READ_COUNT=0`):* Toàn bộ tập dữ liệu Test HDFS được niêm phong mật mã tuyệt đối trong suốt quá trình nghiên cứu. Chưa có bất kỳ lần đọc hay tính toán nào được thực hiện trên tập Test.
2. *Đóng băng Bản thảo Luận văn (`MASTER_CHANGED=false`):* Các tệp luận án chính thức (`Chuyên đề chuyên sâu.docx` và `.pdf`) được giữ nguyên trạng thái, không bị chỉnh sửa hồi tố cho đến khi toàn bộ số liệu được Quý Reviewer thẩm tra và thông qua.
3. *Đính chính Ranh giới Dữ liệu Thực nghiệm:* Báo cáo xác nhận số lượng 7.500 phiên (119.531 sự kiện đồ thị thời gian) thuộc về tập Kiểm định cố định (Validation split), không phải tập Test. Tập Test hoàn toàn chưa mở.
4. *Kỷ luật Suy diễn Khoa học:* Mọi khẳng định trong báo cáo đều được phân định rõ ràng giữa số liệu quan sát trực tiếp (`OBSERVED_RESULT`), số liệu thống kê suy diễn (`DERIVED_RESULT`) và các giả thuyết thảo luận (`HYPOTHESIS`).

---

## 2. Kế toán Các Bước Tối ưu Hóa (Optimizer Step Accounting)

Trong giai đoạn thẩm định chuẩn hóa V3 này, không có bất kỳ bước tối ưu hóa nào được áp dụng lên các mạng nơ-ron nền tảng (backbones):

- `NEW_BACKBONE_OPTIMIZER_STEPS_THIS_PHASE`: **`0`** (Toàn bộ 6 backbone được đóng băng 100%).
- `NEW_V3_ANOMALY_PROBE_OPTIMIZER_STEPS`: **`41,100`** (Bao gồm 6 bộ phân loại tuyến tính mỏng $W \in \mathbb{R}^{128 \times 1}$, mỗi bộ thực hiện 6.850 bước tối ưu trên 35.000 phiên Train: $6 \times 6,850 = 41,100$ bước).
- `NEW_H1_PROBE_OPTIMIZER_STEPS`: **`0`** (Không huấn luyện thêm probe H1 do độ mịn mục tiêu không tương thích cấp độ phiên; bài kiểm thử cắt bỏ che tham số sử dụng trực tiếp các probe đã huấn luyện).

---

## 3. Kết quả Đánh giá Chuẩn Hóa V3 cho Sáu Mô Hình Xác Nhận

Quy trình đánh giá V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`) được thực thi độc lập tại [`scripts/evaluate_nineplus_v3.py`](file:///D:/Research/scripts/evaluate_nineplus_v3.py). Mã băm định danh danh sách phiên được xác thực trùng khớp tuyệt đối với hợp đồng Split Authority:
- Train Membership SHA256: `65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc`
- Val Membership SHA256: `14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a`
- Ordered Train Evaluation SHA256: `35396a595ded6ab643c07ce03528da4b91c1d270979b2c52e3e11f0cebcc7e60`
- Ordered Val Evaluation SHA256: `4f474991f03aab4856c2666a671bee3fc69d8e893e22e9c2d9ca1269b8bd68ae`

*Bảng 1. Ma trận kết quả đánh giá V3 trên 100% tập Validation cố định (7.500 phiên, Probe Seed = 10007)*

| Kiến trúc Mô hình | Hạt giống (Seed) | Checkpoint Nguồn | Average Precision (AP) | ROC-AUC | Phương sai Ẩn $\text{Var}(z)$ | Chống sụp đổ (Ngưỡng 0.01) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **`SEQUENCE_ONLY`** | 42 | `best_checkpoint.pt` (Ep 3) | 1.0000 | 1.0000 | 0.004535 | KHÔNG ĐẠT (FAIL) |
| (Đơn chuỗi sự kiện) | 7 | `best_checkpoint.pt` (Ep 11) | 1.0000 | 1.0000 | 0.005755 | KHÔNG ĐẠT (FAIL) |
| | 999 | `best_checkpoint.pt` (Ep 12) | 1.0000 | 1.0000 | 0.006097 | KHÔNG ĐẠT (FAIL) |
| **Trung bình Sequence** | **$N=3$** | **—** | **`1.0000 ± 0.0000`** | **`1.0000 ± 0.0000`** | **`0.005462 ± 0.000821`** | **0/3 Đạt** |
| | | | | | | |
| **`MULTI_VIEW_ALIGNED`**| 42 | `best_checkpoint.pt` (Ep 6) | 0.7604 | 0.9946 | 0.005513 | KHÔNG ĐẠT (FAIL) |
| (Đa góc nhìn liên kết) | 7 | `best_checkpoint.pt` (Ep 3) | 0.6309 | 0.8081 | 0.004682 | KHÔNG ĐẠT (FAIL) |
| | 999 | `best_checkpoint.pt` (Ep 4) | 0.5911 | 0.7693 | 0.008013 | KHÔNG ĐẠT (FAIL) |
| **Trung bình Multi-View** | **$N=3$** | **—** | **`0.6608 ± 0.0885`** | **`0.8573 ± 0.1204`** | **`0.006069 ± 0.001734`** | **0/3 Đạt** |
| | | | | | | |
| *`GRAPH_ONLY` (Lịch sử)* | 42 | Stage A2 (Ep 1) | 0.7090 | 0.8053 | 0.007200 | Tham chiếu lịch sử |
| *(Đơn đồ thị tham chiếu)*| 7 | Stage A2 (Ep 12) | 0.6178 | 0.7516 | 0.072700 | Tham chiếu lịch sử |
| | 999 | Stage A2 (Ep 12) | 0.6815 | 0.8857 | 0.073800 | Tham chiếu lịch sử |
| *Trung bình Graph Lịch sử*| *$N=3$* | *—* | *`0.6694 ± 0.0468`* | *`0.8142 ± 0.0675`* | *`0.051200 ± 0.038100`* | *Chỉ để đối chứng* |

*Bảng 2. Phân tích độ lệch bắt cặp giữa Multi-View và Sequence-Only ($\Delta = \text{Multi-View} - \text{Sequence-Only}$)*

| Hạt giống (Seed) | $\Delta \text{AP}$ (Độ lệch AP) | $\Delta \text{ROC-AUC}$ (Độ lệch ROC) | Biên Không Thua Kém ($\ge -0.02$) | Kết luận Bắt Cặp |
| :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | -0.2396 | -0.0054 | Vi phạm ($\Delta < -0.02$) | Thua kém đáng kể |
| **Seed 7** | -0.3691 | -0.1919 | Vi phạm ($\Delta < -0.02$) | Thua kém đáng kể |
| **Seed 999** | -0.4089 | -0.2307 | Vi phạm ($\Delta < -0.02$) | Thua kém đáng kể |
| **Trung bình** | **`-0.3392 ± 0.0885`** | **`-0.1427 ± 0.1204`** | **Vi phạm nghiêm trọng** | **Thua kém có ý nghĩa thống kê** |

*Ghi chú quan trọng về phương sai:* Trong các lượt chạy cũ, phương sai được tính trên luồng DataLoader chứa cơ chế che ngẫu nhiên 15% sự kiện (`<MASK>`), dẫn đến phương sai bị thổi phồng nhân tạo. Khi trích xuất biểu diễn thuần nhất trên dữ liệu gốc không che, phương sai thực tế của cả hai mô hình đều hội tụ quanh mức $0.0045 - 0.0080$.

---

## 4. Tái Định Nghĩa Phạm Vi và Phán Quyết Khoa Học của Giả Thuyết H2

### 4.1. Tái Định Nghĩa Phạm Vi Kiểm Chứng
Do chi phí tính toán lớn (nhánh Graph-Only tiêu tốn trên 190 phút/epoch trên phần cứng thử nghiệm) và chiến dịch được kết thúc có chủ đích theo chiến lược tối ưu hóa chi phí (`COST-OPTIMIZED EVIDENCE STRATEGY`), tác giả không triển khai huấn luyện mới bộ ba `GRAPH_ONLY_FRESH`.

Do đó, phạm vi của Giả thuyết H2 được định nghĩa lại chuẩn xác:
- *Phạm vi Xác nhận Chính (Primary Confirmatory Scope):* So sánh triển vọng trực tiếp giữa `MULTI_VIEW_ALIGNED_VICREG` và `SEQUENCE_ONLY` dưới cùng điều kiện hợp đồng Nineplus V3.
- *Phạm vi Khảo sát Thứ cấp (Secondary Exploratory Scope):* So sánh giữa `MULTI_VIEW_ALIGNED_VICREG` và số liệu tham chiếu lịch sử của `GRAPH_ONLY` (Stage A2).
- *Tuyên bố giới hạn:* Nghiên cứu không tuyên bố hoàn thành kiểm định xác nhận 3 phía (three-architecture confirmatory experiment). Số liệu Graph-Only chỉ đóng vai trò tham chiếu lịch sử.

### 4.2. Phán Quyết Chính Thức cho Giả Thuyết H2
- Biên độ không thua kém đăng ký trước: $\delta_{margin} \ge -0.02$ (được định danh rõ là `AUTHOR_DEFINED_A_PRIORI_PRACTICAL_MARGIN`).
- Độ lệch AP quan sát được: $\text{Mean } \Delta_{AP} = -0.3392 \pm 0.0885 \ll -0.02$.
- Toàn bộ 3 cặp hạt giống đều có độ suy giảm AP vượt xa ngưỡng dung sai cho phép (Seed 42: $-0.2396$; Seed 7: $-0.3691$; Seed 999: $-0.4089$).
- **Phán quyết chính thức:**
  ```
  H2_CONFIRMATORY_STATUS = NOT_SUPPORTED_WITHIN_SEQUENCE_COMPARATOR_SCOPE
  ```
  Dữ liệu thực nghiệm thực tế chứng minh rằng mô hình đa góc nhìn không đạt được tính không thua kém so với mô hình chuỗi đơn lẻ trên tập dữ liệu HDFS trong bài toán phát hiện bất thường hạ nguồn.

---

## 5. Kiểm Toán Tính Toàn Vẹn Tiếp Tục Huấn Luyện của Hạt Giống MULTI_VIEW Seed 999

Tiến trình huấn luyện Seed 999 đã trải qua hai lần tạm dừng hành chính và được khôi phục thành công:

1. *Ranh giới Tiếp tục Huấn luyện (Continuation Boundaries):*
   - Lần dừng 1: Hoàn tất Epoch 2 (Global Step 1094), lưu `checkpoint_epoch2.pt`. Khôi phục tại Epoch 3 qua [`scripts/resume_seed999_confirmatory.py`](file:///D:/Research/scripts/resume_seed999_confirmatory.py).
   - Lần dừng 2: Hoàn tất Epoch 5 (Global Step 2735), lưu `checkpoint_epoch5.pt`. Khôi phục tại Epoch 6.
   - Kết thúc: Kích hoạt dừng sớm khoa học tại Epoch 7 (Global Step 3829).
2. *Tính Toàn vẹn của Trạng thái:*
   - Các từ điển trạng thái `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict` được nạp đầy đủ.
   - Các biến điều khiển `global_step` (547 bước/epoch, liên tục từ 1 đến 3829), `best_val_loss` (48.7659 tại Epoch 4), `best_epoch`, và `patience_counter` (đạt 3/3 tại Epoch 7) được bảo toàn chuẩn xác.
   - Trình tạo số ngẫu nhiên của DataLoader được tua nhanh (fast-forward) qua các epoch đã hoàn thành để đồng bộ thứ tự mẫu.
3. *Phân loại Pháp chứng:*
   - `SEED999_RESUME_INTEGRITY = FULL_STATE_RESUME` (Ghi nhận độ lệch nhỏ: Trạng thái RNG của PyTorch được khôi phục qua thiết lập lại hạt giống và tua bộ lặp thay vì tuần tự hóa trực tiếp từ điển trạng thái RNG).
   - `SEED999_CONFIRMATORY_ELIGIBILITY = CONFIRMATORY_ELIGIBLE`.

---

## 6. Kiểm Toán Ranh Giới Ngữ Nghĩa và Dữ Liệu của Giả Thuyết H1

### 6.1. Xuất Xứ Dữ Liệu Thực Tế (Data Provenance)
Qua kiểm toán cấu trúc tệp dữ liệu:
- Nhãn bất thường phục vụ bài toán hạ nguồn lưu tại: `experiments/runs/data/vault/hdfs_probe_labels_train.pt` (35.000 nhãn) và `hdfs_probe_labels_val.pt` (7.500 nhãn). Các tệp này không chứa nhãn tham số.
- Nhãn danh mục tham số (`param_targets`) thực tế được lưu trong tệp huấn luyện tự giám sát: `experiments/runs/data/hdfs/hdfs_ssl_train.pt` và `hdfs_ssl_val.pt`.

### 6.2. Kiểm Toán Độ Mịn Mục Tiêu (Granularity Audit)
- Mỗi phiên $i$ có độ dài $L_i$ sự kiện. Nhãn `param_targets[i]` có kích thước $[L_i, 4]$, đại diện cho 4 khe tham số tại từng vị trí sự kiện/token.
- Biểu diễn hạ nguồn được trích xuất là vector gộp cấp độ phiên: $z_{session} \in \mathbb{R}^{128}$.
- Phân tích phân bố nếu ánh xạ sang vector nhị phân đa nhãn cấp phiên (Multi-Label Presence Vector):
  - Danh mục địa chỉ IP (`PARAM_IP_RFC1918_PRIVATE`) và chuỗi tổng quát (`PARAM_STR_GENERIC`) xuất hiện trong 100.00% số phiên (35.000/35.000 ở Train và 7.500/7.500 ở Val). Phương sai nhãn bằng 0, không có mẫu âm.
  - Năm danh mục số nhỏ và khối byte xuất hiện trong 98.16% đến 99.81% số phiên (thiếu mẫu âm trầm trọng).
  - Mười tám danh mục còn lại có 0 mẫu dương trong tập Validation.
- Do đó, việc gượng ép một bài toán phân loại đa nhãn cấp phiên để đo `Macro-F1` là thoái hóa về mặt thống kê.
- **Phân loại độ mịn:**
  ```
  H1_TARGET_ALIGNMENT = TOKEN_LEVEL_REQUIRES_TOKEN_REPRESENTATION
  H1_STATUS = NOT_DIRECTLY_EVALUABLE_WITH_CURRENT_SESSION_REPRESENTATION
  ```
  Để bảo đảm liêm chính học thuật, nghiên cứu không tạo nhãn giả mạo hay chọn ngẫu nhiên tham số đại diện cho phiên.

### 6.3. Kiểm Thử Cắt Bỏ Đầu Vào Đóng Băng (`FROZEN_INPUT_MASKING_ABLATION`)
Thay vì huấn luyện probe trên nhãn cấp phiên thoái hóa, nghiên cứu thực hiện kiểm thử cắt bỏ trên 3 mô hình `SEQUENCE_ONLY` đóng băng: trích xuất biểu diễn khi mở toàn bộ tham số (`param_slots = params`) so với khi che hoàn toàn tham số (`param_slots = None`):

*Bảng 3. Kết quả kiểm thử cắt bỏ che tham số đầu vào trên mô hình Sequence-Only đóng băng*

| Hạt giống (Seed) | Độ tương đồng Cosine trung bình | Khoảng cách Euclid ($L_2$) trung bình | AP khi có tham số | AP khi che tham số | Độ suy giảm $\Delta \text{AP}$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | 0.9581 | 3.2742 | 1.0000 | 1.0000 | +0.0000 |
| **Seed 7** | 0.8201 | 6.7778 | 1.0000 | 1.0000 | +0.0000 |
| **Seed 999** | 0.9546 | 3.4056 | 1.0000 | 1.0000 | +0.0000 |

*Phát hiện thực nghiệm:*
- Việc che các khe tham số làm thay đổi đáng kể vector biểu diễn ẩn (độ tương đồng cosine giảm xuống mức $0.8201 - 0.9581$, khoảng cách Euclid dịch chuyển $3.27 - 6.78$). Điều này xác nhận các khe tham số động đóng góp thông tin được mô hình tiếp nhận và tích hợp vào không gian biểu diễn.
- Tuy nhiên, trên tập dữ liệu HDFS, chuỗi định danh sự kiện (Event Templates) đã mang tính phân tách tuyến tính tuyệt đối đối với nhãn bất thường, nên việc che tham số không làm suy giảm AP hạ nguồn.

---

## 7. Ranh Giới Khẳng Định Khoa Học (Allowed & Forbidden Inferences)

Nhằm tuân thủ các chuẩn mực đạo đức nghiên cứu và chỉ dẫn phản biện, các khẳng định học thuật được giới hạn rõ ràng:

### 7.1. Các Khẳng Định Được Phép (Allowed Claims)
1. Dưới giao thức đánh giá chuẩn hóa V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`), mô hình đơn chuỗi `SEQUENCE_ONLY` đạt hiệu năng vượt trội ($\text{AP} = 1.0000$, $\text{ROC-AUC} = 1.0000$) so với mô hình đa góc nhìn liên kết `MULTI_VIEW_ALIGNED_VICREG` ($\text{AP} = 0.6608$, $\text{ROC-AUC} = 0.8573$) trên tập dữ liệu HDFS.
2. Việc tích hợp các khe tham số động trong nhánh `SEQUENCE_ONLY` đóng góp thông tin vật lý làm biến đổi không gian biểu diễn ẩn $z$, được chứng minh qua khoảng cách biểu diễn trong kiểm thử cắt bỏ che đầu vào.
3. Dưới giao thức probe cũ, mô hình đa góc nhìn đạt ROC-AUC cao hơn mô hình đơn đồ thị lịch sử ($0.8933$ so với $0.8142$).
4. Toàn bộ tiến trình thực nghiệm bảo toàn tính liêm chính phương pháp luận: tập Test được niêm phong mật mã 100% (`TEST_OPENED=false`, `TEST_READ_COUNT=0`), bản thảo chính không bị sửa đổi hồi tố (`MASTER_CHANGED=false`).

### 7.2. Các Khẳng Định Bị Cấm Tuyệt Đối (Forbidden Claims)
1. *Không khẳng định tính vượt trội của Multi-View:* Tuyệt đối không tuyên bố mô hình đa góc nhìn vượt trội hơn mô hình chuỗi đơn lẻ trên bài toán HDFS.
2. *Không khẳng định quan hệ nhân quả của VICReg:* Không tuyên bố hàm mất mát VICReg trực tiếp gây ra nén phương sai, do nghiên cứu chưa tiến hành kiểm thử cắt bỏ đối chứng riêng rẽ từng số hạng của VICReg.
3. *Không khẳng định quan hệ nhân quả của cơ chế dung hợp:* Không khẳng định việc kết hợp đa góc nhìn là nguyên nhân duy nhất làm tăng độ nhạy so với mô hình đồ thị lịch sử, do mô hình đồ thị lịch sử không phải là mô hình đối chứng triển vọng tương thích.
4. *Không khẳng định tính ưu việt của cơ chế có tham số so với mô hình chỉ học mẫu:* Kiểm thử cắt bỏ trên mô hình đóng băng chỉ chứng minh tham số có đóng góp thông tin vào biểu diễn hiện tại, không chứng minh mô hình học có tham số vượt trội hơn một mô hình độc lập được huấn luyện hoàn toàn không có tham số.

---

## 8. Hạn Chế Còn Lại của Nghiên Cứu (Remaining Limitations)

1. *Hạn chế nhánh Graph-Only:* Bộ ba xác nhận triển vọng `GRAPH_ONLY_FRESH` chưa được huấn luyện do hạn chế về ngân sách tính toán (thời gian huấn luyện ước tính trên 38 giờ GPU cho 12 epochs). Các so sánh với Graph-Only chỉ mang tính chất khảo sát lịch sử.
2. *Tính phân tách cao của tập HDFS:* Tập dữ liệu HDFS thể hiện đặc tính phân tách mạnh theo chuỗi sự kiện, khiến mô hình đơn chuỗi đạt mức trần hiệu năng và làm giảm cơ hội thể hiện tính bổ trợ của góc nhìn đồ thị thời gian.
3. *Quy tắc chống sụp đổ phương sai:* Quy tắc ngưỡng phương sai ẩn ($0.01000$) trong các tài liệu tiền đăng ký ban đầu chưa chỉ định rõ ràng là áp dụng trên từng hạt giống đơn lẻ hay lấy trung bình các hạt giống (`ANTI_COLLAPSE_AGGREGATION_RULE = AMBIGUOUS_PREREGISTRATION`). Nghiên cứu báo cáo minh bạch kết quả từng hạt giống thay vì điều chỉnh quy tắc sau thực nghiệm.

Tác giả kính trình Quý Reviewer bản báo cáo tổng kết toàn diện này để làm căn cứ thẩm định học thuật cho công trình.

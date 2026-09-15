# BÁO CÁO TIẾN ĐỘ THỰC NGHIỆM TOÀN DIỆN CHIẾN DỊCH NINEPLUS (CAMPAIGN V2 / TU CHÍNH V3)
**Dành cho Hội đồng Đánh giá & Phản biện Khoa học (Reviewer Report)**

- **Đề tài:** Nghiên cứu phát hiện bất thường nhật ký hệ thống sử dụng biểu diễn học tự giám sát đa góc nhìn (Multi-View Self-Supervised Learning).
- **Mã chiến dịch:** `NINEPLUS-EXPERIMENT-CAMPAIGN-V2` / Kế hoạch tu chính: [`NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json)
- **Thời điểm cập nhật:** 2026-09-15 16:35:00 (UTC+7)
- **Môi trường phần cứng:** Laptop NVIDIA GeForce RTX 3050 Ti (4.0 GB VRAM), AMD Ryzen CPU, Windows 11.
- **Môi trường thực thi:** Python 3.12.8 (`.venv-stage-a2-cuda`), PyTorch 2.6.0+cu124, CUDA 12.4.
- **Nhánh Git thẩm tra:** `fix/thesis-apply-edits` (Origin: `Minhlike/Chuyende`).

---

## METHODOLOGICAL CORRECTION — V3 (THÔNG CÁO ĐIỀU CHỈNH PHƯƠNG PHÁP LUẬN)

> [!IMPORTANT]
> **Kiểm toán Phương pháp luận V3 đã chính thức phân loại lại toàn bộ các chỉ số thu thập trước thời điểm này:**
> 1. **Nhánh `SEQUENCE_ONLY` (Seeds 42, 7, 999):** Các backbone đã hoàn thành hợp lệ và được phân loại là `CONFIRMATORY_BACKBONE_ELIGIBLE`. Toàn bộ chỉ số AP và ROC-AUC hiện có trong các bảng báo cáo được phân loại là `LEGACY_PROBE_EXPLORATORY_METRIC` vì được đo qua giao thức cũ (chia 80/20 nội bộ tập Validation, seed phụ thuộc). Các chỉ số này đang chờ tính toán lại theo giao thức chuẩn hóa V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`).
> 2. **Nhánh `SEQUENCE_ONLY` (Seeds 1337, 2024):** Được phân loại là `SUPPLEMENTARY_EXPLORATORY`. Cung cấp ngữ cảnh độ bền bổ trợ cho phân bố $N=5$, nhưng không thuộc bộ ba hạt giống đối chứng H2 chính thức ($N=3$).
> 3. **Nhánh `GRAPH_ONLY` (Seeds 42, 7, 999):** Toàn bộ kết quả hiện tại được đánh dấu là `HISTORICAL_EXPLORATORY_REFERENCE_ONLY` do được đánh giá từ checkpoint của giai đoạn thăm dò Stage A2 cũ. Nhánh này bắt buộc phải được huấn luyện mới hoàn toàn (`GRAPH_ONLY_FRESH`) dưới cùng harness triển vọng để bước vào ma trận quyết định H2 chính thức.
> 4. **Nhánh `MULTI_VIEW_ALIGNED_VICREG` (Seed 42):** Backbone hoàn thành hợp lệ (`CONFIRMATORY_BACKBONE_ELIGIBLE`). Trạng thái chống sụp đổ biểu diễn được phân loại chính thức là `FAIL_UNDER_PREREGISTERED_THRESHOLD` do phương sai đạt $0.00997 < 0.01000$. Chỉ số AP/ROC-AUC hiện tại được phân loại là `LEGACY_PROBE_EXPLORATORY_METRIC` chờ tính lại theo V3.
> 5. **Nhánh `MULTI_VIEW_ALIGNED_VICREG` (Seed 7):** Trạng thái `TRAINING_IN_PROGRESS`. Tuyệt đối không can thiệp hay rút ra kết luận sớm; tiến trình huấn luyện được để chạy tự nhiên cho đến khi thỏa mãn điều kiện early stopping hoặc chạm trần 12 epoch.
> 6. **Nhánh `MULTI_VIEW_ALIGNED_VICREG` (Seed 999):** Trạng thái `PENDING_CONFIRMATORY_REQUIRED` (bắt buộc thực hiện, tạm hoãn cho lượt sau).
> 7. **Kỷ luật Thuật ngữ:** Đã chuẩn hóa nhãn `Average Precision (AP)`, bãi bỏ cách gọi không chuẩn mực `AP (PR-AUC)`. Toàn bộ các suy đoán nhân quả hậu nghiệm đã được loại bỏ, thay bằng ngôn ngữ quan sát khách quan.
> 8. **Trạng thái Hiện tại của H2:** `H2_CONFIRMATORY_STATUS = INCOMPLETE_PROTOCOL_REPAIR_IN_PROGRESS`.

---

## 1. Tóm tắt Điều hành & Ràng buộc Bất biến (Epistemic Invariants)

Chiến dịch Thực nghiệm Nineplus được thiết lập nhằm trả lời câu hỏi nghiên cứu cốt lõi của Chương 3 và Chương 4: **"Việc kết hợp đa góc nhìn giữa Chuỗi sự kiện (Sequence View) và Đồ thị thời gian (Temporal Graph View) qua hàm mất mát căn chỉnh VICReg có mang lại sự vượt trội thực nghiệm hoặc không thua kém có ý nghĩa so với các mô hình đơn góc nhìn độc lập hay không?"**

Toàn bộ quá trình thực nghiệm tuân thủ nghiêm ngặt các nguyên tắc phương pháp luận:
1. **Niêm phong Mật mã Tập Test (`TEST_OPENED=false`, `TEST_READ_COUNT=0`):** Tuyệt đối không có bất kỳ nhãn hay sự kiện nào của tập Test được mở trong quá trình tiền huấn luyện (Stage A) hoặc tinh chỉnh siêu tham số.
2. **Đánh giá Biểu diễn Đóng băng (Capacity-Controlled Frozen Linear Probe):** Biểu diễn đặc trưng được trích xuất cố định từ mô hình tối ưu. Đánh giá nhãn dị thường hạ nguồn (downstream anomaly detection) được thực hiện qua bộ phân loại tuyến tính mỏng ($W \in \mathbb{R}^{128 	imes 1}$, 50 epochs, zero hidden layers).
3. **Bảo toàn Tính Toàn vẹn Tài liệu Chính (`MASTER_CHANGED=false`):** Toàn bộ tệp bản thảo chính của luận văn (`Chuyên đề chuyên sâu.docx` và `.pdf`) được giữ nguyên vẹn, không chỉnh sửa trực tiếp cho tới khi có phê duyệt nghiệm thu toàn bộ số liệu.

---

## 2. Giai đoạn 1: Thử nghiệm Kỹ thuật (Phase 1 Technical Pilots) — ĐÃ HOÀN THÀNH 100%

*Cam kết khóa mã nguồn: Commit [`3e0bcef`](https://github.com/Minhlike/Chuyende/commit/3e0bcef) (Báo cáo: `NINEPLUS-PHASE1-PILOT-REPORT.md`)*

Giai đoạn Pilot đã kiểm thử thành công cả 3 kiến trúc ở Seed 42 (mỗi kiến trúc chạy 2 epochs, tổng cộng 3,334 bước optimizer mới):
- **Kiểm định VRAM:** Cả 3 kiến trúc đều nằm gọn trong phong bì bộ nhớ 4.0 GB VRAM của RTX 3050 Ti (Sequence: 184.3 MB, Graph: 1,255.1 MB, Multi-View: 277.6 MB).
- **Ổn định Số học:** Tuyệt đối 0 lỗi `NaN`, 0 lỗi `Inf`.
- **Kiểm định Checkpoint & Resume:** 100% vượt qua kiểm tra so khớp tham số máy học (`torch.allclose(atol=0.0)`).
- **Đặc tả Biểu diễn Đầu ra:** Vector biểu diễn của cả 3 kiến trúc đều đảm bảo đúng kích thước $z \in \mathbb{R}^{7500 	imes 128}$, tương thích 100% với danh sách định danh phiên (`session_ids`) của kho nhãn kiểm chứng (`hdfs_probe_labels_val.pt`).

---

## 3. Giai đoạn 2: Tiến độ Thực nghiệm Kiểm chứng (Phase 2 Confirmatory Runs)

### 3.1. Nhánh `SEQUENCE_ONLY` (Đơn chuỗi Transformer) — 5 SEED ĐÃ HOÀN TẤT
*Cam kết đồng bộ Git: Commit [`47e4ad6`](https://github.com/Minhlike/Chuyende/commit/47e4ad6)*

Kiến trúc `SequenceViewExtractor` (Transformer Encoder 4-layer, $d=128$, MEP + MPP + Time SSL) đã hoàn thành huấn luyện backbone. Lưu ý rằng các chỉ số Probe dưới đây thuộc nhóm `LEGACY_PROBE_EXPLORATORY_METRIC` (đo theo giao thức 80/20 cũ) và sẽ được đo lại theo chuẩn V3:

| Canonical Seed | Vai trò Phân loại V3 | Số Epoch | Best Epoch | Best Val Loss | **Legacy Probe Average Precision (AP)** | **Legacy Probe ROC-AUC** | Phương sai $	ext{Var}(z)$ | Thời gian chạy |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | `CONFIRMATORY_BACKBONE_ELIGIBLE` | 6 | 3 | 0.0092 | **`0.8994`** | **`0.9973`** | `0.0935` | 13.6 phút |
| **Seed 7** | `CONFIRMATORY_BACKBONE_ELIGIBLE` | 12 | 11 | 0.0063 | **`0.9179`** | **`0.9984`** | `0.0999` | 26.2 phút |
| **Seed 999** | `CONFIRMATORY_BACKBONE_ELIGIBLE` | 12 | 12 | 0.0073 | **`0.7887`** | **`0.9263`** | `0.1455` | 13.1 phút |
| **TRUNG BÌNH H2 ($N=3$)** | **Đối chứng Xác nhận H2** | — | — | **`0.0076`** | **`0.8687 ± 0.0700`** | **`0.9740 ± 0.0413`** | **`0.1130 ± 0.0284`** | **52.9 phút tổng** |
| *Seed 1337* | `SUPPLEMENTARY_EXPLORATORY` | 12 | 11 | 0.0067 | `1.0000` | `1.0000` | `0.1427` | 27.1 phút |
| *Seed 2024* | `SUPPLEMENTARY_EXPLORATORY` | 12 | 9 | 0.0071 | `0.7310` | `0.9416` | `0.0696` | 22.0 phút |
| *TỔNG THỂ ($N=5$)* | *Bổ trợ Khảo sát Mở rộng* | — | — | *`0.0073`* | *`0.8674 ± 0.1072`* | *`0.9727 ± 0.0358`* | *`0.1102 ± 0.0329`* | *102 phút tổng* |

---

### 3.2. Nhánh `GRAPH_ONLY` (Đơn đồ thị thời gian TGN) — HỒ SƠ THAM CHIẾU LỊCH SỬ STAGE A2
*Cam kết đồng bộ Git: Commit [`d6fb10b`](https://github.com/Minhlike/Chuyende/commit/d6fb10b)*

> [!NOTE]
> **PHÂN LOẠI SUY DIỄN: `HISTORICAL_EXPLORATORY_REFERENCE_ONLY`**
> Các kết quả dưới đây sử dụng trọng số từ checkpoint Stage A2 lịch sử (`best_val_loss.pt`). Bảng này được lưu giữ để bảo toàn chuỗi bằng chứng thực nghiệm, **không tham gia ma trận quyết định H2 chính thức**. Chiến dịch Nineplus V3 yêu cầu huấn luyện mới triển vọng (`GRAPH_ONLY_FRESH`) cho cả 3 seed `42, 7, 999`.

| Canonical Seed | Nguồn Checkpoint Lịch sử | **Legacy Probe Average Precision (AP)** | **Legacy Probe ROC-AUC** | Phương sai $	ext{Var}(z)$ | Tỷ lệ Khớp Node Session |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | Stage A2 `best_val_loss.pt` (Epoch 1) | **`0.7090`** | **`0.8053`** | `0.0072` | 7,500/7,500 (100%) |
| **Seed 7** | Stage A2 `best_val_loss.pt` (Epoch 12) | **`0.6178`** | **`0.7516`** | `0.0727` | 7,500/7,500 (100%) |
| **Seed 999** | Stage A2 `best_val_loss.pt` (Epoch 12) | **`0.6815`** | **`0.8857`** | `0.0738` | 7,500/7,500 (100%) |
| **TRUNG BÌNH ($N=3$)** | — | **`0.6694 ± 0.0468`** | **`0.8142 ± 0.0675`** | **`0.0512 ± 0.0381`** | **100% Khớp hoàn hảo** |

---

### 3.3. Nhánh `MULTI_VIEW_ALIGNED_VICREG` (Đa góc nhìn liên kết) — TIẾN TRÌNH THỰC THI

- **Seed 42 (Hoàn tất 100% - Commit [`7bdcade`](https://github.com/Minhlike/Chuyende/commit/7bdcade)):**
  - Số epoch hoàn thành: 9 / 12 (Kích hoạt Early Stopping tại Epoch 9; điểm cực tiểu Val Loss tại **Epoch 6**: `49.1768`).
  - **Legacy Probe AP:** **`0.7032`** | **Legacy Probe ROC-AUC:** **`0.9319`** (Phân loại: `LEGACY_PROBE_EXPLORATORY_METRIC`, chờ tính lại theo V3).
  - Phương sai biểu diễn: $	ext{Var}(z) = 0.00997$.
  - **Đánh giá Chống Sụp đổ:** Phân loại chính thức là `FAIL_UNDER_PREREGISTERED_THRESHOLD` do thấp hơn ngưỡng đăng ký trước $0.01000$. Backbone được bảo toàn để tái đánh giá Probe V3; kết luận H2 không định đoạt trên một seed đơn lẻ.
- **Seed 7 (Hoàn tất 100% — Early Stopping tại Epoch 6):**
  - Số epoch hoàn thành: 6 / 12 (Kích hoạt Early Stopping khoa học tại Epoch 6 với patience=3).
  - Điểm cực tiểu tối ưu toàn cục: **Epoch 3** (Val Loss: `49.0099`).
  - Checkpoint tối ưu: [`best_checkpoint.pt`](file:///D:/Research/experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed7_1789452137/best_checkpoint.pt).
  - **Legacy Probe AP:** **`0.6082` (60.82%)** | **Legacy Probe ROC-AUC:** **`0.8899` (88.99%)** (Phân loại: `LEGACY_PROBE_EXPLORATORY_METRIC`, chờ tính lại theo V3).
  - Phương sai biểu diễn: $\text{Var}(z) = 0.012643$.
  - **Đánh giá Chống Sụp đổ:** Phân loại chính thức là **`PASS_OVER_PREREGISTERED_THRESHOLD`** ($\text{Var}(z) = 0.012643 \ge 0.01000$). Khác với Seed 42 sát ngưỡng dưới, Seed 7 vượt qua ngưỡng kiểm định chống sụp đổ biểu diễn theo hợp đồng V2/V3.
  - Tổng số bước tối ưu hóa: 3,282 bước. Biên bản nghiệm thu đã xuất tại [`RUN-MANIFEST.json`](file:///D:/Research/experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed7_1789452137/RUN-MANIFEST.json).
- **Seed 999 (Chờ thực thi):**
  - Phân loại: `PENDING_CONFIRMATORY_REQUIRED`. Bắt buộc thực hiện đầy đủ để cấu thành bộ ba xác nhận.

---

## 4. Bảng Đối chứng Tổng hợp & Phân tích Quan sát (Audit Comparison)

Bảng dưới đây tổng hợp các phép đo hiện có. Lưu ý rằng các giá trị Probe thuộc nhóm giao thức cũ (`LEGACY_PROBE_EXPLORATORY_METRIC`) và nhánh Graph là dữ liệu lịch sử Stage A2:

| Tiêu chí Đánh giá | `GRAPH_ONLY` (Lịch sử Stage A2, $N=3$) | `MULTI_VIEW_ALIGNED` (Seed 42, Legacy Probe) | `SEQUENCE_ONLY` ($N=3$: Seeds 42, 7, 999, Legacy Probe) | `SEQUENCE_ONLY` ($N=5$ Toàn diện, Legacy Probe) |
| :--- | :---: | :---: | :---: | :---: |
| **Phân loại Suy diễn** | `HISTORICAL_EXPLORATORY_REFERENCE_ONLY` | `CONFIRMATORY_BACKBONE_ELIGIBLE` (Probe V3 pending) | `CONFIRMATORY_BACKBONE_ELIGIBLE` (Probe V3 pending) | `SUPPLEMENTARY_EXPLORATORY` |
| **Average Precision (AP)** | `0.6694 ± 0.0468` | `0.7032` | **`0.8687 ± 0.0700`** | **`0.8674 ± 0.1072`** |
| **ROC-AUC** | `0.8142 ± 0.0675` | `0.9319` | **`0.9740 ± 0.0413`** | **`0.9727 ± 0.0358`** |
| **Phương sai $	ext{Var}(z)$** | `0.0512 ± 0.0381` | `0.00997` (`FAIL_UNDER_PREREGISTERED_THRESHOLD`) | **`0.1130 ± 0.0284`** | **`0.1102 ± 0.0329`** |
| **Thời gian Train / Epoch** | ~190 phút | ~23.5 phút | **~2.0 phút** | **~2.0 phút** |
| **Bộ nhớ VRAM đỉnh** | 1,255 MB | 260.6 MB | **170.4 MB** | **170.4 MB** |

### Ghi nhận Quan sát Thực nghiệm (Kỷ luật Ngôn ngữ V3):
1. **Quan sát về ROC-AUC giữa Multi-View Seed 42 và Graph-Only Lịch sử:**
   - Dưới giao thức probe cũ, `MULTI_VIEW_ALIGNED` Seed 42 đạt ROC-AUC `0.9319`, cao hơn so với giá trị đo được từ checkpoint lịch sử của `GRAPH_ONLY` Seed 42 (`0.8053`). Việc đánh giá xem sự cải thiện này có mang tính quy luật và có ý nghĩa thống kê hay không đòi hỏi phải hoàn thành đối chứng matched-pairs với `GRAPH_ONLY_FRESH`.
2. **Quan sát về AP giữa Sequence-Only và Multi-View Seed 42:**
   - Dưới giao thức probe cũ, mô hình `SEQUENCE_ONLY` đạt AP trung bình $0.8687$ trên 3 seed xác nhận, cao hơn giá trị quan sát được trên `MULTI_VIEW_ALIGNED` Seed 42 ($0.7032$).
   - Đồng thời, phương sai không gian biểu diễn của Multi-View Seed 42 ($	ext{Var}(z) = 0.00997$) thấp hơn đáng kể so với Sequence-Only ($	ext{Var}(z) = 0.1130$). Giả thuyết về sự nén biểu diễn do ràng buộc căn chỉnh VICReg hoặc đặc thù liên kết đồ thị là một hướng giải thích cần được kiểm định có đối chứng, không xem là nguyên nhân nhân quả đã được chứng minh.
3. **Ý nghĩa đối với Giả thuyết H2:**
   - Trạng thái hiện tại: `H2_CONFIRMATORY_STATUS = INCOMPLETE_PROTOCOL_REPAIR_IN_PROGRESS`.
   - Mọi kết luận khẳng định hay bác bỏ H2 đều chưa có cơ sở phương pháp luận đầy đủ cho đến khi hoàn thành: (1) huấn luyện tự nhiên Seed 7, (2) huấn luyện Seed 999, (3) huấn luyện mới `GRAPH_ONLY_FRESH` (Seeds 42, 7, 999), và (4) tính toán đồng bộ Probe V3 trên toàn bộ 9 mô hình.

---

## 5. Chuỗi Bằng chứng Mật mã Git (Provenance Chain)

Toàn bộ các mốc tiến độ đều được bảo chứng qua các commit phân tán trên GitHub:
- [`0df87c2`](https://github.com/Minhlike/Chuyende/commit/0df87c2): Thiết kế khóa hợp đồng Chiến dịch Nineplus V2.
- [`3e0bcef`](https://github.com/Minhlike/Chuyende/commit/3e0bcef): Khóa nghiệm thu 100% Phase 1 Technical Pilots (3 kiến trúc, 6 epochs).
- [`7bdcade`](https://github.com/Minhlike/Chuyende/commit/7bdcade): Nghiệm thu Phase 2 Confirmatory Multi-View Seed 42.
- [`4234aa8`](https://github.com/Minhlike/Chuyende/commit/4234aa8): Nghiệm thu Phase 2 Confirmatory Sequence-Only Seed 42.
- [`47e4ad6`](https://github.com/Minhlike/Chuyende/commit/47e4ad6): Hoàn tất 100% 5 seed nhánh Sequence-Only.
- [`d6fb10b`](https://github.com/Minhlike/Chuyende/commit/d6fb10b): Hoàn tất nghiệm thu Probe cho nhánh Graph-Only lịch sử Stage A2.

---
*Báo cáo được tổng hợp từ các artifact được liệt kê và tiếp tục chịu kiểm toán protocol trước khi hình thành kết luận xác nhận.*

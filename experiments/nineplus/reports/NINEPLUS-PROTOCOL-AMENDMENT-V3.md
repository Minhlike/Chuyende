# BÁO CÁO TU CHÍNH PROTOCOL CHIẾN DỊCH NINEPLUS (V3 PROTOCOL AMENDMENT)
**Tài liệu Kiểm toán & Điều chỉnh Phương pháp luận Thực nghiệm (Audit & Methodological Correction)**

- **Mã chiến dịch:** `NINEPLUS-EXPERIMENT-CAMPAIGN-V3`
- **Kế hoạch chuẩn hóa V3:** [`NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json)
- **Kế hoạch tiền nhiệm V2:** [`NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json)
- **Base Git SHA trước tu chính:** `4df9666489fa7147d68f5e4d972305a905ff469f`
- **Thời điểm ban hành:** 2026-09-15 16:35:00 (UTC+7)
- **Phân loại tu chính:** `PROSPECTIVE_CORRECTIVE_AMENDMENT`

---

## LƯU Ý PHƯƠNG PHÁP LUẬN BẮT BUỘC (AMENDMENT NOTICE)

> [!WARNING]
> **V3 là Bản Tu chính Sửa sai Triển vọng (Prospective Corrective Amendment), không phải bản tiền đăng ký nguyên sơ trước khi quan sát dữ liệu (Pristine Pre-Outcome Preregistration).**
> Bản tu chính này được thiết lập **SAU KHI** một số kết quả sơ bộ và bán phần đã được quan sát trong Chiến dịch V2 (toàn bộ 5 seed nhánh Sequence, 3 checkpoint lịch sử nhánh Graph, và Seed 42 nhánh Multi-View). Mục đích của V3 là minh bạch hóa các khiếm khuyết phương pháp luận đã phát hiện, cô lập các kết quả cũ vào đúng phân loại suy diễn (`EXPLORATORY`), và khóa cứng quy trình kiểm định công bằng, độc lập cho các bước đo đạc xác nhận tiếp theo (`CONFIRMATORY`).

---

## 1. TẠI SAO V3 TỒN TẠI (WHY V3 EXISTS)

Trong quá trình thực thi huấn luyện `MULTI_VIEW_ALIGNED_VICREG` Seed 7 theo kế hoạch V2, việc kiểm toán độc lập quy trình thu thập số liệu và suy diễn khoa học đã phát hiện 5 vấn đề phương pháp luận nghiêm trọng:

1. **Sự không tương thích của nhánh Đơn Đồ thị (Graph-Only Mismatch):** Kết quả đối chứng đơn đồ thị trong báo cáo tiến độ được đo từ các checkpoint Stage A2 lịch sử, không được huấn luyện đồng bộ từ đầu dưới cùng harness thực nghiệm triển vọng của chiến dịch Nineplus.
2. **Khiếm khuyết quy trình Linear Probe hạ nguồn (Probe Protocol Flaw):** Đánh giá Linear Probe trước đây chia 80/20 nội bộ ngay trong tập Validation (7,500 session), vừa làm giảm kích thước mẫu đánh giá, vừa phụ thuộc vào seed ngẫu nhiên của mô hình.
3. **Sự không đồng nhất của tập đánh giá con (Seed-Dependent Evaluation Subsets):** Do chia 80/20 dùng seed mô hình làm RNG, các mô hình với seed khác nhau được chấm điểm trên các tập session con khác nhau, vi phạm nguyên tắc mẫu cặp đối chứng (matched-pairs).
4. **Nguy cơ can thiệp phi khoa học từ tiến trình Watcher theo giờ hành chính:** Script giám sát ngầm (`scripts/stop_after_seed7.ps1`) có điều kiện cưỡng chế dừng tiến trình tại mốc 17:00 chiều và đánh dấu giả mạo `early_stopped=true`, vi phạm nguyên tắc dừng tự nhiên của mô hình.
5. **Suy diễn nhân quả vượt quá bằng chứng thực nghiệm (Unsupported Causal Over-interpretation):** Các diễn giải trong báo cáo tiến độ trước đây khẳng định các cơ chế nhân quả (như "Gated Fusion bù đắp thông tin chuỗi", "HDFS tuyến tính gây sụt giảm đa góc nhìn", "VICReg gây negative transfer") mà không có các kiểm thử cắt bỏ (ablation) đối chứng nhân quả tương ứng.

V3 được ban hành để giải quyết dứt điểm các khiếm khuyết này một cách công khai, minh bạch, bảo vệ độ tin cậy khoa học của toàn bộ luận án.

---

## 2. NHỮNG ĐIỂM CHƯA ĐẠT TRONG QUY TRÌNH CŨ (WHAT WAS WRONG)

| STT | Hạng mục | Quy trình cũ (V2 / Legacy) | Sai sót Phương pháp luận |
| :---: | :--- | :--- | :--- |
| **1** | **Nhánh Graph-Only** | Đo Probe từ checkpoint Stage A2 lịch sử (`.artifacts/stage-a2/HDFS/best_val_loss.pt`). | Không được huấn luyện prospectively dưới cùng pipeline, cùng điều kiện hội tụ và scheduler với Sequence và Multi-View. |
| **2** | **Tập dữ liệu Probe** | Trích xuất 7,500 vector Validation; cắt 80% để train probe, 20% (1,500 vector) để test. | Dùng tập Validation cho cả huấn luyện lẫn kiểm tra probe; chỉ đánh giá trên 1,500 phiên thay vì toàn bộ 7,500 phiên cố định. |
| **3** | **RNG của Probe** | Dùng chính seed của mô hình backbone để xáo trộn tập chia 80/20. | Mỗi mô hình (Seed 42, 7, 999) bị chấm điểm trên 1,500 phiên khác nhau; không thể tính toán paired delta tin cậy. |
| **4** | **Điều kiện Dừng** | Watcher ngầm áp đặt dừng tại 17:00 chiều và ghi nhận `COMPLETED` / `early_stopped=true`. | Đồng hồ thực không phải tiêu chuẩn dừng khoa học; làm sai lệch bản chất hội tụ của thuật toán tối ưu. |
| **5** | **Diễn giải Thống kê** | Gộp $N=5$ seed Sequence với $N=3$ seed khác; dùng thuật ngữ `AP (PR-AUC)` lẫn lộn; diễn giải nhân quả. | Vi phạm đối chứng công bằng $N=3$; AP được tính bằng diện tích dưới đường PR nội suy, không phải PR-AUC xấp xỉ; suy diễn nhân quả chưa có căn cứ. |

---

## 3. NHỮNG DỮ LIỆU ĐƯỢC BẢO TOÀN (WHAT REMAINS USABLE)

Tuyệt đối không xóa bỏ hay tiêu hủy bất kỳ dữ liệu thực nghiệm nào đã thu thập. Các artifact sau đây được bảo toàn nguyên vẹn trong hệ thống lưu trữ và lịch sử Git:

1. **Các backbone đã huấn luyện của `SEQUENCE_ONLY`:**
   - Seed 42 (Epoch 6, Early Stopped)
   - Seed 7 (Epoch 12)
   - Seed 999 (Epoch 12)
   - Seed 1337 (Epoch 12)
   - Seed 2024 (Epoch 12)
2. **Backbone đã huấn luyện của `MULTI_VIEW_ALIGNED_VICREG`:**
   - Seed 42 (Epoch 9, Early Stopped tại Epoch 6 tối ưu)
3. **Tiến trình huấn luyện trực tiếp của `MULTI_VIEW_ALIGNED_VICREG` Seed 7:**
   - Đang chạy bình thường trên GPU; các checkpoint `checkpoint_epoch1.pt`, `checkpoint_epoch2.pt`, `checkpoint_epoch3.pt`, `best_checkpoint.pt` được bảo vệ nguyên vẹn.
4. **Các phép đo thăm dò lịch sử (Historical Exploratory Records):**
   - Các chỉ số AP/ROC-AUC cũ của Stage A2 Graph và các probe 80/20 cũ được lưu giữ làm hồ sơ nguồn gốc thực thi (execution provenance), không bị chỉnh sửa hồi tố.
5. **Niêm phong Mật mã Tập Test (`TEST_FIREWALL`):**
   - `TEST_OPENED=false`, `TEST_READ_COUNT=0` được duy trì tuyệt đối.

---

## 4. NHỮNG GÌ PHẢI TÍNH TOÁN LẠI (WHAT MUST BE RECOMPUTED)

Để bảo đảm tính công bằng tuyệt đối giữa các mô hình mà không cần phải huấn luyện lại backbone tốn hàng chục giờ GPU:

> [!IMPORTANT]
> **QUY TRÌNH LINEAR PROBE CHUẨN HÓA V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`):**
> 1. Trích xuất biểu diễn đóng băng trên **toàn bộ 35,000 phiên Train** từ backbone đã huấn luyện.
> 2. Lấy nhãn dị thường của tập Train từ kho nhãn kiểm chứng đã khóa ([`hdfs_probe_labels_train.pt`](file:///D:/Research/experiments/runs/data/vault/hdfs_probe_labels_train.pt)).
> 3. Huấn luyện bộ phân loại tuyến tính dung lượng kiểm soát ($W \in \mathbb{R}^{128 	imes 1}$, AdamW, lr=1e-2, weight decay=1e-4, 50 epochs, batch size=256) **chỉ trên biểu diễn Train**.
> 4. Đóng băng trọng số bộ phân loại tuyến tính.
> 5. Trích xuất biểu diễn đóng băng trên **toàn bộ 7,500 phiên Validation cố định** (`val_membership_sha256 = 14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a`).
> 6. Đánh giá suy luận trên **100% (7,500/7,500) phiên Validation**.
> 7. Khóa RNG seed của Probe ở giá trị cố định (`10007`), độc lập hoàn toàn với seed của backbone mô hình.

**Đối tượng áp dụng tính toán lại:**
- `SEQUENCE_ONLY`: Seeds 42, 7, 999.
- `MULTI_VIEW_ALIGNED_VICREG`: Seed 42, Seed 7 (sau khi huấn luyện tự nhiên hoàn tất), Seed 999 (sau khi huấn luyện hoàn tất).

---

## 5. NHỮNG GÌ PHẢI HUẤN LUYỆN LẠI MỚI (WHAT MUST BE RETRAINED)

1. **`GRAPH_ONLY_FRESH` (Seeds 42, 7, 999):**
   - Bắt buộc phải huấn luyện mới triển vọng (fresh prospective runs) dưới cùng harness của chiến dịch Nineplus.
   - Cùng trần 12 epoch, cùng điều kiện early stopping (patience=3), cùng phân bổ Train/Val session HDFS, cùng quy trình đo V3 Probe.
   - *Lưu ý: Không thực hiện trong lượt tác vụ hiện tại; chỉ khởi chạy sau khi hoàn tất bảo vệ Seed 7 và V3 được phê duyệt.*
2. **`MULTI_VIEW_ALIGNED_VICREG` Seed 999:**
   - Khởi chạy huấn luyện mới sau khi Seed 7 hoàn thành.

---

## 6. PHÂN LOẠI VAI TRÒ SUY DIỄN (INFERENTIAL ROLE CLASSIFICATION)

### 6.1. Nhóm Khảo sát Bổ trợ (`HISTORICAL_EXPLORATORY_REFERENCE_ONLY` / `SUPPLEMENTARY_EXPLORATORY`)
- **Kết quả Graph-Only từ Stage A2:** Phân loại là `HISTORICAL_EXPLORATORY_REFERENCE_ONLY`. Cung cấp ngữ cảnh kỹ thuật ban đầu, tuyệt đối không đưa vào ma trận quyết định H2 chính thức.
- **Toàn bộ chỉ số AP/ROC-AUC từ Probe 80/20 cũ:** Phân loại là `LEGACY_PROBE_EXPLORATORY_METRIC`.
- **Nhánh Sequence Seed 1337 và Seed 2024:** Phân loại là `SUPPLEMENTARY_EXPLORATORY`. Cung cấp bằng chứng độ bền trên tập mẫu mở rộng $N=5$, nhưng loại khỏi bộ ba đối chứng trực tiếp $N=3$.

### 6.2. Nhóm Đủ điều kiện Xác nhận (`CONFIRMATORY_BACKBONE_ELIGIBLE`)
- **Bộ ba hạt giống chuẩn hóa H2:** Bắt buộc và duy nhất là `Seeds 42, 7, 999` trên cả 3 cấu hình:
  1. `SEQUENCE_ONLY` (Tái sử dụng backbone, đo lại Probe V3)
  2. `GRAPH_ONLY_FRESH` (Huấn luyện mới triển vọng, đo Probe V3)
  3. `MULTI_VIEW_ALIGNED_VICREG` (Seed 42 đo lại Probe V3, Seed 7 tiếp tục huấn luyện, Seed 999 huấn luyện sau)
- **Đánh giá Chống Sụp đổ Biểu diễn của Multi-View Seed 42:**
  - Phương sai quan sát: $	ext{Var}(z) = 0.00997$.
  - Ngưỡng V2: $0.01000$.
  - Phân loại chính thức: `FAIL_UNDER_PREREGISTERED_THRESHOLD`.
  - Không che giấu hay làm giảm nhẹ kết quả này. Tuy nhiên, kết luận cuối cùng của giả thuyết H2 phụ thuộc vào phân phối trên toàn bộ 3 seed, không định đoạt bởi 1 seed đơn lẻ.

---

## 7. KỶ LUẬT NGÔN NGỮ VÀ TUÂN THỦ TRANH LUẬN KHOA HỌC

1. **Thuật ngữ Độ đo:** Sử dụng chuẩn xác `Average Precision (AP)`, không dùng cách viết gộp gây hiểu lầm `AP (PR-AUC)`.
2. **Xóa bỏ các Tuyên bố Nhân quả Hậu nghiệm:**
   - *Không khẳng định:* "Gated Fusion bù đắp thông tin chuỗi", "Tính tuyến tính của HDFS gây ra sự vượt trội của Sequence-only", "VICReg gây ra negative transfer".
   - *Thay thế bằng ngôn ngữ quan sát khách quan:* "Trên tập dữ liệu HDFS dưới giao thức Probe cũ, Sequence-only thể hiện AP cao hơn Multi-view Seed 42"; "Hiện tượng nén phương sai biểu diễn là một giả thuyết giải thích cần được kiểm chứng qua các ablation độc lập".
3. **Biên độ Không thua kém (Non-Inferiority Margin):**
   - Ngưỡng $\delta_{	ext{AP}} \ge -0.02$ được xác định là `AUTHOR_DEFINED_A_PRIORI_PRACTICAL_NONINFERIORITY_MARGIN`.
   - Đây là ngưỡng thực hành do tác giả đề xuất từ thiết kế V2, không phải hằng số phổ quát hay quy chuẩn bắt buộc của toàn ngành. Ngưỡng này được giữ cố định, không điều chỉnh theo kết quả quan sát.
4. **Trạng thái Hiện tại của H2:**
   - `H2_CONFIRMATORY_STATUS = INCOMPLETE_PROTOCOL_REPAIR_IN_PROGRESS`.
   - Tuyệt đối chưa tuyên bố H2 được ủng hộ hay bị bác bỏ ở thời điểm hiện tại.

---

## 8. BẢNG TỔNG HỢP TRẠNG THÁI PROTOCOL

| Cấu hình | Seed | Trạng thái Backbone | Trạng thái Probe | Vai trò Suy diễn H2 |
| :--- | :---: | :--- | :--- | :--- |
| `SEQUENCE_ONLY` | 42 | Đã hoàn tất (Epoch 6) | Cần đo lại Probe V3 | `CONFIRMATORY_BACKBONE_ELIGIBLE` |
| `SEQUENCE_ONLY` | 7 | Đã hoàn tất (Epoch 12) | Cần đo lại Probe V3 | `CONFIRMATORY_BACKBONE_ELIGIBLE` |
| `SEQUENCE_ONLY` | 999 | Đã hoàn tất (Epoch 12) | Cần đo lại Probe V3 | `CONFIRMATORY_BACKBONE_ELIGIBLE` |
| `SEQUENCE_ONLY` | 1337 | Đã hoàn tất (Epoch 12) | Giữ Probe cũ | `SUPPLEMENTARY_EXPLORATORY` |
| `SEQUENCE_ONLY` | 2024 | Đã hoàn tất (Epoch 12) | Giữ Probe cũ | `SUPPLEMENTARY_EXPLORATORY` |
| `GRAPH_ONLY` (Stage A2) | 42, 7, 999 | Checkpoint lịch sử | Probe 80/20 cũ | `HISTORICAL_EXPLORATORY_REFERENCE_ONLY` |
| `GRAPH_ONLY_FRESH` | 42, 7, 999 | **Bắt buộc huấn luyện mới** | Đo Probe V3 | `CONFIRMATORY_BACKBONE_ELIGIBLE` (Tương lai) |
| `MULTI_VIEW_ALIGNED` | 42 | Đã hoàn tất (Epoch 9) | Cần đo lại Probe V3 | `CONFIRMATORY_BACKBONE_ELIGIBLE` |
| `MULTI_VIEW_ALIGNED` | 7 | **Đang huấn luyện tự nhiên** | Đo Probe V3 sau khi xong | `CONFIRMATORY_BACKBONE_ELIGIBLE` |
| `MULTI_VIEW_ALIGNED` | 999 | Chờ thực thi | Đo Probe V3 sau khi xong | `CONFIRMATORY_BACKBONE_ELIGIBLE` |

---
*Báo cáo được lập phục vụ công tác kiểm toán phương pháp luận, tuân thủ nguyên tắc trung thực khoa học khách quan và không làm thay đổi các artifact huấn luyện đang chạy.*

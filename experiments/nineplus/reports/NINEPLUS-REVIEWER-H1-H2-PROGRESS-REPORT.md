# BÁO CÁO TIẾN ĐỘ THỰC NGHIỆM GỬI REVIEWER
## TỔNG KẾT TOÀN BỘ TIẾN TRÌNH KIỂM CHỨNG GIẢ THUYẾT H1 VÀ H2 (CHIẾN DỊCH NINEPLUS)
### TỪ KHỞI ĐẦU ĐẾN THỜI ĐIỂM HOÀN TẤT BỘ BA XÁC NHẬN ĐA GÓC NHÌN

**Kính gửi:** Quý Reviewer  
**Đề tài:** Nghiên cứu phát hiện bất thường nhật ký hệ thống sử dụng biểu diễn học tự giám sát đa góc nhìn (Multi-View Self-Supervised Learning)  
**Mã chiến dịch:** `NINEPLUS-EXPERIMENT-CAMPAIGN-V3` (Kế thừa và tu chính từ V1 và V2)  
**Tệp kế hoạch chuẩn hóa:** [`experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json`](file:///D:/Research/experiments/plans/NINEPLUS-EXPERIMENT-CAMPAIGN-V3.json)  
**Thời điểm lập báo cáo:** 2026-09-18 00:20:00 (UTC+7)  
**Nhánh Git thẩm tra:** `fix/thesis-apply-edits` (Origin: `Minhlike/Chuyende`)  
**Môi trường thực thi:** NVIDIA GeForce RTX 3050 Ti Laptop GPU (4.0 GB VRAM), AMD Ryzen / Intel Core i5, Python 3.12.8 (`.venv-stage-a2-cuda`), PyTorch 2.6.0+cu124, CUDA 12.4.

---

## 1. Tuyên bố Bất biến và Ranh giới Phương pháp luận (Epistemic Invariants)

Báo cáo này được lập nhằm cung cấp cho Reviewer bức tranh toàn cảnh, minh bạch và có thể kiểm chứng độc lập về toàn bộ tiến trình thực nghiệm kiểm chứng hai giả thuyết khoa học cốt lõi của đề tài: **Giả thuyết H1** và **Giả thuyết H2**, bắt đầu từ các thử nghiệm kỹ thuật ban đầu cho tới thời điểm hoàn tất bộ ba hạt giống xác nhận đa góc nhìn.

Mọi số liệu trong báo cáo tuân thủ tuyệt đối các nguyên tắc phương pháp luận:

1. *Niêm phong tập Test (`TEST_OPENED=false`, `TEST_READ_COUNT=0`):* Tập Test HDFS được niêm phong mật mã tuyệt đối trong toàn bộ chiến dịch. Chưa có bất kỳ lần đọc hay tính toán nào trên tập Test. Toàn bộ 7.500 phiên (119.531 sự kiện đồ thị thời gian) được thẩm định thuộc về tập Kiểm định cố định (Validation split).
2. *Đóng băng bản thảo gốc (`MASTER_CHANGED=false`):* Các tệp luận văn chính (`Chuyên đề chuyên sâu.docx` và `.pdf`) được giữ nguyên vẹn, không chỉnh sửa số liệu hồi tố khi chưa hoàn tất nghiệm thu toàn bộ các nhánh.
3. *Kỷ luật phân loại suy diễn:* Báo cáo phân định rạch ròi giữa số liệu đo đạc trực tiếp (`OBSERVED_RESULT`), số liệu thống kê suy diễn (`DERIVED_RESULT`) và giả thuyết giải thích (`HYPOTHESIS`), loại bỏ các kết luận nhân quả vượt quá bằng chứng đo lường thực tế.

---

## 2. Bản chất Khoa học và Khung Kiểm chứng của Giả thuyết H1 và H2

### 2.1. Giả thuyết H1: Tính Trung thực Ngữ nghĩa Tham số (Parameter Semantic Fidelity)
- **Câu hỏi nghiên cứu:** Khe tham số động (`param_slots`: danh mục địa chỉ IP nội bộ/công khai, kích thước khối byte) có được lưu giữ tuyến tính trong không gian biểu diễn ẩn $z \in \mathbb{R}^{128}$ sau quá trình tiền huấn luyện tự giám sát qua hàm mất mát Masked Parameter Prediction ($L_{MPP}$) hay không?
- **Khung kiểm định trực tiếp:**
  - Bộ phân loại tuyến tính mỏng ($W \in \mathbb{R}^{128 \times C}$, zero hidden layers) huấn luyện trên biểu diễn đóng băng để khôi phục lớp tham số động (`param_targets`).
  - **Chỉ số trực tiếp chính:** `Macro-F1` trên bài toán phân loại danh mục tham số (để xử lý mất cân bằng lớp).
  - **Chỉ số tiện ích thứ cấp:** `Average Precision (AP)` trên bài toán phát hiện bất thường hạ nguồn (`HDFS_ANOMALY_LABEL`).
  - **Kiểm thử cắt bỏ đầu vào đóng băng (`FROZEN_INPUT_MASKING_ABLATION`):** Đánh giá mô hình khi che toàn bộ tham số (`param_slots = None`) so với khi mở tham số.
- **Ranh giới nhận thức:** Chứng minh các tham số động cung cấp thông tin bảo toàn tuyến tính trong vector biểu diễn; không tự suy diễn rằng cơ chế học có tham số vượt trội toàn diện trên mọi phân bố khác.

### 2.2. Giả thuyết H2: Tính Bổ trợ Đa Góc nhìn và Chống Suy thoái Chuyển giao (Multi-View Complementarity & Negative Transfer Prevention)
- **Câu hỏi nghiên cứu:** Việc căn chỉnh và dung hợp đa góc nhìn giữa Chuỗi sự kiện (Sequence View) và Đồ thị thời gian (Temporal Graph View) qua hàm mất mát căn chỉnh VICReg và cổng dung hợp động (Gated Dynamic Fusion) có đạt hiệu năng phát hiện bất thường không thua kém (non-inferior, biên sai số $\delta_{margin} \ge -0.02$) hoặc vượt trội so với các mô hình đơn góc nhìn độc lập (`SEQUENCE_ONLY` và `GRAPH_ONLY`) dưới cùng điều kiện triển vọng mà không bị sụp đổ biểu diễn ($\text{Var}(z) \ge 0.01000$) hay không?
- **Ba kiến trúc tham gia kiểm định:**
  1. `SEQUENCE_ONLY`: Transformer Encoder (4 layers, $d=128$, hàm mất mát $L_{seq} = 1.0 L_{MEP} + 1.0 L_{MPP} + 0.1 L_{time}$).
  2. `GRAPH_ONLY`: Mạng nơ-ron đồ thị thời gian TGN ($L_{graph} = 1.0 L_{rel} + 1.0 L_{node} + 0.1 L_{time}$).
  3. `MULTI_VIEW_ALIGNED_VICREG`: Kiến trúc kết hợp đa góc nhìn ($L_{StageA} = L_{seq} + L_{graph} + 1.0 L_{VICReg} + 1.0 L_{fuse\_rec}$).
- **Tập hạt giống xác nhận chính thức (Confirmatory Triad):** `Seeds [42, 7, 999]` (tổng cộng $3 \times 3 = 9$ lượt chạy xác nhận).
- **Quy tắc phán quyết đăng ký trước (Pre-registered Decision Rule):**
  - $\Delta_{vs\_seq} = \text{AP}_{mv} - \text{AP}_{seq}$
  - $\Delta_{vs\_graph} = \text{AP}_{mv} - \text{AP}_{graph}$
  - Điều kiện tiên quyết: Phương sai ẩn $\text{Var}(z_{mv}) \ge 0.01000$.
  - **`SUPPORTED` (Được ủng hộ):** $\Delta_{vs\_seq} \ge -0.02$ VÀ $\Delta_{vs\_graph} \ge -0.02$, đồng thời vượt trội có ý nghĩa thống kê ($\Delta > 0$, khoảng tin cậy 95% không chứa 0) trên ít nhất 1 mô hình đơn góc nhìn.
  - **`PARTIALLY_SUPPORTED` (Ủng hộ một phần):** Thỏa mãn không thua kém cả 2 mô hình đơn góc nhìn ($\Delta \ge -0.02$) mà không bị sụp đổ phương sai, nhưng không vượt trội hoàn toàn cả hai.
  - **`FALSIFIED` (Bác bỏ):** Thua kém đáng kể một trong hai mô hình ($\Delta < -0.02$) HOẶC sụp đổ phương sai ($\text{Var}(z) < 0.01$).
  - **`INCONCLUSIVE` (Chưa thể kết luận):** Khoảng tin cậy cắt qua mốc biên độ $-0.02$.

---

## 3. Nhật ký Tiến trình Thực thi Chiến dịch từ Khởi đầu đến Nay (Campaign Chronology)

### Giai đoạn 0: Thiết kế Khung Hợp đồng Thực nghiệm (Commit [`0df87c2`](https://github.com/Minhlike/Chuyende/commit/0df87c2))
- Ban hành Kế hoạch Chiến dịch V1 và V2 (`NINEPLUS-EXPERIMENT-CAMPAIGN-V2.json`).
- Thiết lập tường lửa kiểm thử (`TEST_FIREWALL`), cấu hình môi trường phần cứng Sweet Spot (`scripts/set_training_sweetspot.ps1`) để tối ưu hóa việc huấn luyện dài ngày trên GPU RTX 3050 Ti Laptop.
- Tách bạch dứt điểm yêu cầu kỹ thuật công nghệ (ER1: VRAM < 550 MB, độ trễ suy luận) ra khỏi câu hỏi khoa học thuần túy H1 và H2.

### Giai đoạn 1: Thử nghiệm Tính Khả thi Kỹ thuật (Phase 1 Technical Pilots - Commit [`3e0bcef`](https://github.com/Minhlike/Chuyende/commit/3e0bcef))
- Chạy thử nghiệm kỹ thuật ngắn hạn (1 đến 2 epochs, Seed 42) cho cả 3 kiến trúc:
  - `PILOT_SEQUENCE_ONLY`: 2 epochs, VRAM đỉnh 184.3 MB, thời gian 2.1 phút/epoch.
  - `PILOT_GRAPH_ONLY`: 2 epochs, VRAM đỉnh 1,255.1 MB, thời gian 190.2 phút/epoch.
  - `PILOT_MULTI_VIEW_ALIGNED`: 2 epochs, VRAM đỉnh 277.6 MB, thời gian 23.5 phút/epoch.
- Kết luận Pilot: Cả 3 kiến trúc vận hành ổn định trên GPU 4.0 GB VRAM, tuyệt đối 0 lỗi `NaN` và 0 lỗi `Inf`. Khóa mã nguồn bước vào giai đoạn chạy xác nhận.

### Giai đoạn 2: Hoàn tất 100% Nhánh Sequence-Only (Commit [`47e4ad6`](https://github.com/Minhlike/Chuyende/commit/47e4ad6))
- Huấn luyện hoàn chỉnh 5 hạt giống của nhánh `SEQUENCE_ONLY`:
  - 3 hạt giống xác nhận chính thức: Seed 42 (dừng tại Epoch 6), Seed 7 (chạm trần Epoch 12), Seed 999 (chạm trần Epoch 12).
  - 2 hạt giống khảo sát mở rộng: Seed 1337 và Seed 2024.
- Kết quả bộ ba xác nhận:
  - $\text{AP} = \mathbf{0.8687 \pm 0.0700}$ (`[0.8994, 0.9179, 0.7887]`)
  - $\text{ROC-AUC} = \mathbf{0.9740 \pm 0.0413}$ (`[0.9973, 0.9984, 0.9263]`)
  - $\text{Var}(z) = \mathbf{0.1130 \pm 0.0284}$ (100% hạt giống vượt xa ngưỡng $0.01000$).
- Nghiệm thu: Toàn bộ backbone được lưu trữ an toàn, phục vụ đối chứng H2 và kiểm định H1.

### Giai đoạn 3: Kiểm toán Phương pháp luận và Ban hành Bản Tu chính V3 (Commit [`4df9666`](https://github.com/Minhlike/Chuyende/commit/4df9666))
Trong lúc mô hình `MULTI_VIEW_ALIGNED` Seed 7 đang huấn luyện, quá trình rà soát độc lập đã phát hiện các điểm nghẽn phương pháp luận trong kế hoạch V2:
1. *Khiếm khuyết nhánh Graph:* Số liệu đối chứng của `GRAPH_ONLY` được trích xuất từ các checkpoint Stage A2 lịch sử, không được huấn luyện cùng pipeline triển vọng của Nineplus.
2. *Khiếm khuyết Linear Probe:* Giao thức probe cũ chia 80/20 nội bộ tập Validation và phụ thuộc vào RNG seed của mô hình, khiến các mô hình bị đánh giá trên các tập con khác nhau.
3. *Nguy cơ can thiệp giờ hành chính:* Script watcher ngầm có điều kiện dừng tiến trình lúc 17:00 chiều và đánh dấu giả mạo `early_stopped=true`.
4. *Suy diễn nhân quả chưa có căn cứ:* Báo cáo cũ chứa một số suy đoán nhân quả vượt quá bằng chứng thực nghiệm.

**Các quyết sách khắc phục tại Tu chính V3:**
- Bảo vệ tuyệt đối tiến trình Seed 7 đang chạy, cấm mọi hành vi dừng cưỡng chế.
- Khóa quy tắc dừng: Chỉ dừng khi thỏa mãn `patience=3` hoặc chạm trần 12 epochs. Nếu tạm dừng máy thì ghi nhận trạng thái `ADMINISTRATIVE_PAUSE`, không ngụy tạo dừng sớm.
- Chuẩn hóa Giao thức Probe V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`): Huấn luyện probe trên 35.000 phiên Train cố định với RNG seed độc lập (`10007`), suy luận trên 100% (7.500 phiên) Validation cố định.
- Yêu cầu huấn luyện mới triển vọng nhánh `GRAPH_ONLY_FRESH` (Seeds 42, 7, 999).

### Giai đoạn 4: Huấn luyện Trọn vẹn Bộ Ba Xác nhận Multi-View (Multi-View Confirmatory Triad)
Quá trình huấn luyện 3 hạt giống xác nhận của `MULTI_VIEW_ALIGNED_VICREG` đã được triển khai nghiêm ngặt:

1. *Seed 42 (Commit [`7bdcade`](https://github.com/Minhlike/Chuyende/commit/7bdcade)):*
   - Huấn luyện 9 epochs; kích hoạt Early Stopping tại Epoch 9. Cực tiểu Validation Loss tại **Epoch 6** (`49.1768`).
   - Legacy Probe: $\text{AP} = 0.7032$, $\text{ROC-AUC} = 0.9319$.
   - Phương sai không gian ẩn: $\text{Var}(z) = 0.00997$. Xếp loại: `FAIL_UNDER_PREREGISTERED_THRESHOLD` do sát dưới ngưỡng $0.01000$.
2. *Seed 7 (Được bảo vệ chạy tự nhiên qua đêm):*
   - Huấn luyện 6 epochs; kích hoạt Early Stopping tại Epoch 6. Cực tiểu Validation Loss tại **Epoch 3** (`49.0099`).
   - Legacy Probe: $\text{AP} = 0.6082$, $\text{ROC-AUC} = 0.8899$.
   - Phương sai không gian ẩn: $\text{Var}(z) = 0.012643$. Xếp loại: **`PASS_OVER_PREREGISTERED_THRESHOLD`** ($\ge 0.01000$).
3. *Seed 999 (Hoàn tất lúc 00:10 ngày 18/09/2026 - Commit [`0cc1752`](https://github.com/Minhlike/Chuyende/commit/0cc1752)):*
   - Huấn luyện qua các giai đoạn ban ngày và ban đêm, trải qua 2 lần tạm dừng hành chính bảo toàn checkpoint.
   - Hoàn thành 7 epochs; kích hoạt Early Stopping tự nhiên tại Epoch 7. Cực tiểu Validation Loss tại **Epoch 4** (`48.7659` - kỷ lục tối ưu của Seed 999).
   - Legacy Probe: $\text{AP} = 0.6855$, $\text{ROC-AUC} = 0.8580$.
   - Phương sai không gian ẩn: $\text{Var}(z) = 0.014419$. Xếp loại: **`PASS_OVER_PREREGISTERED_THRESHOLD`** ($\ge 0.01000$).
   - Checkpoint và biên bản nghiệm thu: [`best_checkpoint.pt`](file:///D:/Research/experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed999_1789541331/best_checkpoint.pt) và [`RUN-MANIFEST.json`](file:///D:/Research/experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed999_1789541331/RUN-MANIFEST.json).

---

## 4. Bảng Số liệu Đối chứng Tổng hợp Hiện tại của Hai Giả thuyết

### 4.1. Tiến độ và Trạng thái Kiểm chứng Giả thuyết H1 (Parameter Semantic Fidelity)
- **Tình trạng thực thi:** Các backbone của nhánh `SEQUENCE_ONLY` đã hoàn tất huấn luyện và đóng băng 100%.
- **Dữ liệu nhãn tham số:** Nhãn tham số `param_targets` được lưu trữ tại `hdfs_ssl_train.pt` và `hdfs_ssl_val.pt`, tách biệt với kho nhãn phát hiện bất thường hạ nguồn (`hdfs_probe_labels_train.pt` và `hdfs_probe_labels_val.pt`).
- **Kết quả sơ bộ quan sát:** Trong quá trình tiền huấn luyện Stage A, hàm mất mát dự đoán tham số $L_{MPP}$ giảm ổn định từ $\approx 0.50$ xuống $\approx 0.02$ đến $0.05$, cho thấy mô hình học được mối tương quan giữa chuỗi sự kiện và thuộc tính tham số.
- **Bước hoàn thiện H1:** Kiểm toán độ mịn mục tiêu và thực hiện kiểm thử cắt bỏ `FROZEN_INPUT_MASKING_ABLATION`.

### 4.2. Bảng Đối chứng Ma trận Hạt giống Xác nhận Giả thuyết H2 ($N=3$)

*Bảng 1. Ma trận đối chứng chi tiết từng hạt giống xác nhận của Giả thuyết H2*

| Kiến trúc Mô hình | Seed | Epoch Dừng (Tối ưu) | Phương sai $\text{Var}(z)$ | Đạt chuẩn $\text{Var}(z)$ | Legacy Probe AP | Legacy Probe ROC-AUC | Trạng thái Nghiệm thu |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`SEQUENCE_ONLY`** | 42 | Ep 6 (Ep 3) | 0.0935 | ĐẠT (PASS) | 0.8994 | 0.9973 | `BACKBONE_PRESERVED` |
| (Đơn chuỗi sự kiện) | 7 | Ep 12 (Ep 11) | 0.0999 | ĐẠT (PASS) | 0.9179 | 0.9984 | `BACKBONE_PRESERVED` |
| | 999 | Ep 12 (Ep 12) | 0.1455 | ĐẠT (PASS) | 0.7887 | 0.9263 | `BACKBONE_PRESERVED` |
| **Trung bình Sequence** | **$N=3$** | **N/A** | **`0.1130 ± 0.0284`** | **100% PASS** | **`0.8687 ± 0.0700`** | **`0.9740 ± 0.0413`** | **Hoàn tất 100%** |
| | | | | | | | |
| **`MULTI_VIEW_ALIGNED`**| 42 | Ep 9 (Ep 6) | 0.00997 | KHÔNG ĐẠT (FAIL) | 0.7032 | 0.9319 | `BACKBONE_PRESERVED` |
| (Đa góc nhìn liên kết) | 7 | Ep 6 (Ep 3) | 0.01264 | ĐẠT (PASS) | 0.6082 | 0.8899 | `BACKBONE_PRESERVED` |
| | 999 | Ep 7 (Ep 4) | 0.01442 | ĐẠT (PASS) | 0.6855 | 0.8580 | `BACKBONE_PRESERVED` |
| **Trung bình Multi-View** | **$N=3$** | **N/A** | **`0.0123 ± 0.0022`** | **2/3 PASS** | **`0.6656 ± 0.0505`** | **`0.8933 ± 0.0371`** | **Hoàn tất 100%** |
| | | | | | | | |
| *`GRAPH_ONLY` (Lịch sử)* | 42 | Stage A2 (Ep 1) | 0.0072 | KHÔNG ĐẠT (FAIL) | 0.7090 | 0.8053 | `HISTORICAL_REFERENCE` |
| *(Đơn đồ thị tham chiếu)*| 7 | Stage A2 (Ep 12) | 0.0727 | ĐẠT (PASS) | 0.6178 | 0.7516 | `HISTORICAL_REFERENCE` |
| | 999 | Stage A2 (Ep 12) | 0.0738 | ĐẠT (PASS) | 0.6815 | 0.8857 | `HISTORICAL_REFERENCE` |
| *Trung bình Graph Lịch sử*| *$N=3$* | *N/A* | *`0.0512 ± 0.0381`* | *2/3 PASS* | *`0.6694 ± 0.0468`* | *`0.8142 ± 0.0675`* | *Chỉ để đối chứng* |

---

## 5. Báo cáo Nhận định Khoa học Khách quan Dành cho Reviewer

Dựa trên các số liệu thực nghiệm đo đạc thực tế, tác giả báo cáo trung thực với Reviewer ba phát hiện học thuật quan trọng:

*Thứ nhất, về sự tương quan giữa Multi-View và Graph-Only:*  
Dưới giao thức probe cũ, mô hình đa góc nhìn `MULTI_VIEW_ALIGNED_VICREG` đạt ROC-AUC trung bình $0.8933 \pm 0.0371$, cao hơn so với mô hình đơn đồ thị lịch sử ($0.8142 \pm 0.0675$). Tuy nhiên, do mô hình đơn đồ thị lịch sử không phải là mô hình đối chứng triển vọng tương thích (unmatched exploratory reference), so sánh này không cô lập được tác động của cơ chế dung hợp đa góc nhìn. Về chỉ số AP, hai nhánh đạt mức tương đương ($0.6656$ so với $0.6694$).

*Thứ hai, về khoảng cách giữa Multi-View và Sequence-Only trên tập HDFS:*  
Mô hình đơn chuỗi `SEQUENCE_ONLY` duy trì hiệu năng vượt trội trên tập dữ liệu HDFS cả về AP ($0.8687$ so với $0.6656$) và ROC-AUC ($0.9740$ so với $0.8933$). Số liệu thực tế không hỗ trợ kỳ vọng lạc quan ban đầu rằng mô hình đa góc nhìn sẽ vượt trội hơn mô hình chuỗi thuần túy trên bài toán này. Tác giả bảo toàn kết quả này như một phát hiện thực nghiệm khách quan, không che giấu hay điều chỉnh số liệu.

*Thứ ba, về hiện tượng nén phương sai biểu diễn ẩn ($\text{Var}(z)$):*  
Mô hình đa góc nhìn thể hiện phương sai biểu diễn ẩn thấp hơn. Tác động điều hòa liên quan đến VICReg là một giả thuyết giải thích hợp lý; tuy nhiên đóng góp cụ thể của từng số hạng VICReg chưa được cô lập bằng kiểm thử cắt bỏ đối chứng. Đây là phát hiện thực nghiệm có giá trị để thảo luận sâu trong luận án.

---

## 6. Lộ trình Kế tiếp Hoàn tất Toàn bộ Ma trận Kiểm chứng

Để hoàn thiện trọn vẹn báo cáo kiểm chứng H1 và H2 đáp ứng yêu cầu thẩm định khắt khe của Reviewer:

```
[HIỆN TẠI: ĐÃ HOÀN THÀNH 100%]
Đã hoàn thành và kiểm định toàn vẹn 6/6 Confirmatory Backbones:
- SEQUENCE_ONLY: Seeds 42, 7, 999 (Hoàn tất)
- MULTI_VIEW_ALIGNED: Seeds 42, 7, 999 (Hoàn tất)
                          │
                          ▼
[BƯỚC KẾ TIẾP 1: TÍNH TOÁN PROBE CHUẨN HÓA V3]
Thực thi quy trình TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE:
- Huấn luyện probe trên 35,000 phiên Train (RNG seed độc lập = 10007).
- Đánh giá trên 100% (7,500 phiên) Validation cố định.
- Chạy đồng bộ trên cả 6 backbone đã có để thay thế toàn bộ Legacy Probe metrics.
- Đánh giá chỉ số Macro-F1 khôi phục tham số cho Giả thuyết H1.
                          │
                          ▼
[BƯỚC KẾ TIẾP 2: HUẤN LUYỆN GRAPH_ONLY_FRESH]
Khởi chạy huấn luyện mới triển vọng nhánh GRAPH_ONLY_FRESH (Seeds 42, 7, 999):
- Dưới cùng harness, epoch ceiling = 12, early stopping patience = 3.
- Xóa bỏ hoàn toàn sự phụ thuộc vào checkpoint Stage A2 lịch sử.
                          │
                          ▼
[BƯỚC KẾ TIẾP 3: TỔNG HỢP MA TRẬN PHÁN QUYẾT H1 & H2]
- Tính toán phân phối hiệu năng Paired Deltas (mean delta, sample std, 95% CI).
- Áp dụng Decision Rule đã đăng ký trước để đưa ra phán quyết chính thức cho H1 và H2.
```

Tác giả kính trình Reviewer bản báo cáo tiến độ chi tiết này và sẵn sàng thực thi các bước tính toán tiếp theo theo quy chuẩn đã cam kết.

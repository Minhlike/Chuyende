# Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công

**Đơn vị:** Học viện Kỹ thuật Mật mã  
**Học phần:** Chuyên đề chuyên sâu  
**Đối tượng nghiên cứu:** Không gian biểu diễn đặc trưng vector/đa tạp $\mathbf{z} \in \mathbb{R}^d$ từ chuỗi sự kiện log an ninh  
**Hàm ánh xạ trích xuất:** $f_\theta : \mathcal{L}_{1:t} \to \mathbf{z}_t$  

---

## 1. TÀI LIỆU CHUYÊN ĐỀ CHÍNH THỨC

| Văn bản | Định dạng | Quy mô | Mã băm SHA-256 kiểm chứng |
| :--- | :---: | :---: | :--- |
| **Bản thảo Chuyên đề (PDF)** | [PDF](Chuyên%20đề%20chuyên%20sâu.pdf) | **121 trang** | `a4a347ea159043e8ab0dd308f3ad9ccd5d06369062c58e6f4a23deaf1a6e5052` |
| **Bản thảo Master (DOCX)** | [DOCX](Chuyên%20đề%20chuyên%20sâu.docx) | 8.77 MB | `3a6a2be313154654c4004e687d30357a4bb3c5e0e5d612083a93b46f21559704` |
| **Hướng dẫn chạy & xác minh** | [Markdown](HUONG_DAN_CHAY_VA_XAC_MINH.md) | Tóm tắt 2 phút | *Dành cho Giảng viên / Hội đồng phản biện* |
| **Tái lập độc lập cho sinh viên** | [Markdown](manual_reproduction/README.md) | PowerShell tự động | *Chạy độc lập trên máy trạm cá nhân* |
| **Chỉ mục thực nghiệm chuẩn** | [CSV](experiments/experiment_index.csv) | 18 cột đối soát | *Tra cứu toàn bộ mô hình và kiểm định* |
| **Báo cáo phòng sạch đã nghiệm thu** | [Markdown](cleanroom/CLEANROOM-REPORT.md) | Bằng chứng độc lập | *Đạt chuẩn CLEAN_ROOM_PASS = true* |

---

## 2. TỔNG QUAN ĐỀ TÀI VÀ ĐÓNG GÓP KỸ THUẬT

Chuyên đề tập trung giải quyết bài toán biểu diễn dữ liệu log phục vụ phát hiện tấn công mạng, bảo toàn ngữ nghĩa an ninh và cấu trúc quan hệ thực thể, đồng thời tuân thủ nghiêm ngặt tính quy nạp theo dòng thời gian nhân quả:

1. **Kiến trúc biểu diễn đa góc nhìn (Multi-View Representation):**
   - *Góc nhìn tuần tự (Sequence View):* Mạng Transformer Encoder xử lý đồng thời chuỗi sự kiện cú pháp và các tham số động đa khe (`d_model=128`, 4 layers, 4 heads).
   - *Góc nhìn đồ thị động (Temporal Graph View):* Bộ mã hóa đồ thị thời gian tích hợp bộ nhớ `GRUCell` và hàm nhúng thời gian liên tục $\phi(\Delta t)$, bảo toàn quan hệ tương tác giữa các thực thể hệ thống.
   - *Hòa trộn dựa trên cổng độ tin cậy động (Gated Fusion):* Mạng cổng MLP tự động cân bằng đóng góp giữa chuỗi cú pháp và cấu trúc đồ thị.

2. **Bảo tồn tham số động có nhận thức an ninh (Security-Aware Dynamic Parameter Preservation):**
   - Lược đồ phân loại kiểu dữ liệu an ninh (IP nội bộ/ngoại vi, cổng dịch vụ, đường dẫn hệ điều hành trọng yếu, mã tiến trình).
   - Cơ chế tạo mã giả danh nhất quán theo phiên dựa trên hàm băm HMAC có khóa ngắn hạn, triệt tiêu nguy cơ suy diễn định danh người dùng.

3. **Giao thức phân chia dữ liệu nhân quả chống rò rỉ (SPL-HDFS-001):**
   - Phân chia 11,17 triệu dòng log HDFS theo đúng mũi tên thời gian ($\text{Train} < \text{Val} < \text{Test}$).
   - Loại bỏ triệt để các phiên vắt ngang ranh giới chuyển tiếp (purging cross-boundary sessions).
   - Ngân sách xác nhận độc lập: 35.000 phiên Train, 7.500 phiên Validation; tập Test giữ nguyên trạng thái niêm phong bảo vệ tuyệt đối (`TEST_OPENED=false`, `TEST_READ_COUNT=0`).

---

## 3. KẾT QUẢ THỰC NGHIỆM CHÍNH (NINEPLUS V3 STANDARDIZED)

Toàn bộ mô hình được đánh giá thông qua giao thức Đầu dò Tuyến tính Đóng băng V3 (`TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`): Đóng băng 100% trọng số backbone, huấn luyện đầu dò tuyến tính mỏng ($W \in \mathbb{R}^{128 \times 1}$) trên 35.000 vector Train, và đo kiểm hiệu năng phát hiện bất thường trên 7.500 vector Validation:

| Kiến trúc | Seed | Best Val Loss | Internal Probe (AP / ROC-AUC) | Frozen Linear Probe V3 (AP / ROC-AUC) | Trạng thái bằng chứng |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SEQUENCE_ONLY** | 42 | `0.0092` | 0.8994 / 0.9973 | **1.0000 / 1.0000** | COMPLETED (Có sẵn trong Git) |
| **SEQUENCE_ONLY** | 7 | `0.0063` | 0.9179 / 0.9984 | **1.0000 / 1.0000** | COMPLETED (Có sẵn trong Git) |
| **SEQUENCE_ONLY** | 999 | `0.0073` | 0.7887 / 0.9263 | **1.0000 / 1.0000** | COMPLETED (Có sẵn trong Git) |
| **MULTI_VIEW_ALIGNED** | 42 | `49.1768` | 0.7032 / 0.9319 | **0.7604 / 0.9946** | COMPLETED (Có sẵn trong Git) |
| **MULTI_VIEW_ALIGNED** | 7 | `49.0099` | 0.6082 / 0.8899 | **0.6309 / 0.8081** | RESULT_JSON_ONLY_IN_GIT |
| **MULTI_VIEW_ALIGNED** | 999 | `48.7659` | 0.6855 / 0.8580 | **0.5911 / 0.7693** | RESULT_JSON_ONLY_IN_GIT |
| **GRAPH_ONLY** | 42, 7, 999 | `5.71`–`6.08` | 0.61–0.71 / 0.75–0.88 | *(Chưa đánh giá V3)* | HISTORICAL_REF_PENDING_AUDIT |

*Chi tiết đối soát từng dòng xem tại:* [`experiments/experiment_index.csv`](experiments/experiment_index.csv).

---

## 4. CẤU TRÚC THƯ MỤC HỆ THỐNG

```text
├── Chuyên đề chuyên sâu.pdf        # Bản thảo PDF chính thức (121 trang)
├── Chuyên đề chuyên sâu.docx       # Bản thảo Word Master (606 công thức OMML)
├── HUONG_DAN_CHAY_VA_XAC_MINH.md   # Cẩm nang 2 phút dành cho Giảng viên / Hội đồng
├── requirements-lock.txt           # Khóa phụ thuộc chính thức (kèm CUDA 12.4 index)
├── pyproject.toml                  # Cấu hình gói và metadata cài đặt
│
├── src/research_agent/             # Toàn bộ mã nguồn thư viện nghiên cứu
│   ├── experiments/                # Triển khai mô hình Transformer, Graph GNN, Fusion
│   ├── composition/                # Trình xuất bản và tích hợp công thức OMML
│   ├── verification/               # Bộ thẩm định chỉ số, bất biến, thống kê
│   └── visuals/                    # Quản lý đồ họa và bảng biểu khoa học
│
├── scripts/                        # Kịch bản thực thi và kiểm định chuẩn mực
│   ├── gpu_smoke_test.py           # Kiểm tra môi trường GPU và cờ xác định CUDA
│   ├── evaluate_nineplus_v3.py     # Bộ đánh giá đầu dò tuyến tính đóng băng V3
│   ├── run_nineplus_confirmatory.py# Huấn luyện mô hình xác nhận độc lập
│   ├── provision_cleanroom_artifacts.py # Nạp và đối soát mã băm artifact ngoại vi
│   └── validate_experiment_index.py# Kiểm tra tính toàn vẹn của experiment_index.csv
│
├── manual_reproduction/            # Thư mục thực nghiệm độc lập cho sinh viên
│   ├── README.md                   # Hướng dẫn chi tiết từng bước
│   ├── run_manual_sequence42.ps1   # Kịch bản PowerShell tự động (~13.6 phút)
│   ├── MANUAL_RUN_SUMMARY.txt      # Báo cáo tóm tắt đối soát kết quả
│   └── screenshots/                # Ảnh chụp màn hình console thực tế
│
├── cleanroom/                      # Bộ bằng chứng kiểm thử phòng sạch độc lập
│   ├── CLEANROOM-REPORT.md         # Báo cáo chi tiết thẩm định môi trường sạch
│   ├── ARTIFACT_PROVISIONING_REPORT.json # Đối soát 7/7 artifact ngoại vi
│   ├── commands.log                # Toàn bộ lệnh thực thi đã chạy
│   └── V3-PROBE-RESULT.json        # Kết quả đánh giá hạ nguồn V3 độc lập
│
├── experiments/                    # Hồ sơ thực nghiệm khoa học
│   ├── experiment_index.csv        # Bảng chỉ mục 18 cột đối soát toàn bộ mô hình
│   └── nineplus/                   # Manifest và bằng chứng V3 (JSON)
│
└── tests/                          # Bộ kiểm thử tự động pytest (50 tests pass)
```

---

## 5. HƯỚNG DẪN KIỂM CHỨNG NHANH (QUICK VERIFICATION)

Giảng viên hoặc người phản biện có thể kiểm chứng toàn bộ hệ thống qua 3 lệnh ngắn gọn:

1. **Kiểm tra phần cứng và môi trường tính toán:**
   ```powershell
   $env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
   python scripts/gpu_smoke_test.py
   ```
   *Kỳ vọng:* `[PASS] GPU Smoke Test Passed 100% (Zero Model Training)` (Exit Code 0).

2. **Kiểm tra tính nhất quán của bảng chỉ mục thực nghiệm:**
   ```powershell
   python scripts/validate_experiment_index.py
   ```
   *Kỳ vọng:* `[VALIDATOR-PASS] 100% records in experiment_index.csv match source JSON artifacts!` (Exit Code 0).

3. **Tái lập kết quả đánh giá hạ nguồn V3 (AP = 1.0000, ROC-AUC = 1.0000):**
   ```powershell
   $env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
   python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42
   ```
   *Kỳ vọng:* Trích xuất biểu diễn và in ra `AP=1.0000 | ROC-AUC=1.0000` trong ~15 giây.

*Xem chi tiết hướng dẫn đầy đủ tại:* [`HUONG_DAN_CHAY_VA_XAC_MINH.md`](HUONG_DAN_CHAY_VA_XAC_MINH.md).

---

## 6. TUYÊN BỐ VỀ ARTIFACT NGOẠI VI VÀ BẢN CLONE SẠCH

> [!CAUTION]
> **Trạng thái kho lưu trữ ngoại vi:** `PUBLIC_CLEAN_CLONE_READY = false`  
> Kho lưu trữ mở Zenodo/OSF phục vụ xuất bản công khai đang ở trạng thái `OPEN` chờ thủ tục xuất xưởng chính thức.

- **Chính sách Git:** Tuân thủ chuẩn mực kỹ thuật phần mềm, toàn bộ tệp nhị phân kích thước lớn (`*.pt`, trọng số mô hình `best_checkpoint.pt`, tập dữ liệu thô `HDFS_1.tar.gz`) không lưu trực tiếp trong Git.
- **Để chạy tái lập trên bản clone sạch:** Người phản biện cần nạp 7 artifact ngoại vi vào các thư mục tương ứng theo bảng kê [`experiments/nineplus/ARTIFACT-MANIFEST.json`](experiments/nineplus/ARTIFACT-MANIFEST.json), hoặc sử dụng script tự động:
  ```powershell
  python scripts/provision_cleanroom_artifacts.py <đường_dẫn_chứa_artifact_ngoại_vi>
  ```
- Toàn bộ quy trình onboarding từ clone sạch, nạp artifact, cài đặt môi trường đến tái lập kết quả đã được thẩm định độc lập và đạt chuẩn **`CLEAN_ROOM_PASS = true`** (ghi nhận tại [`cleanroom/CLEANROOM-REPORT.md`](cleanroom/CLEANROOM-REPORT.md)).

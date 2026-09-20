# CẨM NANG HƯỚNG DẪN CHẠY VÀ XÁC MINH THỰC NGHIỆM
**Dành cho:** Giảng viên Hướng dẫn, Giảng viên Phản biện và Hội đồng Đánh giá Chuyên đề  
**Đề tài:** *Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công*  
**Sinh viên thực hiện:** Đoàn Ngọc Hoàng Minh – AT180632  
**Thời gian kiểm chứng dự kiến:** Khoảng 2–3 phút  

---

## 1. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)

- **Hệ điều hành:** Windows 10/11 (64-bit).
- **Môi trường Python:** Python 3.12 (đã kiểm định chuẩn xác trên Python 3.12.8).
- **Phần cứng đề xuất:** Card đồ họa rời NVIDIA (đã kiểm định trên NVIDIA GeForce RTX 3050 Ti Laptop GPU 4GB VRAM) hoặc CPU tương thích.
- **Công cụ dòng lệnh:** Windows PowerShell thông thường.

---

## 2. QUY TRÌNH THIẾT LẬP MÔI TRƯỜNG (KHOẢNG 1 PHÚT)

Từ thư mục gốc của repository, mở cửa sổ Windows PowerShell và thực hiện các lệnh sau:

```powershell
# 1. Khởi tạo môi trường ảo Python biệt lập
python -m venv .venv

# 2. Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# 3. Đảm bảo hỗ trợ UTF-8 cho PowerShell và nâng cấp pip
$env:PYTHONUTF8 = "1"
python -m pip install --upgrade pip

# 4. Cài đặt các thư viện phụ thuộc chính thức (có hỗ trợ CUDA 12.4)
pip install --extra-index-url https://download.pytorch.org/whl/cu124 -r requirements-lock.txt

# 5. Liên kết gói mã nguồn nghiên cứu ở chế độ phát triển
pip install -e .
```

---

## 3. NẠP ARTIFACT NGOẠI VI (KHOẢNG 30 GIÂY)

> [!NOTE]
> Do chính sách không lưu trữ dữ liệu nhị phân lớn trong Git (tuân thủ `.gitignore`), 7 artifact thực nghiệm ngoại vi (bao gồm tensor đặc trưng `.pt`, từ vựng, nhãn kiểm định và checkpoint tối ưu `best_checkpoint.pt`) cần được nạp trước khi chạy.

Giảng viên / người phản biện có thể sử dụng script tự động để nạp và đối soát mã băm SHA-256 đối chiếu với `experiments/nineplus/ARTIFACT-MANIFEST.json`:

```powershell
# Nạp và đối soát toàn vẹn 7 artifact từ thư mục lưu trữ cục bộ/ngoại vi
python scripts/provision_cleanroom_artifacts.py <đường_dẫn_thư_mục_chứa_artifact>
```

*Kỳ vọng:* In ra `[PASS] All 7 external artifacts successfully provisioned and verified.` và xuất báo cáo tại `cleanroom/ARTIFACT_PROVISIONING_REPORT.json`.

---

## 4. BA LỆNH KIỂM CHỨNG NHANH CỦA HỘI ĐỒNG (QUICK VERIFICATION)

### Lệnh 1: Kiểm tra phần cứng GPU và môi trường tính toán xác định
```powershell
$env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
python scripts/gpu_smoke_test.py
```
- **Thời gian chạy:** ~3 giây.
- **Kỳ vọng:** In ra `[PASS] GPU Smoke Test Passed 100% (Zero Model Training)` với mã thoát 0.
- **Mục đích:** Xác nhận GPU NVIDIA khả dụng, PyTorch 2.6.0+cu124, PyG 2.6.1 và cờ tái lập `CUBLAS_WORKSPACE_CONFIG` hoạt động đúng.

---

### Lệnh 2: Thẩm định tính toàn vẹn của Bảng chỉ mục Thực nghiệm
```powershell
python scripts/validate_experiment_index.py
```
- **Thời gian chạy:** ~2 giây.
- **Kỳ vọng:** In ra:
  ```text
  [VALIDATOR-PASS] 100% records in experiment_index.csv match source JSON artifacts!
  [VALIDATOR-PASS] 100% artifacts in ARTIFACT-MANIFEST.json verified!
  ```
- **Mục đích:** Đối soát tự động 100% từng dòng trong `experiments/experiment_index.csv` (18 cột) với các tệp JSON nguồn, bảo đảm không có hiện tượng trộn lẫn chỉ số giữa đầu dò nội bộ và đầu dò V3 chuẩn hóa.

---

### Lệnh 3: Tái lập chỉ số Đánh giá Hạ nguồn V3 ($AP = 1.0000$, $ROC\text{-}AUC = 1.0000$)
```powershell
$env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42
```
- **Thời gian chạy:** ~15 giây trên GPU.
- **Tiến trình tự động:**
  1. Kiểm tra 4 bất biến mật mã phân chia nhân quả (Train Membership SHA: `65b76694b0a3...`, Val Membership SHA: `14cf689f9682...`, Ordered Train/Val SHA) $\to$ **PASS**.
  2. Xác nhận tường lửa bảo vệ tập Test (`TEST_OPENED=false`, `TEST_READ_COUNT=0`) $\to$ **PASS**.
  3. Trích xuất đặc trưng 35.000 phiên Train và 7.500 phiên Validation.
  4. Huấn luyện Frozen Linear Probe V3 trong 50 epochs (Seed 10007, AdamW).
  5. In ra kết quả đánh giá hạ nguồn:
     ```text
     >>> V3 PROBE RESULT: AP=1.0000 | ROC-AUC=1.0000 | Var(z)=0.004535 | Steps=6850
     >>> Result written to experiments/nineplus/evaluation_v3/.../V3-PROBE-RESULT.json
     ```
- **Mã thoát:** `0`.

---

## 5. ĐỐI SOÁT VỚI BẢN THẢO CHUYÊN ĐỀ CHÍNH THỨC

Sau khi chạy xong, Thầy/Cô có thể mở bản thảo [`Chuyên đề chuyên sâu.pdf`](Chuyên%20đề%20chuyên%20sâu.pdf) (121 trang) để đối chiếu trực tiếp:

1. **Mục 3.2.4 "Kiểm chứng tái lập độc lập trên máy trạm" (Trang 85–88):**
   - **Bảng 3.7b:** Đối chiếu các chỉ số hội tụ của đợt huấn luyện xác nhận: `best_epoch = 3`, `best_val_loss = 0.009218`, dừng sớm tại `Epoch 6` với `patience = 3`, VRAM đỉnh `170.4 MB`.
   - **Hình 3.1:** Ảnh chụp console thực tế thể hiện quá trình tối ưu hóa qua các epochs và lưu vết checkpoint.
2. **Bảng 3.7 "Hiệu năng phát hiện bất thường qua các cấu hình kiến trúc":**
   - Hàng cấu hình `SEQUENCE_ONLY` (Seed 42): Đạt $AP = 1.0000$ và $ROC\text{-}AUC = 1.0000$.
3. **Báo cáo Thẩm định Phòng sạch Độc lập:**
   - Xem chi tiết biên bản kiểm thử từ clone Git sạch tại [`cleanroom/CLEANROOM-REPORT.md`](cleanroom/CLEANROOM-REPORT.md) (đạt chuẩn `CLEAN_ROOM_PASS = true`).

---

## 6. TUYÊN BỐ VỀ TÍNH SẴN SÀNG CÔNG KHAI

- **Trạng thái hiện tại:** `PUBLIC_CLEAN_CLONE_READY = false`.
- **Lý do kỹ thuật:** Do dữ liệu HDFS và checkpoint lớn chưa được cấp phát định danh DOI trên Zenodo/OSF để tải về tự động qua URL công khai, một bản clone Git sạch từ Internet sẽ cần bước nạp artifact cục bộ như hướng dẫn ở Mục 3 ở trên.
- **Cam kết khoa học:** Toàn bộ thuật toán, mã nguồn, biểu thức toán học OMML và kịch bản đối soát là hoàn toàn xác định, minh bạch và có khả năng truy vết mật mã 100%.

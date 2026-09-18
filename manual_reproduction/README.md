# HƯỚNG DẪN THỰC NGHIỆM TÁI LẬP ĐỘC LẬP DÀNH CHO SINH VIÊN
**Dự án:** Chuyên đề chuyên sâu - Học biểu diễn đặc trưng log an ninh  
**Cấu hình mục tiêu:** `SEQUENCE_ONLY` (Seed 42)  
**Mục tiêu:** Sinh viên có thể tự mở cửa sổ Windows PowerShell và thực hiện lại quá trình huấn luyện mô hình xác nhận độc lập trên máy trạm cá nhân, không phụ thuộc vào công cụ AI.

---

## 1. TẠI SAO CHỌN CẤU HÌNH `SEQUENCE_ONLY seed42`?

1. **Thời gian chạy tối ưu (~13.6 phút):**
   - Huấn luyện 6 epochs (khoảng 12.45 phút).
   - Kiểm định Validation (khoảng 1.16 phút).
   - Cơ chế Early Stopping tự động dừng tại Epoch 6 sau khi đạt loss tối ưu ở Epoch 3.
2. **Tiêu thụ tài nguyên rất thấp (~170.4 MB VRAM):**
   - Chiếm chưa đầy 5% dung lượng card rời 4GB (RTX 3050 Ti Laptop).
   - RAM hệ thống chỉ khoảng 1.4 GB. Không gây quá nhiệt hay rủi ro tràn bộ nhớ.
3. **Tính tái lập xác định 100%:**
   - Sử dụng cờ xác định `CUBLAS_WORKSPACE_CONFIG=:4096:8`.
   - Cố định hạt giống ngẫu nhiên 42 cho toàn bộ hệ thống (Python, NumPy, PyTorch CPU/CUDA).

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)

### 2.1. Môi trường Python và Thư viện phụ thuộc
Trước khi chạy, kích hoạt môi trường ảo chứa PyTorch có hỗ trợ CUDA 12.4:
```powershell
# Từ thư mục gốc D:\Research (hoặc thư mục clone của dự án)
.venv\Scripts\Activate.ps1
```
Cài đặt thư viện theo tệp khóa phụ thuộc `requirements-lock.txt`:
```powershell
pip install --extra-index-url https://download.pytorch.org/whl/cu124 -r requirements-lock.txt
```

### 2.2. Kiểm tra phần cứng và môi trường
Chạy script kiểm tra để xác nhận GPU và cấu hình CUDA:
```powershell
$env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
python scripts/gpu_smoke_test.py
```
Kỳ vọng in ra: `[PASS] GPU Smoke Test Passed 100% (Zero Model Training)` với mã thoát 0. Nếu thiếu bất kỳ gói phụ thuộc nào (như `torch-geometric==2.6.1`) hoặc GPU không khả dụng, script sẽ dừng ngay lập tức với mã thoát 1 (Fail-Fast).

### 2.3. Dữ liệu thực nghiệm bắt buộc (Lưu ý về Clean Clone)
> [!CAUTION]
> **Trạng thái kho ngoại vi:** `clean_clone_ready: false` (Kho lưu trữ ngoại vi Zenodo/OSF đang ở trạng thái `OPEN` chờ xuất xưởng). Bản clone Git sạch **chưa thể chạy ngay** nếu chưa có sẵn dữ liệu và checkpoint cục bộ.

Các tệp dữ liệu sau đây không lưu trong Git (theo quy định `.gitignore`) và cần có sẵn tại đường dẫn cục bộ tương ứng (kích thước và mã băm SHA-256 được script đối soát động từ `experiments/nineplus/ARTIFACT-MANIFEST.json`):
- `experiments/runs/data/hdfs/hdfs_ssl_train.pt` (64,300,470 bytes)
- `experiments/runs/data/hdfs/hdfs_ssl_val.pt` (12,125,250 bytes)
- `experiments/runs/data/hdfs/hdfs_vocab.json` (5,897 bytes)
- `experiments/runs/data/vault/hdfs_probe_labels_val.pt` (265,624 bytes)

---

## 3. LỆNH CHẠY THỰC NGHIỆM ĐỘC LẬP

### 3.1. Kiểm tra tiền thực thi (Preflight Check - Không chạy huấn luyện)
Sinh viên hoặc reviewer có thể kiểm tra toàn diện GPU, môi trường xác định và tính toàn vẹn 4 tệp dữ liệu mà không tốn thời gian huấn luyện:
```powershell
powershell -ExecutionPolicy Bypass -File manual_reproduction\run_manual_sequence42.ps1 -PreflightOnly
```
Kỳ vọng in ra `[PREFLIGHT-PASS]` với mã thoát 0.

### 3.2. Huấn luyện thực tế (Full Training Run)
Khi sẵn sàng thực hiện huấn luyện thực tế (~13.6 phút):
```powershell
powershell -ExecutionPolicy Bypass -File manual_reproduction\run_manual_sequence42.ps1
```

---

## 4. QUY TRÌNH TỰ ĐỘNG CỦA SCRIPT

Script PowerShell `run_manual_sequence42.ps1` thực hiện nghiêm ngặt 10 bước an toàn:
1. **Thiết lập biến môi trường xác định:** Thiết lập `$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"`.
2. **Khởi chạy Smoke Test & Fail-Fast:** Gọi `scripts/gpu_smoke_test.py`; nếu mã thoát khác 0, script dừng khẩn cấp và không tiến hành huấn luyện.
3. **Tự động xác định thư mục gốc:** Không hard-code `D:\Research`, tự nhận diện thư mục cha của `manual_reproduction/`.
4. **Kiểm tra mã băm động:** Đọc danh mục tệp và mã băm SHA-256 kỳ vọng trực tiếp từ `experiments/nineplus/ARTIFACT-MANIFEST.json` để đối soát toàn vẹn dữ liệu.
5. **Khởi tạo thư mục phiên chạy:** Tạo `manual_reproduction/runs/<timestamp>/` riêng biệt, không ghi đè bất kỳ tệp lịch sử nào.
6. **Ghi nhật ký đầy đủ (Audit Trail):** Ghi transcript console bằng `Start-Transcript` (đảm bảo dừng bằng `Stop-Transcript` trong khối `finally`), lưu Git commit SHA, git status và thông số môi trường.
7. **Snapshot danh mục trước khi chạy:** Quét các thư mục hiện hữu trong `experiments/nineplus/confirmatory/`.
8. **Kích hoạt huấn luyện:** Gọi `scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda --base-dir <RepoRoot>`.
9. **Nhận diện và thẩm định thư mục kết quả mới:** Phát hiện thư mục `CONF_SEQUENCE_ONLY_seed42_<timestamp>/` duy nhất vừa sinh ra, xác thực `RUN-MANIFEST.json`, `TRAIN-LOG.jsonl`, `best_checkpoint.pt`, kiểm tra không có NaN/Inf trong loss.
10. **Xuất báo cáo tóm tắt:** Lưu báo cáo đối soát tại `manual_reproduction/runs/<timestamp>/MANUAL_RUN_SUMMARY.txt`.

---

## 5. ĐỐI SOÁT KẾT QUẢ VỚI BÁO CÁO CHUYÊN ĐỀ

Sau khi chạy xong, sinh viên mở tệp `MANUAL_RUN_SUMMARY.txt` và đối chiếu:
- **Best Epoch:** Epoch 3.
- **Early Stopping:** Dừng tại Epoch 6 với `patience=3`.
- **Best Val Loss:** Hội tụ xấp xỉ `0.0092` (theo hàm mất mát tự giám sát đa nhiệm Sequence View).
- **Internal Online Probe AP / ROC-AUC:** Đạt xấp xỉ `AP ~ 0.8994`, `ROC-AUC ~ 0.9973`.
- **Frozen Linear Probe V3 Standardized:** Đạt `AP = 1.0000`, `ROC-AUC = 1.0000` (được thẩm định độc lập qua `scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42`).

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
Kỳ vọng in ra: `[PASS] GPU Smoke Test Passed 100% (Zero Model Training)`.

### 2.3. Dữ liệu thực nghiệm bắt buộc
Các tệp dữ liệu sau đây không lưu trong Git (theo quy định `.gitignore`) và cần có sẵn tại đường dẫn cục bộ tương ứng (tra cứu SHA-256 đối soát tại `experiments/nineplus/ARTIFACT-MANIFEST.json`):
- `experiments/runs/data/hdfs/hdfs_ssl_train.pt` (64,300,470 bytes)
- `experiments/runs/data/hdfs/hdfs_ssl_val.pt` (12,125,250 bytes)
- `experiments/runs/data/hdfs/hdfs_vocab.json` (5,897 bytes)
- `experiments/runs/data/vault/hdfs_probe_labels_val.pt` (265,624 bytes)

---

## 3. LỆNH CHẠY THỰC NGHIỆM ĐỘC LẬP

Sinh viên chỉ cần mở PowerShell thông thường tại thư mục dự án và thực thi duy nhất một lệnh:

```powershell
powershell -ExecutionPolicy Bypass -File manual_reproduction\run_manual_sequence42.ps1
```

---

## 4. QUY TRÌNH TỰ ĐỘNG CỦA SCRIPT

Script PowerShell `run_manual_sequence42.ps1` thực hiện nghiêm ngặt 10 bước an toàn:
1. **Tự động xác định thư mục gốc:** Không hard-code `D:\Research`, tự nhận diện thư mục cha của `manual_reproduction/`.
2. **Kiểm tra Fail-Fast:** Xác thực Python, CUDA, dung lượng đĩa trống (tối thiểu 2GB) và sự tồn tại của 4 tệp dữ liệu.
3. **Kiểm tra mã băm toàn vẹn (SHA-256 Check):** Đối soát mã băm của 4 tệp dữ liệu trước khi nạp vào PyTorch.
4. **Khởi tạo thư mục phiên chạy:** Tạo `manual_reproduction/runs/<timestamp>/` riêng biệt, không ghi đè bất kỳ tệp lịch sử nào.
5. **Ghi nhật ký đầy đủ (Audit Trail):** Tự động ghi lại transcript console, Git commit SHA, git status, thông số Python/CUDA và các mã băm đầu vào.
6. **Chụp ảnh snapshot thư mục trước khi chạy:** Quét danh sách các thư mục confirmatory đã có để nhận diện chính xác thư mục vừa sinh ra.
7. **Kích hoạt huấn luyện:** Gọi `scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda`.
8. **Nhận diện thư mục kết quả mới:** Phát hiện đúng thư mục `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_<timestamp>/` vừa được tạo.
9. **Kiểm tra nghiệm thu đầu ra:** Xác nhận sự hiện diện của `RUN-MANIFEST.json`, `TRAIN-LOG.jsonl`, `best_checkpoint.pt`, và tính mã băm SHA-256 của checkpoint mới.
10. **Xuất báo cáo tóm tắt:** Lưu báo cáo đối soát tại `manual_reproduction/runs/<timestamp>/MANUAL_RUN_SUMMARY.txt`.

---

## 5. ĐỐI SOÁT KẾT QUẢ VỚI BÁO CÁO CHUYÊN ĐỀ

Sau khi chạy xong, sinh viên mở tệp `MANUAL_RUN_SUMMARY.txt` và đối chiếu:
- **Best Epoch:** Phải là Epoch 3.
- **Early Stopping:** Dừng tại Epoch 6 với `patience=3`.
- **Best Val Loss:** Hội tụ xấp xỉ `1.1577`.
- **Probe AP / ROC-AUC:** Đạt xấp xỉ `AP = 1.0000`, `ROC-AUC = 1.0000`.

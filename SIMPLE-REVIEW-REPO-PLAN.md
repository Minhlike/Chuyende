# KẾ HOẠCH TINH GỌN VÀ CHUẨN HÓA KHO LƯU TRỮ DÀNH CHO PHẢN BIỆN
**Tài liệu:** `SIMPLE-REVIEW-REPO-PLAN.md`  
**Dự án:** Chuyên đề chuyên sâu của Sinh viên  
**Kho lưu trữ:** `Minhlike/Chuyende` | **Nhánh:** `fix/thesis-apply-edits`  
**Mục tiêu:** Tinh giản cấu trúc kho mã nguồn, loại bỏ thủ tục hành chính phức tạp, xây dựng tài liệu hướng dẫn trực quan, thiết thực cho giảng viên phản biện và lộ trình thực nghiệm độc lập cho sinh viên.

---

## 1. PHÂN TÍCH CÁC VẤN ĐỀ TỒN ĐỌI CỦA REPOSITORY HIỆN TẠI

1. **Sai lệch định danh học thuật và quá tải thuật ngữ hành chính:**
   - Tệp `README.md` hiện tại viết bằng tiếng Anh và tuyên bố sai lệch học vị: *"PhD-level research study..."*, trong khi đây là chuyên đề chuyên sâu của sinh viên.
   - Trạng thái nghiên cứu trong `README.md` đã lỗi thời: Chương 3 vẫn ghi *"PRE-REGISTRATION LOCKED / All experiments in PLANNED state"*, trong khi toàn bộ thực nghiệm Nineplus V3 đã hoàn tất và được tích hợp vào văn bản Master DOCX/PDF.
   - Sử dụng quá nhiều thuật ngữ hàn lâm mang phong cách quản trị doanh nghiệp nặng nề: *"Research Constitution", "Invariants", "RC-01 - RC-18", "Hard firewall", "Authority", "Evidence matrix", "Contract"*. Cần chuyển đổi về ngôn ngữ kỹ thuật chuẩn mực, dễ hiểu của một báo cáo chuyên đề sinh viên.

2. **Tình trạng phân mảnh và quá tải tệp tin tại thư mục gốc (Root Clutter):**
   - Thư mục gốc `D:\Research` có hơn 120 tệp tin, bao gồm hàng chục script phụ trợ dùng một lần (`test_omml.py`, `test_word_com.py`, `test_canvas_order.py`, `patch_section_2_3_and_2_4.py`, `add_chapter1_sources.py`), các tệp tạm (`.tmp`, `~$uyên đề...`), các bản sao lưu DOCX (`Chuyên đề chuyên sâu.pre_sweep_backup.docx`, `clean_tgn_buildup.docx`).
   - Người phản biện khi truy cập thư mục gốc rất khó phân biệt đâu là mã nguồn cốt lõi, đâu là script thực thi chính thức và đâu là dữ liệu kết quả.

3. **Thiếu vắng tài liệu dẫn đường thực hành trực tiếp (Reviewer Onboarding Barrier):**
   - Chưa có tệp `HUONG_DAN_CHAY_VA_XAC_MINH.md` để giảng viên phản biện có thể mở lên, chạy ngay 2-3 lệnh kiểm tra và tái lập kết quả trong vòng vài phút.
   - Chưa có thư mục và cẩm nang `manual_reproduction/` hướng dẫn sinh viên tự chạy một thực nghiệm độc lập từ PowerShell mà không phụ thuộc vào công cụ AI.

4. **Chú thích mã nguồn (Docstrings / Comments) quá dài dòng:**
   - Nhiều module trong `src/research_agent/` chứa các khối docstring tiếng Anh quá dài, nhắc lại các điều khoản quy ước nội bộ thay vì giải thích trực diện logic toán học và luồng xử lý dữ liệu.

---

## 2. CẤU TRÚC CÂY THƯ MỤC TINH GỌN MỤC TIÊU (MINIMAL TARGET TREE)

Repository sẽ được tổ chức lại gọn gàng, trong sáng theo đúng mô hình một đồ án/chuyên đề nghiên cứu sinh viên:

```text
D:\Research\
├── README.md                              # Giới thiệu tổng quan ngắn gọn, tự nhiên, súc tích (1-2 trang tiếng Việt)
├── HUONG_DAN_CHAY_VA_XAC_MINH.md           # Cẩm nang thực hành cho giảng viên / reviewer tái lập kết quả
├── manual_reproduction/
│   ├── README.md                          # Hướng dẫn chi tiết cho sinh viên tự chạy thực nghiệm độc lập
│   └── run_manual_sequence42.ps1          # Script PowerShell tinh gọn chuẩn bị sẵn để sinh viên chạy
│
├── Chuyên đề chuyên sâu.docx              # Bản thảo Master DOCX chính thức (606 nút OMML)
├── Chuyên đề chuyên sâu.pdf               # Bản xuất bản Master PDF 114 trang đồng bộ
├── SPECIALIZED-TOPIC-FINAL-QA-REPORT.md   # Báo cáo kiểm toán chất lượng học thuật và 8 chỉ tiêu bất biến
├── SPECIALIZED-TOPIC-NINEPLUS-INTEGRATION-REPORT.md # Báo cáo tích hợp số liệu V3 đã chuẩn hóa
│
├── src/                                   # Mã nguồn chính của chuyên đề (research_agent)
│   └── research_agent/
│       ├── core/                          # Tiện ích hàm băm, hằng số hệ thống
│       └── experiments/
│           ├── data/                      # Đọc log HDFS, trích xuất thuộc tính, phân chia causal split
│           ├── extractor/                 # Tokenizer bảo vệ tham số, Transformer Sequence View, Multi-View
│           ├── models/                    # Mô hình TemporalGraphViewEncoder
│           └── training/                  # Module huấn luyện Stage A2
│
├── scripts/                               # Các script chạy thực nghiệm và kiểm tra chính
│   ├── run_nineplus_confirmatory.py       # Huấn luyện mô hình xác nhận (Sequence, Multi-View)
│   ├── evaluate_nineplus_v3.py            # Đánh giá đầu dò tuyến tính V3 trên tập Validation
│   ├── run_h1_masking_ablation.py         # Kiểm thử cắt bỏ che tham số đầu vào H1
│   ├── run_h2_sequence_noparam_sensitivity.py # Phân tích độ nhạy bỏ tham số Sequence H2
│   └── gpu_smoke_test.py                  # Kiểm tra môi trường GPU, CUDA, PyTorch
│
├── experiments/
│   ├── experiment_index.csv               # Bảng mục lục tra cứu nhanh các đợt thực nghiệm
│   └── nineplus/
│       ├── confirmatory/                  # Checkpoints và nhật ký huấn luyện của 6 mô hình
│       └── evaluation_v3/                 # Tệp JSON tổng hợp kết quả đánh giá V3, H1, H2
│
└── datasets/
    └── raw/hdfs/                          # Dữ liệu HDFS nén gốc và bộ nhớ đệm phân vùng
```

---

## 3. ĐỀ CƯƠNG CHI TIẾT CHO `README.md`

Tệp `README.md` mới sẽ được viết lại hoàn toàn bằng tiếng Việt chuẩn mực, ngắn gọn, súc tích, loại bỏ hoàn toàn các từ ngữ quản trị doanh nghiệp:

1. **Tên đề tài & Thông tin chung:**
   - Tên đề tài: *Nghiên cứu các phương pháp học biểu diễn đặc trưng log phục vụ phát hiện bất thường an toàn thông tin*.
   - Đối tượng thực hiện: Sinh viên thực hiện chuyên đề nghiên cứu chuyên sâu.
   - Tài liệu báo cáo chính thức: Liên kết tới `Chuyên đề chuyên sâu.docx` và `Chuyên đề chuyên sâu.pdf`.

2. **Tóm tắt chuyên đề (1–2 đoạn tự nhiên):**
   - Trình bày bài toán biểu diễn đặc trưng nhật ký hệ thống (log telemetry) bảo toàn ngữ cảnh an ninh phục vụ phát hiện bất thường.
   - Khung phương pháp luận tích hợp: Chuỗi thời gian ngữ nghĩa dựa trên Transformer kết hợp Đồ thị phụ thuộc thời gian liên tục (Temporal GNN) thông qua hàm mất mát tự giám sát đa góc nhìn VICReg và cơ chế hòa trộn động (Gated Fusion).

3. **Cấu trúc thư mục tối giản:** Sơ đồ khối cây thư mục ngắn gọn như Mục 2 trên.

4. **Yêu cầu môi trường thực nghiệm:**
   - Hệ điều hành: Windows 11 (hoặc Linux tương đương).
   - Python: 3.12+.
   - PyTorch: 2.6.0+cu124 (hoặc phiên bản CUDA tương thích).
   - Phần cứng thực tế: Laptop GPU NVIDIA GeForce RTX 3050 Ti (4GB VRAM), RAM 16GB.

5. **Bộ dữ liệu thực nghiệm:**
   - Tập dữ liệu HDFS (Hadoop Distributed File System log telemetry).
   - Phân chia theo dòng thời gian chống rò rỉ (Causal Temporal Split): 35.000 phiên Train (68,4%), 7.500 phiên Validation (14,7%). Tập Test chưa từng được truy cập (`test_opened = false`, `test_reads = 0`).

6. **Cách chạy nhanh (Quick Start cho Reviewer):**
   - Lệnh 1: Kiểm tra môi trường phần cứng (`python scripts/gpu_smoke_test.py`).
   - Lệnh 2: Tái lập bảng kết quả đánh giá hạ nguồn V3 trên checkpoint có sẵn (`python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42`).

7. **Vị trí lưu trữ Checkpoints, Logs và Kết quả:**
   - Checkpoints: `experiments/nineplus/confirmatory/<run_id>/best_checkpoint.pt`.
   - Nhật ký huấn luyện: `experiments/nineplus/confirmatory/<run_id>/TRAIN-LOG.jsonl`.
   - Kết quả tổng hợp: `experiments/nineplus/evaluation_v3/V3_SIX_BACKBONE_EVALUATION_SUMMARY.json`.

8. **Tóm tắt kết quả chính (Bảng số liệu ngắn):**
   - Trình bày bảng so sánh ngắn gọn giữa Sequence-Only (AP = 1.0000, ROC-AUC = 1.0000) và Multi-View (AP trung bình = 0.6608, ROC-AUC trung bình = 0.8573).
   - Tóm tắt trung thực kết quả kiểm chứng: H2 không được hỗ trợ trong phạm vi đối chứng trực tiếp với Sequence-Only trên tập HDFS ($\Delta	ext{AP} = -0.3392 \pm 0.0885$, vi phạm biên $\delta \ge -0.02$); H1 chưa thể đánh giá trực tiếp do bất tương thích độ mịn mục tiêu; H3, H4, H5 được bảo lưu cho nghiên cứu tiếp theo.

9. **Chỉ mục chuyển tiếp:** Đường dẫn trực tiếp tới `HUONG_DAN_CHAY_VA_XAC_MINH.md`.

---

## 4. ĐỀ CƯƠNG CHI TIẾT CHO `HUONG_DAN_CHAY_VA_XAC_MINH.md`

Đây là tài liệu thực hành trung tâm dành cho Thầy/Cô và Reviewer để tái lập kết quả:

- **Mục A: Cài đặt môi trường:**
  - Hướng dẫn kích hoạt môi trường ảo Python.
  - Lệnh cài đặt các thư viện cần thiết: `torch`, `numpy`, `scipy`, `python-docx`, `pypdfium2`.

- **Mục B: Kiểm tra cấu hình phần cứng và PyTorch:**
  - Lệnh thực thi: `python scripts/gpu_smoke_test.py`.
  - Kết quả in ra kỳ vọng: GPU name, dung lượng VRAM khả dụng, CUDA capability, trạng thái xác định `CUBLAS_WORKSPACE_CONFIG=:4096:8`.

- **Mục C: Cấu trúc dữ liệu yêu cầu:**
  - Vị trí tệp dữ liệu HDFS gốc: `datasets/raw/hdfs/HDFS_1.tar.gz`.
  - Vị trí các tệp bộ nhớ đệm phân vùng đã tiền xử lý: `experiments/runs/data/hdfs/`.

- **Mục D: Lệnh chạy thực nghiệm đại diện (Representative Training Run):**
  - Chạy mô hình Sequence-Only hạt giống 42:
    ```powershell
    python scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda
    ```
  - Thời gian dự kiến: ~13.6 phút trên laptop GPU RTX 3050 Ti.
  - Bộ nhớ VRAM chiếm dụng: ~170 MB.
  - Cơ chế Early Stopping tự động kích hoạt tại Epoch 6 sau khi đạt val loss tốt nhất ở Epoch 3.

- **Mục E: Lệnh nạp và kiểm tra Checkpoint có sẵn:**
  - Lệnh Python một dòng để đọc siêu dữ liệu checkpoint mà không cần chạy lại từ đầu:
    ```powershell
    python -c "import torch; ckpt=torch.load('experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_1789413645/best_checkpoint.pt', map_location='cpu', weights_only=False); print('Keys:', list(ckpt.keys())); print('Best Epoch:', ckpt['epoch']); print('Best Val Loss:', ckpt['val_loss'])"
    ```

- **Mục F: Lệnh tái lập các chỉ số Validation trong báo cáo:**
  - Tái lập kết quả đầu dò tuyến tính đóng băng cho mô hình Sequence-Only Seed 42:
    ```powershell
    python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42
    ```
  - Kết quả in ra xác nhận: Average Precision = 1.0000, ROC-AUC = 1.0000, thời gian trích xuất ~10 giây.
  - Tái lập trên toàn bộ 6 mô hình xác nhận (Sequence và Multi-View):
    ```powershell
    python scripts/evaluate_nineplus_v3.py --all
    ```

- **Mục G: Bảng tra cứu vị trí tệp tin bằng chứng:**
  - Bảng liệt kê chi tiết: Tên mô hình, Seed, Đường dẫn Checkpoint, Đường dẫn nhật ký huấn luyện `TRAIN-LOG.jsonl`, Đường dẫn hồ sơ thực nghiệm `RUN-MANIFEST.json`.

- **Mục H: Hướng dẫn kiểm tra mã băm toàn vẹn SHA-256:**
  - Sử dụng lệnh PowerShell chuẩn: `Get-FileHash <đường_dẫn_tệp> -Algorithm SHA256`.
  - Cung cấp mã băm chuẩn của tệp dữ liệu và checkpoint để đối soát.

- **Mục I: Cam kết về tập dữ liệu Kiểm thử (Test split):**
  - Tuyên bố minh bạch: Tập dữ liệu Kiểm thử tiếp tục được bảo toàn trạng thái chưa mở (`TEST_OPENED=false`, `TEST_READ_COUNT=0`), toàn bộ kết quả báo cáo được đo kiểm độc lập trên tập Kiểm định (Validation).

---

## 5. KẾ HOẠCH THỰC NGHIỆM ĐỘC LẬP DÀNH CHO SINH VIÊN (`manual_reproduction/`)

Thư mục `manual_reproduction/` được thiết kế riêng để sinh viên có thể tự tay mở cửa sổ Windows PowerShell độc lập (không thông qua giao diện AI Agent) và thực hiện lại một đợt chạy huấn luyện:

1. **Lý do lựa chọn cấu hình `SEQUENCE_ONLY seed42`:**
   - *Thời lượng tối ưu:* Chỉ mất ~13.6 phút (12.45 phút huấn luyện + 1.16 phút kiểm định qua 6 epochs).
   - *Tài nguyên phần cứng thấp:* VRAM đỉnh chỉ 170.4 MB (chiếm chưa đầy 5% dung lượng GPU 4GB), RAM hệ thống ~1.4 GB. Không gây nóng máy hay rủi ro tràn bộ nhớ.
   - *Tính tái lập xác định:* Đã cấu hình `CUBLAS_WORKSPACE_CONFIG=:4096:8` và khóa seed ngẫu nhiên 42, đảm bảo hàm mất mát hội tụ khớp chính xác với lịch sử.

2. **Quy trình thực hiện bằng PowerShell độc lập:**
   - Bước 1: Mở Windows PowerShell thông thường.
   - Bước 2: Kích hoạt môi trường: `.venv-stage-a2-cuda\Scripts\Activate.ps1`.
   - Bước 3: Di chuyển vào thư mục nghiên cứu: `cd D:\Research`.
   - Bước 4: Bật ghi nhật ký phiên làm việc:
     ```powershell
     Start-Transcript -Path manual_reproduction\MANUAL_RUN_SEQUENCE42.log
     ```
   - Bước 5: Chạy lệnh thực nghiệm có gắn nhãn riêng:
     ```powershell
     python scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda
     ```
   - Bước 6: Sau khi hoàn thành, dừng ghi nhật ký:
     ```powershell
     Stop-Transcript
     ```

3. **Tính toán mã băm và lưu trữ:**
   - Tính mã băm SHA-256 của checkpoint vừa sinh ra và lưu vào `manual_reproduction/MANUAL_HASH.txt`.

4. **Định danh minh bạch:**
   - Toàn bộ kết quả chạy của sinh viên được lưu tại thư mục gắn nhãn `manual_reproduction/` và không ghi đè lên các tệp lịch sử đã nghiệm thu trong `experiments/nineplus/confirmatory/`.

---

## 6. KẾ HOẠCH 5–7 ẢNH CHỤP MÀN HÌNH MINH CHỨNG (SCREENSHOT PLAN)

Để minh chứng tính trung thực và khả năng thực thi thực tế trong báo cáo, thiết kế danh mục 7 ảnh chụp màn hình cụ thể từ cửa sổ dòng lệnh Windows PowerShell (tuyệt đối không chụp giao diện AI):

| STT | Tên tệp ảnh dự kiến | Lệnh / Màn hình thực hiện | Mục đích chứng minh |
| :---: | :--- | :--- | :--- |
| **1** | `01_environment_gpu_git.png` | `python scripts/gpu_smoke_test.py`<br>`git log -n 1 --oneline` | Chứng minh môi trường thực tế trên máy trạm cá nhân: Windows 11, GPU RTX 3050 Ti, PyTorch CUDA và mã commit Git hiện tại. |
| **2** | `02_manual_run_command.png` | Cửa sổ PowerShell với dấu nhắc `PS D:\Research>` hiển thị dòng lệnh sinh viên tự gõ để chạy Sequence-Only Seed 42. | Chứng minh sinh viên trực tiếp thao tác dòng lệnh từ hệ điều hành. |
| **3** | `03_training_epochs_loss.png` | Màn hình tiến trình Epoch 1, 2, 3 hiển thị train loss giảm dần, val loss và dung lượng VRAM (~170 MB). | Chứng minh mạng nơ-ron thực sự tối ưu hóa và hội tụ trên GPU. |
| **4** | `04_early_stopping_best_checkpoint.png` | Màn hình thông báo Early Stopping tại Epoch 6 (dừng sớm với patience=3, lưu best_checkpoint tại Epoch 3). | Chứng minh cơ chế dừng sớm tự động và việc lưu trữ checkpoint thành công. |
| **5** | `05_checkpoint_hash_verification.png` | `Get-FileHash ...\best_checkpoint.pt -Algorithm SHA256` | Chứng minh tính toàn vẹn và khả năng truy vết mật mã của checkpoint. |
| **6** | `06_validation_metric_reproduction.png` | `python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42` | Chứng minh việc tái lập độc lập các chỉ số đánh giá hạ nguồn (AP = 1.0000, ROC-AUC = 1.0000) trên 7.500 phiên Validation. |
| **7** | `07_repository_file_structure.png` *(Tùy chọn)* | `Get-ChildItem -Directory` hoặc hiển thị cây thư mục dự án sạch sẽ. | Minh họa cấu trúc repository ngăn nắp, sẵn sàng nghiệm thu. |

---

## 7. LỰA CHỌN 8 ĐOẠN MÃ NGUỒN TIÊU BIỂU CHO WORD (CODE EXCERPTS)

Tuyển chọn 8 đoạn trích mã nguồn then chốt (mỗi đoạn từ 8 đến 24 dòng) đại diện cho các đóng góp kỹ thuật cốt lõi trong văn bản chuyên đề:

### Đoạn trích 1: Phân chia tập dữ liệu theo trục thời gian và kiểm tra không rò rỉ
- **FILE:** `src/research_agent/experiments/data/hdfs_split_authority.py`
- **FUNCTION:** `compute_and_cache_split`
- **LINE_RANGE:** 170–185 (16 dòng)
- **THESIS_SECTION:** Mục 3.1.2 (Khung dữ liệu đối chuẩn và giao thức phân chia theo dòng thời gian chống rò rỉ)
- **SHORT_CAPTION:** Ranh giới phân chia thời gian nhân quả và phép kiểm tra tính bất giao
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích được cách xác định thời điểm bắt đầu/kết thúc của từng phiên log, cơ chế loại bỏ (purge) các phiên vắt qua ranh giới phân vùng, và các phép `assert` kiểm tra tính bất giao giữa Train, Val, Test nhằm ngăn chặn rò rỉ thông tin tương lai.

### Đoạn trích 2: Kiểu hóa và mã giả danh tham số có nhận thức an ninh
- **FILE:** `src/research_agent/experiments/extractor/tokenizer.py`
- **FUNCTION:** `PrivacyAwareLogTokenizer.tokenize_line`
- **LINE_RANGE:** 138–159 (22 dòng)
- **THESIS_SECTION:** Mục 2.2.1 / 2.2.2 (Lược đồ kiểu hóa và bảo toàn tham số có nhận thức an ninh)
- **SHORT_CAPTION:** Phân loại và mã hóa tham số động bảo vệ quyền riêng tư
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Phân biệt được địa chỉ IP nội bộ (RFC1918) và ngoại vi, phân loại đường dẫn tập tin hệ thống trọng yếu (`/etc/`, `/tmp/`, `/var/log/`), và việc sử dụng hàm băm HMAC có khóa ngắn hạn để tạo mã giả danh nhất quán trong phiên.

### Đoạn trích 3: Hàm mất mát tự giám sát dự đoán tham số động đa khe (L_MPP)
- **FILE:** `src/research_agent/experiments/extractor/sequence_view.py`
- **FUNCTION:** `SequenceViewExtractor.compute_sequence_ssl_losses`
- **LINE_RANGE:** 201–218 (18 dòng)
- **THESIS_SECTION:** Mục 2.3.1 (Mục tiêu huấn luyện tự giám sát của bộ trích xuất tuần tự)
- **SHORT_CAPTION:** Tính toán hàm mất mát Cross-Entropy cho các khe tham số bị che giấu
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Trình bày được cấu trúc đầu ra đa khe `[B, T, K, V_param]`, cách tạo mặt nạ loại bỏ token đệm `<PAD_PARAM>` để chỉ phạt trên các tham số có nghĩa thực tế, và cơ chế tính toán mất mát tự giám sát L_MPP.

### Đoạn trích 4: Khôi phục trạng thái bộ nhớ rỗng cho đồ thị động (Inductive Reset)
- **FILE:** `src/research_agent/experiments/models/temporal_graph_view_encoder.py`
- **FUNCTION:** `TemporalGraphViewEncoder.reset_node_states`
- **LINE_RANGE:** 161–168 (8 dòng)
- **THESIS_SECTION:** Mục 2.3.2 / Mục 3.1.2 (Bộ trích xuất đồ thị động và thiết lập ranh giới phân vùng)
- **SHORT_CAPTION:** Xóa bộ nhớ trạng thái thực thể tại ranh giới chuyển đổi phân vùng
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích tại sao trong mô hình đồ thị động có bộ nhớ (GRUCell), bắt buộc phải xóa sạch bộ nhớ nút, mốc thời gian và bộ đệm lịch sử khi chuyển giữa Train và Validation để đảm bảo tính quy nạp (inductive) và không rò rỉ trạng thái.

### Đoạn trích 5: Cơ chế hòa trộn đa góc nhìn động dựa trên cổng (Gated Fusion)
- **FILE:** `src/research_agent/experiments/extractor/multi_view.py`
- **FUNCTION:** `GatedMultiViewFusion.forward`
- **LINE_RANGE:** 101–120 (20 dòng)
- **THESIS_SECTION:** Mục 2.4.4 (Cổng độ tin cậy động và Phẫu thuật Gradient / Biểu diễn thống nhất canonical)
- **SHORT_CAPTION:** Hòa trộn thích nghi biểu diễn chuỗi và đồ thị qua vector cổng Sigmoid
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích cách mạng cổng nhận đầu vào kết hợp `[z_seq; z_graph]`, sinh vector trọng số $lpha \in [0, 1]^d$, và tính vector biểu diễn đa góc nhìn cuối cùng qua phép tổ hợp lồi $z_{mv} = lpha \odot z_{seq} + (1-lpha) \odot z_{graph}$.

### Đoạn trích 6: Giao thức huấn luyện đầu dò tuyến tính đóng băng (Frozen Linear Probe)
- **FILE:** `scripts/evaluate_nineplus_v3.py`
- **FUNCTION:** `V3Evaluator.fit_linear_probe`
- **LINE_RANGE:** 305–327 (23 dòng)
- **THESIS_SECTION:** Mục 3.1.3 (Chuẩn hóa Giao thức Đầu dò Tuyến tính Đóng băng V3)
- **SHORT_CAPTION:** Huấn luyện bộ phân loại tuyến tính mỏng trên biểu diễn đóng băng
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích nguyên lý đánh giá chất lượng biểu diễn tự giám sát: đóng băng 100% trọng số backbone, chỉ huấn luyện ma trận $W \in \mathbb{R}^{128 	imes 1}$ với bộ tối ưu AdamW trong 50 epochs trên biểu diễn Train, cố định hạt giống 10007 để đảm bảo tính khách quan tuyệt đối.

### Đoạn trích 7: Tính toán các chỉ số an ninh Average Precision (AP) và ROC-AUC
- **FILE:** `scripts/evaluate_nineplus_v3.py`
- **FUNCTION:** `compute_ap_and_roc_auc`
- **LINE_RANGE:** 57–80 (24 dòng)
- **THESIS_SECTION:** Mục 3.1.3 (Hệ thống thang đo ba tầng và hàm mục tiêu)
- **SHORT_CAPTION:** Thuật toán tính toán tích phân AP và thống kê xếp hạng ROC-AUC
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Phân tích sự phù hợp của chỉ số Average Precision đối với tập dữ liệu mất cân bằng cực đoan (ít mẫu bất thường), giải thích công thức tích phân hình thang Precision-Recall và xếp hạng Mann-Whitney U để tính ROC-AUC.

### Đoạn trích 8: Hàm băm SHA-256 theo khối dữ liệu lớn (Chunk-based Hashing)
- **FILE:** `src/research_agent/core/hash_utils.py`
- **FUNCTION:** `compute_file_sha256`
- **LINE_RANGE:** 11–21 (11 dòng)
- **THESIS_SECTION:** Mục 3.1.1 (Môi trường tính toán, tính tái lập và kiểm định độ bất định)
- **SHORT_CAPTION:** Tính toán mã băm SHA-256 theo từng khối dữ liệu 64KB
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích kỹ thuật đọc luồng nhị phân theo khối (chunk-based streaming) giúp tính toán mã băm toàn vẹn cho các tệp checkpoint và tập dữ liệu dung lượng hàng gigabyte mà không làm tràn bộ nhớ RAM.

---

## 8. RÀ SOÁT TÍNH DỄ ĐỌC CỦA MÃ NGUỒN (SOURCE READABILITY AUDIT)

Rà soát các tệp mã nguồn để chuẩn bị cho giai đoạn tinh gọn tiếp theo (tuyệt đối không chỉnh sửa mã nguồn trong pha này):

| Tệp mã nguồn | Vấn đề phát hiện | Khuyến nghị xử lý |
| :--- | :--- | :--- |
| `src/research_agent/experiments/extractor/sequence_view.py` | Docstring đầu tệp chứa các thuật ngữ hợp đồng nội bộ: *"Frozen Specification", "Bang 2.1", "Stage A1 Contract", "BOUNDED_MULTI_SLOT_..."*. | `SHORTEN`: Rút gọn docstring thành mô tả kỹ thuật kiến trúc Transformer Encoder và các hàm mất mát MEP, MPP, Time. |
| `src/research_agent/experiments/models/temporal_graph_view_encoder.py` | Docstring đầu tệp chứa các quy ước hành chính: *"Contract V1.3 Amended", "Relation Target Firewall", "Node Target Firewall"*. | `SHORTEN`: Rút gọn docstring, mô tả rõ cơ chế GRUCell, hàm nhúng thời gian liên tục $\phi(\Delta t)$, và các đầu ra tự giám sát. |
| `src/research_agent/experiments/data/hdfs_split_authority.py` | Docstring nhắc lại *"Single-source-of-truth session interval extraction, SPL-HDFS-001 Shared Module"*. | `SHORTEN`: Đổi thành mô tả kỹ thuật phân chia dữ liệu nhân quả Train/Val/Test theo dòng thời gian. |
| `src/research_agent/experiments/extractor/tokenizer.py` | Docstring dài dòng về *"Chapter 2 Frozen Specification & Key Governance"*. | `SHORTEN`: Tóm tắt ngắn gọn 4 chế độ tiền xử lý và cơ chế mã giả danh HMAC bảo vệ quyền riêng tư. |
| `src/research_agent/core/hash_utils.py` | Docstring nhắc tới *"RC-10, RC-15, RC-16"* (các quy tắc hiến pháp nội bộ của AI). | `REMOVE_REDUNDANT_COMMENT`: Xóa các ký hiệu mã hiệu nội bộ `(RC-...)`. |
| Toàn bộ các script trong `scripts/` | Các chú thích hiển nhiên, lặp lại mã lệnh (ví dụ: `# Save DOCX`, `# Create directory if not exists`). | `REMOVE_REDUNDANT_COMMENT`: Loại bỏ các chú thích hiển nhiên để mã nguồn gọn gàng. |

---

## 9. CHỈ MỤC BẰNG CHỨNG THỰC NGHIỆM (`experiments/experiment_index.csv`)

Nhằm giúp Thầy/Cô phản biện tra cứu tức thì bất kỳ mô hình nào mà không cần duyệt cây thư mục phức tạp, đề xuất xây dựng duy nhất **MỘT** bảng chỉ mục `experiments/experiment_index.csv` với cấu trúc 9 cột chuẩn:

| run_id | architecture | seed | best_epoch | checkpoint | log | result | commit | status |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `CONF_SEQUENCE_ONLY_seed42_1789413645` | SEQUENCE_ONLY | 42 | 3 | `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_1789413645/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=1.0000, ROC=1.0000` | `878a3db` | COMPLETED |
| `CONF_SEQUENCE_ONLY_seed7_1789415728` | SEQUENCE_ONLY | 7 | 6 | `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed7_1789415728/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=1.0000, ROC=1.0000` | `878a3db` | COMPLETED |
| `CONF_SEQUENCE_ONLY_seed999_1789420295` | SEQUENCE_ONLY | 999 | 6 | `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed999_1789420295/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=1.0000, ROC=1.0000` | `878a3db` | COMPLETED |
| `CONF_MULTI_VIEW_ALIGNED_seed42_1789393292` | MULTI_VIEW_ALIGNED | 42 | 6 | `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed42_1789393292/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=0.7604, ROC=0.9946` | `878a3db` | COMPLETED |
| `CONF_MULTI_VIEW_ALIGNED_seed7_1789452137` | MULTI_VIEW_ALIGNED | 7 | 4 | `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed7_1789452137/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=0.6309, ROC=0.8081` | `878a3db` | COMPLETED |
| `CONF_MULTI_VIEW_ALIGNED_seed999_1789541331` | MULTI_VIEW_ALIGNED | 999 | 5 | `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed999_1789541331/best_checkpoint.pt` | `.../TRAIN-LOG.jsonl` | `AP=0.5911, ROC=0.7693` | `878a3db` | COMPLETED |
| `CONF_GRAPH_ONLY_seed42_1789448995` | GRAPH_ONLY | 42 | - | *Historical Exploratory Checkpoint* | `.../TRAIN-LOG.jsonl` | `AP=0.7051, ROC=0.8715` | `878a3db` | HISTORICAL |
| `CONF_GRAPH_ONLY_seed7_1789449292` | GRAPH_ONLY | 7 | - | *Historical Exploratory Checkpoint* | `.../TRAIN-LOG.jsonl` | `AP=0.6159, ROC=0.7389` | `878a3db` | HISTORICAL |
| `CONF_GRAPH_ONLY_seed999_1789449583` | GRAPH_ONLY | 999 | - | *Historical Exploratory Checkpoint* | `.../TRAIN-LOG.jsonl` | `AP=0.6872, ROC=0.8322` | `878a3db` | HISTORICAL |

---

## 10. TRẢI NGHIỆM ĐỌC CỦA NGƯỜI PHẢN BIỆN (REVIEWER EXPERIENCE)

Hành trình trải nghiệm của Thầy/Cô phản biện được tối ưu hóa theo lộ trình 4 bước tinh giản:

```text
[Mở README.md]
     │
     ▼
[Hiểu mục tiêu đề tài & cấu trúc gọn gàng (trong 2 phút)]
     │
     ▼
[Mở HUONG_DAN_CHAY_VA_XAC_MINH.md]
     │
     ▼
[Chạy 1 lệnh kiểm tra GPU & 1 lệnh đánh giá tái lập số liệu AP=1.0000 (trong 1 phút)]
```

- Không bắt buộc người đọc phải đi qua hàng chục tài liệu đặc tả trung gian.
- Mọi phát ngôn khoa học đều dẫn trực tiếp tới dòng lệnh kiểm tra và tệp kết quả JSON cụ thể.

---

## 11. KẾ HOẠCH HÀNH ĐỘNG TRIỂN KHAI TIẾP THEO (NEXT IMPLEMENTATION STEPS)

Sau khi kế hoạch này được thông qua, các bước triển khai kỹ thuật tiếp theo sẽ là:

1. **Bước 1:** Tạo tệp `experiments/experiment_index.csv` theo cấu trúc 9 cột đã thống nhất.
2. **Bước 2:** Viết lại tệp `README.md` mới bằng tiếng Việt tự nhiên, súc tích theo đề cương Mục 3.
3. **Bước 3:** Soạn thảo tệp `HUONG_DAN_CHAY_VA_XAC_MINH.md` theo đề cương Mục 4.
4. **Bước 4:** Thiết lập thư mục `manual_reproduction/`, biên soạn `manual_reproduction/README.md` và script `manual_reproduction/run_manual_sequence42.ps1` để sinh viên tự thực hành.
5. **Bước 5:** Di chuyển/dọn dẹp các tệp script tạm, tệp rác khỏi thư mục gốc để đạt được cấu trúc cây thư mục sạch sẽ như Mục 2.

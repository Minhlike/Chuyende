"""
Academic Diagram Renderer for Chapter 1 Visuals
Generates pristine monochrome vector-quality figures using Matplotlib with Times New Roman typography.
Enforces: White background, 1pt crisp black outlines, black connector arrows, Times New Roman font, no gradients/shadows/3D.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set global matplotlib typography to match thesis style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 10
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['figure.autolayout'] = False

OUTPUT_DIR = Path(r"D:\Research\figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_fig_1_1() -> str:
    """FIG 1.1: Hierarchy of Log Observation Units and Dimensional Trade-offs."""
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 6 Stacked levels (from bottom to top)
    levels = [
        ("[1] Luồng nhật ký thô (Raw Telemetry Streams)", "Nhật ký kiểm toán Linux Auditd, Windows Sysmon, Zeek, eBPF", 7),
        ("[2] Mức Từ tố (Token Level)", "Chuỗi con, từ khóa tĩnh, tham số rời rạc, mã lỗi hex", 22.5),
        ("[3] Mức Sự kiện (Event Level)", r"Bản ghi telemetry đơn lẻ tại mốc thời gian $t$", 38),
        ("[4] Mức Chuỗi / Phiên (Sequence / Session Level)", r"Chuỗi sự kiện cục bộ $[e_{t-k+1}, \dots, e_t]$ theo tiến trình/thời gian", 53.5),
        ("[5] Mức Thực thể (Entity Level)", "Lịch sử hành vi gom cụm theo Host, User, Process", 69),
        ("[6] Mức Đồ thị Nguồn gốc (Provenance Graph Level)", "Mô hình hóa toàn diện quan hệ luồng phụ thuộc đa thực thể", 84.5),
    ]

    for label, sub, y in levels:
        rect = patches.FancyBboxPatch(
            (17, y), 66, 12,
            boxstyle="round,pad=0.5,rounding_size=1.5",
            facecolor="white", edgecolor="black", linewidth=1.0
        )
        ax.add_patch(rect)
        ax.text(50, y + 7.2, label, ha="center", va="center", fontsize=10.0, fontweight="bold", color="black")
        ax.text(50, y + 2.5, sub, ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#222222")

    # Left upward arrow (Context Richness)
    ax.annotate(
        "", xy=(10, 95), xytext=(10, 7),
        arrowprops=dict(facecolor="black", edgecolor="black", arrowstyle="-|>", lw=1.3, mutation_scale=14)
    )
    ax.text(7, 51, "Bảo toàn ngữ cảnh & Quan hệ an ninh (Context Richness) ↑",
            ha="center", va="center", rotation=90, fontsize=9.0, fontweight="bold", color="black")

    # Right upward arrow (Resource Cost)
    ax.annotate(
        "", xy=(90, 95), xytext=(90, 7),
        arrowprops=dict(facecolor="black", edgecolor="black", arrowstyle="-|>", lw=1.3, mutation_scale=14)
    )
    ax.text(93, 51, "Chi phí tính toán & Trạng thái bộ nhớ (Resource Cost) ↑",
            ha="center", va="center", rotation=270, fontsize=9.0, fontweight="bold", color="black")

    plt.tight_layout(pad=0.2)
    out_path = OUTPUT_DIR / "fig_1_1_observation_hierarchy.png"
    plt.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()
    return str(out_path)


def generate_fig_1_2() -> str:
    """FIG 1.2: Multi-label Non-linear MITRE ATT&CK Behavioral Evidence Space."""
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Container A (Left)
    box_a = patches.Rectangle((2, 4), 45, 92, facecolor="white", edgecolor="black", linewidth=1.0)
    ax.add_patch(box_a)
    ax.text(24.5, 91, "(A) Giả định chuỗi tuyến tính (Kill Chain)", ha="center", va="center", fontsize=10.0, fontweight="bold")
    ax.text(24.5, 85, "Chuỗi đơn tuyến, thứ tự nghiêm ngặt", ha="center", va="center", fontsize=8.5, fontstyle="italic")

    steps_a = [
        ("1. Thâm nhập ban đầu\n(Initial Access)", 63),
        ("2. Thực thi & Duy trì\n(Execution → Persistence)", 40),
        ("3. Leo quyền & Đánh cắp\n(PrivEsc → Exfiltration)", 17),
    ]
    for lbl, y in steps_a:
        rect = patches.FancyBboxPatch((6, y), 37, 15, boxstyle="round,pad=0.3,rounding_size=1.0",
                                      facecolor="white", edgecolor="black", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(24.5, y + 7.5, lbl, ha="center", va="center", fontsize=8.5, fontweight="bold")

    # Downward connectors in A
    ax.annotate("", xy=(24.5, 55), xytext=(24.5, 63), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(24.5, 32), xytext=(24.5, 40), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))

    # Limitation note
    ax.text(24.5, 8, "Hạn chế: Bỏ sót các kỹ thuật APT phi tuyến", ha="center", va="center", fontsize=8.0, fontstyle="italic", color="#333333")

    # Container B (Right)
    box_b = patches.Rectangle((53, 4), 45, 92, facecolor="white", edgecolor="black", linewidth=1.0)
    ax.add_patch(box_b)
    ax.text(75.5, 91, "(B) Không gian Bằng chứng ATT&CK", ha="center", va="center", fontsize=10.0, fontweight="bold")
    ax.text(75.5, 85, "Hành vi phi tuyến tính & Kích hoạt đa nhãn", ha="center", va="center", fontsize=8.5, fontstyle="italic")

    features_b = [
        ("[1] Nhảy cóc (Step Skipping):\nKhai thác RCE → Exfiltration trực tiếp", 63),
        ("[2] Lặp vòng (Looping & Interleaving):\nDiscovery ↔ Credential Access", 40),
        ("[3] Phân nhánh (Parallel Branching):\nKhởi tạo đa tiến trình con song song", 17),
    ]
    for lbl, y in features_b:
        rect = patches.FancyBboxPatch((56, y), 39, 15, boxstyle="round,pad=0.3,rounding_size=1.0",
                                      facecolor="white", edgecolor="black", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(75.5, y + 7.5, lbl, ha="center", va="center", fontsize=8.5)

    # Invariant statement in B
    ax.text(75.5, 8, "Bất biến: ATT&CK ≠ Chuỗi Markov đơn tuyến", ha="center", va="center", fontsize=8.5, fontweight="bold")

    plt.tight_layout(pad=0.2)
    out_path = OUTPUT_DIR / "fig_1_2_evidence_space.png"
    plt.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()
    return str(out_path)


def generate_fig_1_3() -> str:
    """FIG 1.3: Three-Tier Research Architecture and Central Role of Representation z."""
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    boxes = [
        ("Dữ liệu nhật ký thô (Raw Telemetry Streams)", "Auditd, Sysmon, Zeek, eBPF", 84, 13, 1.0),
        ("TẦNG 1: Trích xuất đặc trưng & Tiền xử lý (Feature Extraction)", "Chuẩn hóa cấu trúc trường cú pháp và trích xuất sự kiện sơ cấp", 65, 13, 1.0),
        ("TẦNG 2: Học biểu diễn bất biến (Representation Learning)", "TRỌNG TÂM ĐỀ TÀI — Ràng buộc chặt chẽ theo Representation Contract", 46, 13, 1.8),
        (r"Vector biểu diễn đóng gói: $\mathbf{z} \in \mathbb{R}^d$", "Bảo toàn tín hiệu an ninh • Bất biến cú pháp • Triệt tiêu Shortcut", 27, 13, 1.4),
        ("TẦNG 3: Đánh giá thăm dò đóng băng (Frozen Linear Probe)", r"Khóa cố định tham số $\theta$ — Đánh giá phân loại & quy kết MITRE ATT&CK", 8, 13, 1.0),
    ]

    for title, sub, y, h, lw in boxes:
        rect = patches.FancyBboxPatch(
            (8, y), 84, h,
            boxstyle="round,pad=0.5,rounding_size=1.2",
            facecolor="white", edgecolor="black", linewidth=lw
        )
        ax.add_patch(rect)
        ax.text(50, y + h * 0.65, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color="black")
        ax.text(50, y + h * 0.25, sub, ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#222222")

    # Downward connectors between boxes
    connectors = [
        (84, 78, ""),
        (65, 59, r"$f_\theta(X)$"),
        (46, 40, r"$\mathbf{z} = f_\theta(X)$"),
        (27, 21, r"$\mathbf{z}$ (Frozen)"),
    ]

    for y_top, y_bot, lbl in connectors:
        ax.annotate(
            "", xy=(50, y_bot), xytext=(50, y_top),
            arrowprops=dict(facecolor="black", edgecolor="black", arrowstyle="-|>", lw=1.2, mutation_scale=12)
        )
        if lbl:
            ax.text(56, (y_top + y_bot) / 2, lbl, ha="left", va="center", fontsize=9.0, fontweight="bold", color="black")

    plt.tight_layout(pad=0.2)
    out_path = OUTPUT_DIR / "fig_1_3_three_tier_architecture.png"
    plt.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()
    return str(out_path)


def generate_fig_1_4() -> str:
    """FIG 1.4: Map of Three Log Representation Families to Five Research Gaps."""
    fig, ax = plt.subplots(figsize=(7.2, 3.5), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Left Column: 3 Methodological Families
    fam1 = patches.Rectangle((2, 68), 44, 27, facecolor="white", edgecolor="black", linewidth=1.0)
    ax.add_patch(fam1)
    ax.text(24, 89, "1. Nhóm Thống kê / Cú pháp (Drain, PCA)", ha="center", va="center", fontsize=9.0, fontweight="bold")
    ax.text(4, 76.5, "• Ưu: Tốc độ tuyến tính $\\mathcal{O}(N)$, tài nguyên thấp\n• Giới hạn: Mất tham số động, lan truyền sai số parser", ha="left", va="center", fontsize=8.0)

    fam2 = patches.Rectangle((2, 38), 44, 27, facecolor="white", edgecolor="black", linewidth=1.0)
    ax.add_patch(fam2)
    ax.text(24, 59, "2. Nhóm Chuỗi Semantic (DeepLog, LogBERT)", ha="center", va="center", fontsize=9.0, fontweight="bold")
    ax.text(4, 46.5, "• Ưu: Nắm bắt ngữ nghĩa chuỗi thời gian cục bộ\n• Giới hạn: Chi phí $\\mathcal{O}(L^2)$, thiếu tầm nhìn đa thực thể", ha="left", va="center", fontsize=8.0)

    fam3 = patches.Rectangle((2, 8), 44, 27, facecolor="white", edgecolor="black", linewidth=1.0)
    ax.add_patch(fam3)
    ax.text(24, 29, "3. Nhóm Đồ thị Nguồn gốc (UNICORN, MAGIC)", ha="center", va="center", fontsize=9.0, fontweight="bold")
    ax.text(4, 16.5, "• Ưu: Mô hình hóa toàn diện quan hệ đa thực thể\n• Giới hạn: Bùng nổ phụ thuộc, Over-smoothing/squashing", ha="left", va="center", fontsize=8.0)

    # Converging Connectors
    ax.annotate("", xy=(51, 51.5), xytext=(46, 81.5), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(51, 51.5), xytext=(46, 51.5), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(51, 51.5), xytext=(46, 21.5), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))

    # Right Column: 5 Research Gaps & Questions
    gaps_box = patches.Rectangle((51, 8), 47, 87, facecolor="white", edgecolor="black", linewidth=1.2)
    ax.add_patch(gaps_box)
    ax.text(74.5, 89, "5 KHOẢNG TRỐNG CỐT LÕI (RQ1–RQ5)", ha="center", va="center", fontsize=9.5, fontweight="bold")
    
    gaps_items = [
        ("• Gap 1 (RQ1): Mất mát ngữ nghĩa tham số", 75),
        ("• Gap 2 (RQ2): Suy thoái gióng hàng đa view", 60),
        ("• Gap 3 (RQ3): Rò rỉ thông tin, shortcut & trôi dạt", 45),
        ("• Gap 4 (RQ4): Nhãn thô & Nhiễu Admin-noise", 30),
        ("• Gap 5 (RQ5): Đánh đổi Liên kết & Riêng tư", 15),
    ]
    for g_txt, y in gaps_items:
        ax.text(53, y, g_txt, ha="left", va="center", fontsize=8.5, fontweight="bold")

    plt.tight_layout(pad=0.2)
    out_path = OUTPUT_DIR / "fig_1_4_method_to_gaps_map.png"
    plt.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()
    return str(out_path)


def generate_fig_2_1() -> str:
    """FIG 2.1: Dual-Plane Architecture: Offline Training Plane vs Online Streaming Inference Plane."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Top Frame: Training Plane
    train_frame = patches.Rectangle((2, 52), 96, 45, facecolor="white", edgecolor="black", linewidth=1.2)
    ax.add_patch(train_frame)
    ax.text(50, 93.5, "MẶT PHẲNG HUẤN LUYỆN (TRAINING PLANE — OFFLINE SELF-SUPERVISED)", ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax.text(50, 89.0, r"Tối ưu hóa tham số mạng $f_\theta$ trên dữ liệu nền tảng lịch sử (Không nhãn APT)", ha="center", va="center", fontsize=8.0, fontstyle="italic")

    # Training Plane Sub-boxes
    t_boxes = [
        (r"Dữ liệu telemetry lịch sử" + "\n" + r"$\mathcal{D}_{\mathrm{train}}$ (Auditd/Sysmon)", 5, 56, 26, 28),
        ("Trích xuất Đa góc nhìn\n(Sequential + Graph)", 37, 56, 26, 28),
        (r"Tối ưu hóa Gióng hàng" + "\n" + r"$\min \mathcal{L}_{\mathrm{align}}(\mathbf{z}_{\mathrm{seq}}, \mathbf{z}_{\mathrm{graph}})$", 69, 56, 26, 28),
    ]
    for lbl, x, y, w, h in t_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                                      facecolor="white", edgecolor="black", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, lbl, ha="center", va="center", fontsize=8.0, fontweight="bold")

    # Connectors in Training Plane
    ax.annotate("", xy=(37, 70), xytext=(31, 70), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(69, 70), xytext=(63, 70), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))

    # Transfer Arrow (Trained Weights theta*)
    ax.annotate("", xy=(50, 48), xytext=(50, 52), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.4, mutation_scale=14))
    ax.text(50, 50, r"Tham số tối ưu hóa $\theta^*$ (Đóng băng / Frozen)", ha="center", va="center", fontsize=8.0, fontweight="bold", backgroundcolor="white")

    # Bottom Frame: Streaming Inference Plane
    inf_frame = patches.Rectangle((2, 3), 96, 45, facecolor="white", edgecolor="black", linewidth=1.2)
    ax.add_patch(inf_frame)
    ax.text(50, 44.5, "MẶT PHẲNG SUY LUẬN DÒNG (STREAMING INFERENCE PLANE — ONLINE CAUSAL)", ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax.text(50, 40.0, r"Cập nhật trạng thái hữu hạn $\mathcal{S}_t$ và trích xuất vector $\mathbf{z}_t$ đơn lượt (Zero Lookahead)", ha="center", va="center", fontsize=8.0, fontstyle="italic")

    # Inference Plane Sub-boxes
    i_boxes = [
        ("Luồng log trực tuyến\n" + r"$e_t \in \mathcal{L}_{1:t}$", 4, 7, 20, 28),
        ("Cập nhật trạng thái\n" + r"$\mathcal{S}_t = \mathrm{Upd}(\mathcal{S}_{t-1}, e_t)$" + "\n(TTL, Evict, Decay)", 27, 7, 22, 28),
        ("Trích xuất biểu diễn\n" + r"$\mathbf{z}_t = f_{\theta^*}(\mathcal{S}_t) \in \mathbb{R}^d$" + "\n(Thời gian thực)", 52, 7, 21, 28),
        ("Frozen Probe\n" + r"$\hat{y} = \sigma(\mathbf{W}^\top \mathbf{z}_t + b)$" + "\n(Quy kết ATT&CK)", 76, 7, 20, 28),
    ]
    for lbl, x, y, w, h in i_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                                      facecolor="white", edgecolor="black", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, lbl, ha="center", va="center", fontsize=7.5, fontweight="bold")

    # Connectors in Inference Plane
    ax.annotate("", xy=(27, 21), xytext=(24, 21), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(52, 21), xytext=(49, 21), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))
    ax.annotate("", xy=(76, 21), xytext=(73, 21), arrowprops=dict(arrowstyle="-|>", facecolor="black", lw=1.0, mutation_scale=10))

    plt.tight_layout(pad=0.2)
    out_path = OUTPUT_DIR / "fig_2_1_dual_plane_architecture.png"
    plt.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()
    return str(out_path)


def generate_all_figures():
    f1 = generate_fig_1_1()
    f2 = generate_fig_1_2()
    f3 = generate_fig_1_3()
    f4 = generate_fig_1_4()
    f5 = generate_fig_2_1()
    print(f"Generated Figure 1.1: {f1}")
    print(f"Generated Figure 1.2: {f2}")
    print(f"Generated Figure 1.3: {f3}")
    print(f"Generated Figure 1.4: {f4}")
    print(f"Generated Figure 2.1: {f5}")
    return [f1, f2, f3, f4, f5]


if __name__ == "__main__":
    generate_all_figures()

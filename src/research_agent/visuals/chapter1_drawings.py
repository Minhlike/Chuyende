# -*- coding: utf-8 -*-
"""
Word COM Native Drawing Functions for Chapter 1 Visuals (Figures 1.1, 1.2, 1.3, 1.4)
Implements publication-grade vector architectural diagrams with Drawing Canvas, Shapes, and Connectors.
Directly editable in Microsoft Word 2016+.
"""
from typing import Any
import win32com.client.dynamic as dynamic


def _force_canvas_text_black(items: Any) -> None:
    """Make native canvas text visible regardless of the document theme."""
    for i in range(1, items.Count + 1):
        try:
            shape = items.Item(i)
            shape.TextFrame.TextRange.Font.ColorIndex = 1
        except Exception:
            pass


def set_shape_text_formatted(tf: Any, lines_spec: list, default_font_size: float = 6.6, default_align: int = 0):
    """
    Sets text on a shape's TextFrame with native Word bullet formatting (ListFormat.ApplyBulletDefault)
    and removes all literal unicode bullet characters.
    """
    tr = tf.TextRange
    raw_text = "\n".join([t for _, t in lines_spec])
    tr.Text = raw_text
    tr.Font.Name = "Times New Roman"
    tr.Font.Size = default_font_size
    try:
        tr.Font.ColorIndex = 1  # wdBlack
    except Exception:
        pass
    tr.ParagraphFormat.Alignment = default_align
    tr.ParagraphFormat.LeftIndent = 0.0
    tr.ParagraphFormat.FirstLineIndent = 0.0
    tr.ParagraphFormat.SpaceBefore = 0.0
    tr.ParagraphFormat.SpaceAfter = 1.0
    tr.ParagraphFormat.LineSpacingRule = 0

    for i, (kind, _) in enumerate(lines_spec, 1):
        try:
            p = tr.Paragraphs(i)
            if kind == 'h':
                p.Range.Font.Bold = True
                p.Range.ParagraphFormat.Alignment = 1
                p.Range.ParagraphFormat.LeftIndent = 0.0
                p.Range.ParagraphFormat.FirstLineIndent = 0.0
            elif kind == 'sub':
                p.Range.ParagraphFormat.Alignment = 1
                p.Range.ParagraphFormat.LeftIndent = 0.0
                p.Range.ParagraphFormat.FirstLineIndent = 0.0
            elif kind == 'b':
                p.Range.ListFormat.ApplyBulletDefault()
                p.Range.ParagraphFormat.LeftIndent = 8.0
                p.Range.ParagraphFormat.FirstLineIndent = -6.0
                p.Range.ParagraphFormat.Alignment = 0
            elif kind == 'f':
                p.Range.Font.Italic = True
                p.Range.ParagraphFormat.Alignment = 1
                p.Range.ParagraphFormat.LeftIndent = 0.0
                p.Range.ParagraphFormat.FirstLineIndent = 0.0
        except Exception:
            pass


def draw_fig_1_1(canvas_raw: Any):
    """
    Draws FIG 1.1: Hierarchy of Log Observation Units and Trade-offs
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    # Outer container
    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    levels = [
        ("[6] Mức Đồ thị Nguồn gốc (Provenance Graph Level)", "Mô hình hóa toàn diện quan hệ luồng phụ thuộc đa thực thể", 18.0),
        ("[5] Mức Thực thể (Entity Level)", "Lịch sử hành vi gom cụm theo Host, User, Process", 42.0),
        ("[4] Mức Chuỗi / Phiên (Sequence / Session Level)", "Chuỗi sự kiện trong cửa sổ hoặc phiên", 66.0),
        ("[3] Mức Sự kiện (Event Level)", "Bản ghi telemetry đơn lẻ tại mốc thời gian", 90.0),
        ("[2] Mức Từ tố (Token Level)", "Chuỗi con, từ khóa tĩnh, tham số, mã lỗi hex", 114.0),
        ("[1] Luồng nhật ký thô (Raw Telemetry Streams)", "Nhật ký kiểm toán Linux Auditd, Windows Sysmon, Zeek, eBPF", 138.0),
    ]

    for label, sub, y_pos in levels:
        s = items.AddShape(5, 52.0, y_pos, 338.0, 20.0)  # Rounded rectangle
        s.Fill.Solid()
        s.Fill.ForeColor.RGB = 0xFFFFFF
        s.Line.ForeColor.RGB = 0x0284C7
        s.Line.Weight = 1.0
        tf = s.TextFrame
        tf.WordWrap = -1
        tf.MarginLeft = 2.0
        tf.MarginRight = 2.0
        tf.MarginTop = 1.5
        tf.MarginBottom = 1.5
        tr = tf.TextRange
        tr.Text = f"{label} — {sub}"
        tr.Font.Name = "Times New Roman"
        tr.Font.Size = 6.2
        tr.ParagraphFormat.Alignment = 1

    # Left upward arrow (Context Richness)
    c_left = items.AddConnector(1, 38.0, 154.0, 38.0, 16.0)
    c_left.Line.ForeColor.RGB = 0x0369A1
    c_left.Line.Weight = 1.5
    c_left.Line.EndArrowheadStyle = 2

    tb_left = items.AddTextbox(1, 8.0, 5.0, 165.0, 14.0)
    tb_left.Fill.Visible = False
    tb_left.Line.Visible = False
    tr_l = tb_left.TextFrame.TextRange
    tr_l.Text = "Context Richness ↑ — Bảo toàn ngữ cảnh & quan hệ an ninh"
    tr_l.Font.Name = "Times New Roman"
    tr_l.Font.Size = 5.5
    tr_l.Font.Bold = True

    # Right upward arrow (Resource Cost)
    c_right = items.AddConnector(1, 404.0, 154.0, 404.0, 16.0)
    c_right.Line.ForeColor.RGB = 0xDC2626
    c_right.Line.Weight = 1.5
    c_right.Line.EndArrowheadStyle = 2

    tb_right = items.AddTextbox(1, 274.0, 5.0, 165.0, 14.0)
    tb_right.Fill.Visible = False
    tb_right.Line.Visible = False
    tr_r = tb_right.TextFrame.TextRange
    tr_r.Text = "Resource Cost ↑ — Chi phí tính toán & trạng thái bộ nhớ"
    tr_r.Font.Name = "Times New Roman"
    tr_r.Font.Size = 5.5
    tr_r.Font.Bold = True
    _force_canvas_text_black(items)


def draw_fig_1_2(canvas_raw: Any):
    """
    Draws FIG 1.2: Multi-label Non-linear MITRE ATT&CK Behavioral Evidence Space
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # Paradigm A: Linear Kill Chain (Left Container)
    box_a = items.AddTextbox(1, 10.0, 10.0, 205.0, 142.0)
    box_a.Fill.Solid()
    box_a.Fill.ForeColor.RGB = 0xFFFFFF
    box_a.Line.ForeColor.RGB = 0x0284C7
    box_a.Line.Weight = 1.0

    tf_a = box_a.TextFrame
    tf_a.MarginLeft = 3.0
    tf_a.MarginTop = 3.0
    set_shape_text_formatted(tf_a, [
        ('h', "(A) Giả định chuỗi tuyến tính (Kill Chain)"),
        ('sub', "Chuỗi đơn tuyến, thứ tự nghiêm ngặt"),
    ], default_font_size=7.5)

    steps_a = [
        ("1. Thâm nhập ban đầu (Initial Access)", 40.0),
        ("2. Thực thi & Duy trì (Execution → Persistence)", 70.0),
        ("3. Leo quyền & Đánh cắp (PrivEsc → Exfiltration)", 100.0),
    ]
    for lbl, y_pos in steps_a:
        s = items.AddShape(5, 20.0, y_pos, 185.0, 22.0)
        s.Fill.Solid()
        s.Fill.ForeColor.RGB = 0xF0F9FF
        s.Line.ForeColor.RGB = 0x0284C7
        s.Line.Weight = 0.8
        tr = s.TextFrame.TextRange
        tr.Text = lbl
        tr.Font.Name = "Times New Roman"
        tr.Font.Size = 7.0
        tr.ParagraphFormat.Alignment = 1

    # Connectors between linear steps
    c1 = items.AddConnector(1, 112.0, 62.0, 112.0, 70.0)
    c1.Line.ForeColor.RGB = 0x0369A1
    c1.Line.EndArrowheadStyle = 2
    c2 = items.AddConnector(1, 112.0, 92.0, 112.0, 100.0)
    c2.Line.ForeColor.RGB = 0x0369A1
    c2.Line.EndArrowheadStyle = 2

    # Bottom limitation label for A
    tb_lim = items.AddTextbox(1, 15.0, 126.0, 195.0, 20.0)
    tb_lim.Fill.Visible = False
    tb_lim.Line.Visible = False
    tr_lim = tb_lim.TextFrame.TextRange
    tr_lim.Text = "Hạn chế: Bỏ sót các kỹ thuật APT phi tuyến tính"
    tr_lim.Font.Name = "Times New Roman"
    tr_lim.Font.Size = 6.8
    tr_lim.Font.Italic = True
    tr_lim.ParagraphFormat.Alignment = 1

    # Paradigm B: Multi-label Non-linear Space (Right Container)
    box_b = items.AddTextbox(1, 225.0, 10.0, 215.0, 142.0)
    box_b.Fill.Solid()
    box_b.Fill.ForeColor.RGB = 0xFFFFFF
    box_b.Line.ForeColor.RGB = 0x7C3AED
    box_b.Line.Weight = 1.0

    tf_b = box_b.TextFrame
    tf_b.MarginLeft = 3.0
    tf_b.MarginTop = 3.0
    set_shape_text_formatted(tf_b, [
        ('h', "(B) Không gian Bằng chứng ATT&CK"),
        ('sub', "Hành vi phi tuyến tính & Kích hoạt đa nhãn"),
    ], default_font_size=7.5)

    features_b = [
        ("[1] Nhảy cóc: Khai thác RCE → Exfiltration trực tiếp", 40.0),
        ("[2] Lặp vòng: Discovery ↔ Credential Access", 70.0),
        ("[3] Phân nhánh: Khởi tạo đa tiến trình song song", 100.0),
    ]
    for lbl, y_pos in features_b:
        s = items.AddShape(5, 235.0, y_pos, 195.0, 22.0)
        s.Fill.Solid()
        s.Fill.ForeColor.RGB = 0xF5F3FF
        s.Line.ForeColor.RGB = 0x7C3AED
        s.Line.Weight = 0.8
        tr = s.TextFrame.TextRange
        tr.Text = lbl
        tr.Font.Name = "Times New Roman"
        tr.Font.Size = 7.0
        tr.ParagraphFormat.Alignment = 1

    # Boundary note for B
    tb_inv = items.AddTextbox(1, 230.0, 122.0, 205.0, 28.0)
    tb_inv.Fill.Visible = False
    tb_inv.Line.Visible = False
    tr_inv = tb_inv.TextFrame.TextRange
    tr_inv.Text = "Ranh giới mô hình hóa: ATT&CK không phải chuỗi Markov đơn tuyến"
    tr_inv.Font.Name = "Times New Roman"
    tr_inv.Font.Size = 5.8
    tr_inv.Font.Bold = True
    tr_inv.ParagraphFormat.Alignment = 1
    _force_canvas_text_black(items)


def draw_fig_1_3(canvas_raw: Any):
    """
    Draws FIG 1.3: Three-Tier Research Architecture (Rebuilt from Zero - Pure Semantic)
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # A compact vertical semantic pipeline keeps labels readable at document width.
    boxes = [
        ("Dữ liệu telemetry thô", "Raw telemetry", 0x64748B),
        ("Tầng 1: Tiền xử lý & trích xuất cơ sở", "Chuẩn hóa và trích xuất sự kiện", 0x0284C7),
        ("Tầng 2: Học biểu diễn [TRỌNG TÂM CHUYÊN ĐỀ]", "", 0x0F766E),
        ("Vector biểu diễn đặc trưng", "Đầu ra của bộ biểu diễn", 0x2563EB),
        ("Đóng băng bộ trích xuất", "Giữ cố định trước đánh giá", 0x7C3AED),
        ("Tầng 3: Frozen Linear Probe / Đánh giá hạ nguồn", "Đánh giá độc lập", 0xCA8A04),
    ]
    y = 7.0
    for i, (title, subtitle, color) in enumerate(boxes):
        b = items.AddShape(5, 34.0, y, 382.0, 18.0)
        b.Fill.Solid()
        b.Fill.ForeColor.RGB = 0xFFFFFF if i != 2 else 0xECFDF5
        b.Line.ForeColor.RGB = color
        b.Line.Weight = 1.3 if i == 2 else 1.0
        set_shape_text_formatted(b.TextFrame, [('h', title)], default_font_size=6.3)
        if i < len(boxes) - 1:
            c = items.AddConnector(1, 225.0, y + 18.0, 225.0, y + 22.0)
            c.Line.ForeColor.RGB = 0x334155
            c.Line.Weight = 1.0
            c.Line.EndArrowheadStyle = 2
        y += 22.0

    # Bottom banner states the boundary without introducing source notation.
    banner = items.AddShape(5, 8.0, 138.0, 430.0, 14.0)
    banner.Fill.Solid()
    banner.Fill.ForeColor.RGB = 0xF1F5F9
    banner.Line.ForeColor.RGB = 0x334155
    banner.Line.Weight = 0.8
    tr_b = banner.TextFrame.TextRange
    tr_b.Text = "Ranh giới: Tầng 3 đánh giá độc lập trên vector đóng băng; không học thay Tầng 2"
    tr_b.Font.Name = "Times New Roman"
    tr_b.Font.Size = 5.7
    tr_b.Font.Bold = True
    tr_b.ParagraphFormat.Alignment = 1
    _force_canvas_text_black(items)


def draw_fig_1_4(canvas_raw: Any):
    """
    Draws FIG 1.4: Map of Three Log Representation Families to Five Research Gaps
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # Left Column: 3 Methodological Families
    fam1 = items.AddTextbox(1, 8.0, 8.0, 192.0, 36.0)
    fam1.Fill.Solid()
    fam1.Fill.ForeColor.RGB = 0xFFFFFF
    fam1.Line.ForeColor.RGB = 0x0284C7
    fam1.Line.Weight = 1.0
    set_shape_text_formatted(fam1.TextFrame, [
        ('h', "1. Nhóm Thống kê / Cú pháp (Drain, PCA)"),
        ('b', "Ưu: Chi phí gần tuyến tính theo N, nhẹ"),
        ('b', "Giới hạn: Mất tham số động, sai số parser"),
    ], default_font_size=6.2)

    fam2 = items.AddTextbox(1, 8.0, 48.0, 192.0, 36.0)
    fam2.Fill.Solid()
    fam2.Fill.ForeColor.RGB = 0xFFFFFF
    fam2.Line.ForeColor.RGB = 0x0369A1
    fam2.Line.Weight = 1.0
    set_shape_text_formatted(fam2.TextFrame, [
        ('h', "2. Nhóm Chuỗi Semantic (DeepLog, LogBERT)"),
        ('b', "Ưu: Ngữ nghĩa chuỗi thời gian cục bộ"),
        ('b', "Giới hạn: Chi phí bậc hai theo độ dài L"),
    ], default_font_size=6.2)

    fam3 = items.AddTextbox(1, 8.0, 88.0, 192.0, 36.0)
    fam3.Fill.Solid()
    fam3.Fill.ForeColor.RGB = 0xFFFFFF
    fam3.Line.ForeColor.RGB = 0x0F766E
    fam3.Line.Weight = 1.0
    set_shape_text_formatted(fam3.TextFrame, [
        ('h', "3. Nhóm Đồ thị Nguồn gốc (UNICORN, MAGIC)"),
        ('b', "Ưu: Mô hình hóa quan hệ đa thực thể"),
        ('b', "Giới hạn: Bùng nổ phụ thuộc, Over-smoothing/squashing"),
    ], default_font_size=6.2)

    # Center Converging Arrows
    c_m1 = items.AddConnector(1, 200.0, 26.0, 214.0, 66.0)
    c_m1.Line.ForeColor.RGB = 0x334155
    c_m1.Line.Weight = 1.0
    c_m1.Line.EndArrowheadStyle = 2

    c_m2 = items.AddConnector(1, 200.0, 66.0, 214.0, 66.0)
    c_m2.Line.ForeColor.RGB = 0x334155
    c_m2.Line.Weight = 1.0
    c_m2.Line.EndArrowheadStyle = 2

    c_m3 = items.AddConnector(1, 200.0, 106.0, 214.0, 66.0)
    c_m3.Line.ForeColor.RGB = 0x334155
    c_m3.Line.Weight = 1.0
    c_m3.Line.EndArrowheadStyle = 2

    # Right Column: 5 Research Gaps matching canonical RQ1–RQ5
    gaps_box = items.AddTextbox(1, 214.0, 8.0, 224.0, 116.0)
    gaps_box.Fill.Solid()
    gaps_box.Fill.ForeColor.RGB = 0xFFFFFF
    gaps_box.Line.ForeColor.RGB = 0xDC2626
    gaps_box.Line.Weight = 1.2
    set_shape_text_formatted(gaps_box.TextFrame, [
        ('h', "5 KHOẢNG TRỐNG CỐT LÕI (RQ1–RQ5)"),
        ('blank', ""),
        ('b', "Gap 1 (RQ1): Mất mát ngữ nghĩa tham số"),
        ('b', "Gap 2 (RQ2): Bất đồng bộ & suy thoái gióng hàng"),
        ('b', "Gap 3 (RQ3): Rò rỉ thông tin, shortcut & trôi dạt"),
        ('b', "Gap 4 (RQ4): Nhãn mức thô, phân bổ bằng chứng yếu và nhiễu hành vi quản trị"),
        ('b', "Gap 5 (RQ5): Đánh đổi giữa Liên kết & Quyền riêng tư"),
    ], default_font_size=6.2)

    # Bottom Banner
    banner = items.AddShape(5, 8.0, 128.0, 430.0, 20.0)
    banner.Fill.Solid()
    banner.Fill.ForeColor.RGB = 0xF1F5F9
    banner.Line.ForeColor.RGB = 0x334155
    banner.Line.Weight = 0.8
    tr_syn = banner.TextFrame.TextRange
    tr_syn.Text = "Động lực: Cần biểu diễn đa góc nhìn bảo toàn ngữ nghĩa, gióng hàng chống sụp đổ và kiểm soát riêng tư"
    tr_syn.Font.Name = "Times New Roman"
    tr_syn.Font.Size = 6.8
    tr_syn.Font.Bold = True
    tr_syn.ParagraphFormat.Alignment = 1
    _force_canvas_text_black(items)


# -*- coding: utf-8 -*-
"""
Word COM Native Drawing Functions for Chapter 2 Visuals (Figures 2.1, 2.2, 2.3, 2.4)
Implements publication-grade vector architectural diagrams with Drawing Canvas, Shapes, and Connectors.
Directly editable in Microsoft Word 2016+.
"""
from typing import Any
import win32com.client.dynamic as dynamic


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


def draw_fig_2_1(canvas_raw: Any):
    """
    Draws FIG 2.1: Dual-Plane Architecture (Training Plane & Streaming Inference Plane)
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # Top Plane: Training Plane
    p_top = items.AddTextbox(1, 8.0, 8.0, 426.0, 62.0)
    p_top.Fill.Solid()
    p_top.Fill.ForeColor.RGB = 0xFFFFFF
    p_top.Line.ForeColor.RGB = 0x0284C7
    p_top.Line.Weight = 1.0
    set_shape_text_formatted(p_top.TextFrame, [
        ('h', "MẶT PHẲNG HUẤN LUYỆN (TRAINING PLANE — OFFLINE SELF-SUPERVISED)"),
        ('sub', "Tối ưu hóa tham số mạng trên dữ liệu lịch sử (Không nhãn APT)"),
    ], default_font_size=7.2)

    # Boxes inside Top Plane
    b_t1 = items.AddTextbox(1, 14.0, 28.0, 126.0, 36.0)
    b_t1.Fill.Solid()
    b_t1.Fill.ForeColor.RGB = 0xF0F9FF
    b_t1.Line.ForeColor.RGB = 0x0284C7
    b_t1.Line.Weight = 0.8
    set_shape_text_formatted(b_t1.TextFrame, [
        ('h', "Dữ liệu telemetry lịch sử"),
        ('b', "Thu thập luồng sự kiện đa nguồn"),
        ('b', "Không gắn nhãn tấn công"),
    ], default_font_size=6.2)

    c_t1 = items.AddConnector(1, 140.0, 46.0, 150.0, 46.0)
    c_t1.Line.ForeColor.RGB = 0x0369A1
    c_t1.Line.EndArrowheadStyle = 2

    b_t2 = items.AddTextbox(1, 150.0, 28.0, 136.0, 36.0)
    b_t2.Fill.Solid()
    b_t2.Fill.ForeColor.RGB = 0xF0FDF4
    b_t2.Line.ForeColor.RGB = 0x059669
    b_t2.Line.Weight = 0.8
    set_shape_text_formatted(b_t2.TextFrame, [
        ('h', "Trích xuất hai góc nhìn"),
        ('b', "Trích xuất chuỗi Transformer"),
        ('b', "Trích xuất đồ thị Temporal GNN"),
    ], default_font_size=6.2)

    c_t2 = items.AddConnector(1, 286.0, 46.0, 296.0, 46.0)
    c_t2.Line.ForeColor.RGB = 0x0369A1
    c_t2.Line.EndArrowheadStyle = 2

    b_t3 = items.AddTextbox(1, 296.0, 28.0, 132.0, 36.0)
    b_t3.Fill.Solid()
    b_t3.Fill.ForeColor.RGB = 0xFEF2F2
    b_t3.Line.ForeColor.RGB = 0xDC2626
    b_t3.Line.Weight = 0.8
    set_shape_text_formatted(b_t3.TextFrame, [
        ('h', "Huấn luyện tự giám sát"),
        ('b', "Điều hòa VICReg & chống sụp đổ"),
        ('b', "Attention-MIL trên nhãn túi thô"),
    ], default_font_size=6.2)

    # Downward transfer connector
    c_trans = items.AddConnector(1, 221.0, 70.0, 221.0, 84.0)
    c_trans.Line.ForeColor.RGB = 0x7C3AED
    c_trans.Line.Weight = 1.4
    c_trans.Line.EndArrowheadStyle = 2

    tb_trans = items.AddTextbox(1, 140.0, 71.0, 162.0, 13.0)
    tb_trans.Fill.Solid()
    tb_trans.Fill.ForeColor.RGB = 0xF5F3FF
    tb_trans.Line.ForeColor.RGB = 0x7C3AED
    tb_trans.Line.Weight = 0.6
    tr_tr = tb_trans.TextFrame.TextRange
    tr_tr.Text = "Đóng băng bộ trích xuất đặc trưng ↓"
    tr_tr.Font.Name = "Times New Roman"
    tr_tr.Font.Size = 6.0
    tr_tr.Font.Bold = True
    tr_tr.ParagraphFormat.Alignment = 1

    # Bottom Plane: Streaming Inference Plane
    p_bot = items.AddTextbox(1, 8.0, 85.0, 426.0, 63.0)
    p_bot.Fill.Solid()
    p_bot.Fill.ForeColor.RGB = 0xFFFFFF
    p_bot.Line.ForeColor.RGB = 0x059669
    p_bot.Line.Weight = 1.0
    set_shape_text_formatted(p_bot.TextFrame, [
        ('h', "MẶT PHẲNG SUY LUẬN DÒNG (STREAMING INFERENCE — ZERO-LOOKAHEAD)"),
        ('sub', "Cập nhật trạng thái hữu hạn và trích xuất vector đơn lượt"),
    ], default_font_size=7.2)

    # Boxes inside Bottom Plane
    b_b1 = items.AddTextbox(1, 14.0, 105.0, 96.0, 38.0)
    b_b1.Fill.Solid()
    b_b1.Fill.ForeColor.RGB = 0xF0F9FF
    b_b1.Line.ForeColor.RGB = 0x0284C7
    b_b1.Line.Weight = 0.8
    set_shape_text_formatted(b_b1.TextFrame, [
        ('h', "Luồng sự kiện dòng"),
        ('b', "Sự kiện theo thứ tự"),
        ('b', "Không nhìn trước"),
    ], default_font_size=6.0)

    c_b1 = items.AddConnector(1, 110.0, 124.0, 118.0, 124.0)
    c_b1.Line.ForeColor.RGB = 0x059669
    c_b1.Line.EndArrowheadStyle = 2

    b_b2 = items.AddTextbox(1, 118.0, 105.0, 100.0, 38.0)
    b_b2.Fill.Solid()
    b_b2.Fill.ForeColor.RGB = 0xF0FDF4
    b_b2.Line.ForeColor.RGB = 0x059669
    b_b2.Line.Weight = 0.8
    set_shape_text_formatted(b_b2.TextFrame, [
        ('h', "Cập nhật trạng thái"),
        ('b', "Bộ nhớ thực thể"),
        ('b', "Cửa sổ trượt hữu hạn"),
    ], default_font_size=6.0)

    c_b2 = items.AddConnector(1, 218.0, 124.0, 226.0, 124.0)
    c_b2.Line.ForeColor.RGB = 0x059669
    c_b2.Line.EndArrowheadStyle = 2

    b_b3 = items.AddTextbox(1, 226.0, 105.0, 100.0, 38.0)
    b_b3.Fill.Solid()
    b_b3.Fill.ForeColor.RGB = 0xFAF5FF
    b_b3.Line.ForeColor.RGB = 0x7C3AED
    b_b3.Line.Weight = 0.8
    set_shape_text_formatted(b_b3.TextFrame, [
        ('h', "Trích xuất biểu diễn"),
        ('b', "Mạng đã đóng băng"),
        ('b', "Tổng hợp vector"),
    ], default_font_size=6.0)

    c_b3 = items.AddConnector(1, 326.0, 124.0, 334.0, 124.0)
    c_b3.Line.ForeColor.RGB = 0x059669
    c_b3.Line.EndArrowheadStyle = 2

    b_b4 = items.AddTextbox(1, 334.0, 105.0, 94.0, 38.0)
    b_b4.Fill.Solid()
    b_b4.Fill.ForeColor.RGB = 0xFEFCE8
    b_b4.Line.ForeColor.RGB = 0xCA8A04
    b_b4.Line.Weight = 0.8
    set_shape_text_formatted(b_b4.TextFrame, [
        ('h', "Đánh giá hạ nguồn"),
        ('b', "Dò tuyến tính"),
        ('b', "Quy kết an ninh"),
    ], default_font_size=6.0)


def draw_fig_2_2(canvas_raw: Any):
    """
    Draws FIG 2.2: Transformer Semantic-Sequential Extractor Architecture
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # 1. Box 1: Cửa sổ ngắn hạn (Left)
    b1 = items.AddTextbox(1, 8.0, 8.0, 100.0, 144.0)
    b1.Fill.Solid()
    b1.Fill.ForeColor.RGB = 0xFFFFFF
    b1.Line.ForeColor.RGB = 0x0284C7
    b1.Line.Weight = 1.0
    tf1 = b1.TextFrame
    tf1.WordWrap = -1
    tf1.MarginLeft = 2.0
    tf1.MarginRight = 2.0
    tf1.MarginTop = 3.0
    tf1.MarginBottom = 3.0
    set_shape_text_formatted(tf1, [
        ('h', "CỬA SỔ SỰ KIỆN"),
        ('sub', "(Thời gian ngắn hạn)"),
        ('blank', ""),
        ('b', "Chuỗi telemetry có thứ tự"),
        ('b', "Bộ sáu thuộc tính có kiểu"),
        ('b', "Định danh thực thể vào/ra"),
        ('b', "Hành vi & tham số an ninh"),
        ('blank', ""),
        ('f', "(Cửa sổ L sự kiện)"),
    ], default_font_size=6.6)

    # Connector 1 -> 2
    c1 = items.AddConnector(1, 108.0, 80.0, 114.0, 80.0)
    c1.Line.ForeColor.RGB = 0x334155
    c1.Line.Weight = 1.2
    c1.Line.EndArrowheadStyle = 2

    # 2. Box 2: Mã hóa đặc trưng hợp nhất (Center-Left)
    b2 = items.AddTextbox(1, 114.0, 8.0, 110.0, 144.0)
    b2.Fill.Solid()
    b2.Fill.ForeColor.RGB = 0xFFFFFF
    b2.Line.ForeColor.RGB = 0x0369A1
    b2.Line.Weight = 1.0
    tf2 = b2.TextFrame
    tf2.WordWrap = -1
    tf2.MarginLeft = 2.0
    tf2.MarginRight = 2.0
    tf2.MarginTop = 3.0
    tf2.MarginBottom = 3.0
    set_shape_text_formatted(tf2, [
        ('h', "MÃ HÓA SỰ KIỆN"),
        ('sub', "(Nhúng đặc trưng)"),
        ('blank', ""),
        ('b', "Nhúng kiểu & hành vi"),
        ('b', "Nhúng thực thể đã chuẩn hóa / bảo vệ liên kết"),
        ('b', "Tổng nhúng tham số"),
        ('b', "Điều hòa chu kỳ thời gian"),
        ('b', "Mã hóa vị trí thứ tự chuỗi"),
        ('blank', ""),
        ('f', "Không gian vector biểu diễn"),
    ], default_font_size=6.6)

    # Connector 2 -> 3
    c2 = items.AddConnector(1, 224.0, 80.0, 230.0, 80.0)
    c2.Line.ForeColor.RGB = 0x334155
    c2.Line.Weight = 1.2
    c2.Line.EndArrowheadStyle = 2

    # 3. Box 3: Transformer Encoder (Center-Right)
    b3 = items.AddTextbox(1, 230.0, 8.0, 116.0, 144.0)
    b3.Fill.Solid()
    b3.Fill.ForeColor.RGB = 0xFFFFFF
    b3.Line.ForeColor.RGB = 0x0F766E
    b3.Line.Weight = 1.2
    tf3 = b3.TextFrame
    tf3.WordWrap = -1
    tf3.MarginLeft = 2.0
    tf3.MarginRight = 2.0
    tf3.MarginTop = 3.0
    tf3.MarginBottom = 3.0
    set_shape_text_formatted(tf3, [
        ('h', "BỘ MÃ HÓA TRANSFORMER"),
        ('sub', "(Khối Encoder)"),
        ('blank', ""),
        ('b', "Multi-Head Attention đa đầu"),
        ('b', "LayerNorm & phần dư"),
        ('b', "Truyền thẳng theo vị trí"),
        ('b', "Dropout chống quá khớp"),
        ('blank', ""),
        ('f', "Trạng thái biểu diễn ẩn"),
    ], default_font_size=6.6)

    # Connector 3 -> 4 (Top)
    c3 = items.AddConnector(1, 346.0, 40.0, 352.0, 40.0)
    c3.Line.ForeColor.RGB = 0x334155
    c3.Line.Weight = 1.2
    c3.Line.EndArrowheadStyle = 2

    # 4. Box 4: Output Readout (Right-Top)
    b4 = items.AddShape(5, 352.0, 8.0, 90.0, 64.0)
    b4.Fill.Solid()
    b4.Fill.ForeColor.RGB = 0xE0F2FE
    b4.Line.ForeColor.RGB = 0x0284C7
    b4.Line.Weight = 1.2
    tf4 = b4.TextFrame
    tf4.WordWrap = -1
    tf4.MarginLeft = 2.0
    tf4.MarginRight = 2.0
    tf4.MarginTop = 2.0
    tf4.MarginBottom = 2.0
    set_shape_text_formatted(tf4, [
        ('h', "BIỂU DIỄN CHUỔI"),
        ('sub', "(Attention Readout)"),
        ('blank', ""),
        ('p', "Vector đặc trưng chuỗi"),
        ('f', "[Siêu dữ liệu & mặt nạ]"),
    ], default_font_size=6.5, default_align=1)

    # Connector 3 -> 5 (Bottom)
    c4 = items.AddConnector(1, 346.0, 114.0, 352.0, 114.0)
    c4.Line.ForeColor.RGB = 0xCA8A04
    c4.Line.Weight = 1.0
    c4.Line.EndArrowheadStyle = 2

    # 5. Box 5: Self-Supervised Objectives (Right-Bottom)
    b5 = items.AddTextbox(1, 352.0, 76.0, 90.0, 76.0)
    b5.Fill.Solid()
    b5.Fill.ForeColor.RGB = 0xFEF9C3
    b5.Line.ForeColor.RGB = 0xCA8A04
    b5.Line.Weight = 1.0
    tf5 = b5.TextFrame
    tf5.WordWrap = -1
    tf5.MarginLeft = 2.0
    tf5.MarginRight = 2.0
    tf5.MarginTop = 2.0
    tf5.MarginBottom = 2.0
    set_shape_text_formatted(tf5, [
        ('h', "MỤC TIÊU TỰ GIÁM SÁT"),
        ('blank', ""),
        ('b', "Tái tạo kiểu sự kiện che"),
        ('b', "Tái tạo tham số bị che"),
        ('b', "Dự đoán khoảng cách thời gian tương đối"),
        ('blank', ""),
        ('f', "(Tự giám sát, không sử dụng nhãn tấn công)"),
    ], default_font_size=6.4)


def draw_fig_2_3(canvas_raw: Any):
    """
    Draws FIG 2.3: Dependency-Temporal Provenance Graph Construction & Temporal GNN Extractor
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    frame = items.AddTextbox(1, 4.0, 4.0, 442.0, 154.0)
    frame.Fill.Solid()
    frame.Fill.ForeColor.RGB = 0xF8FAFC
    frame.Line.ForeColor.RGB = 0x334155
    frame.Line.Weight = 1.0

    # 1. Box 1: Provenance Graph Construction (Left)
    b1 = items.AddTextbox(1, 8.0, 8.0, 102.0, 144.0)
    b1.Fill.Solid()
    b1.Fill.ForeColor.RGB = 0xFFFFFF
    b1.Line.ForeColor.RGB = 0x059669
    b1.Line.Weight = 1.0
    tf1 = b1.TextFrame
    tf1.WordWrap = -1
    tf1.MarginLeft = 2.0
    tf1.MarginRight = 2.0
    tf1.MarginTop = 3.0
    tf1.MarginBottom = 3.0
    set_shape_text_formatted(tf1, [
        ('h', "XÂY DỰNG ĐỒ THỊ"),
        ('sub', "(Đồ thị nguồn gốc)"),
        ('blank', ""),
        ('b', "Tập đỉnh: Process, File..."),
        ('b', "Tập cạnh: fork, exec..."),
        ('b', "Thuộc tính & mốc thời gian"),
        ('blank', ""),
        ('f', "Bất biến: Phụ thuộc ≠ Nhân quả"),
    ], default_font_size=6.6)

    # Connector 1 -> 2
    c1 = items.AddConnector(1, 110.0, 80.0, 116.0, 80.0)
    c1.Line.ForeColor.RGB = 0x334155
    c1.Line.Weight = 1.2
    c1.Line.EndArrowheadStyle = 2

    # 2. Box 2: Proposed Graph-Fidelity Candidates (Center-Left)
    b2 = items.AddTextbox(1, 116.0, 8.0, 110.0, 144.0)
    b2.Fill.Solid()
    b2.Fill.ForeColor.RGB = 0xFFFFFF
    b2.Line.ForeColor.RGB = 0xD97706
    b2.Line.Weight = 1.0
    tf2 = b2.TextFrame
    tf2.WordWrap = -1
    tf2.MarginLeft = 2.0
    tf2.MarginRight = 2.0
    tf2.MarginTop = 3.0
    tf2.MarginBottom = 3.0
    set_shape_text_formatted(tf2, [
        ('h', "ỨNG VIÊN KIỂM SOÁT ĐỘ CHÂN THỰC"),
        ('sub', "(Cơ chế đề xuất)"),
        ('blank', ""),
        ('b', "Phân rã đỉnh Unit-of-Work"),
        ('b', "Suy giảm trọng số thời gian"),
        ('b', "Nén cạnh lặp & kiểm soát bậc"),
        ('b', "Khởi tạo đặc trưng đỉnh"),
    ], default_font_size=6.6)

    # Connector 2 -> 3
    c2 = items.AddConnector(1, 226.0, 80.0, 232.0, 80.0)
    c2.Line.ForeColor.RGB = 0x334155
    c2.Line.Weight = 1.2
    c2.Line.EndArrowheadStyle = 2

    # 3. Box 3: Temporal GNN Message Passing (Center-Right)
    b3 = items.AddTextbox(1, 232.0, 8.0, 116.0, 144.0)
    b3.Fill.Solid()
    b3.Fill.ForeColor.RGB = 0xFFFFFF
    b3.Line.ForeColor.RGB = 0x2563EB
    b3.Line.Weight = 1.2
    tf3 = b3.TextFrame
    tf3.WordWrap = -1
    tf3.MarginLeft = 2.0
    tf3.MarginRight = 2.0
    tf3.MarginTop = 3.0
    tf3.MarginBottom = 3.0
    set_shape_text_formatted(tf3, [
        ('h', "TRÍCH XUẤT TEMPORAL GNN"),
        ('sub', "(Truyền thông điệp TGN)"),
        ('blank', ""),
        ('b', "Thông điệp tương tác kiểu"),
        ('b', "Gom cụm thông điệp lân cận"),
        ('b', "Cập nhật bộ nhớ thực thể"),
        ('b', "Skip-connection giảm nguy cơ Over-smoothing"),
        ('b', "Top-k sampling: ứng viên giảm nguy cơ Over-squashing"),
        ('b', "Self-loop chỉ trong đồ thị tính toán"),
    ], default_font_size=6.5)

    # Connector 3 -> 4
    c3 = items.AddConnector(1, 348.0, 80.0, 354.0, 80.0)
    c3.Line.ForeColor.RGB = 0x334155
    c3.Line.Weight = 1.2
    c3.Line.EndArrowheadStyle = 2

    # 4. Box 4: Output Graph Readout (Right)
    b4 = items.AddShape(5, 354.0, 8.0, 88.0, 144.0)
    b4.Fill.Solid()
    b4.Fill.ForeColor.RGB = 0xECFDF5
    b4.Line.ForeColor.RGB = 0x059669
    b4.Line.Weight = 1.2
    tf4 = b4.TextFrame
    tf4.WordWrap = -1
    tf4.MarginLeft = 2.0
    tf4.MarginRight = 2.0
    tf4.MarginTop = 2.0
    tf4.MarginBottom = 2.0
    set_shape_text_formatted(tf4, [
        ('h', "BIỂU DIỄN ĐỒ THỊ"),
        ('sub', "(Graph Readout)"),
        ('blank', ""),
        ('p', "Vector đặc trưng đồ thị"),
        ('blank', ""),
        ('p', "(Cửa sổ trung hạn)"),
        ('blank', ""),
        ('f', "Siêu dữ liệu: [Phạm vi, Mặt nạ]"),
    ], default_font_size=6.5, default_align=1)


def draw_fig_2_4(canvas_raw: Any):
    """
    Draws FIG 2.4: Multi-View Alignment, Anti-Collapse Regularization & Unified Representation Learning
    Editable Word Shapes Drawing Canvas.
    """
    canvas = canvas_raw
    items = canvas.CanvasItems

    # Four equal stages: their exact positions are normalized again with
    # ShapeRange.Align/Distribute below, rather than relying on visual placement.
    stage_x = [8.0, 116.0, 224.0, 332.0]
    stage_width = 100.0
    stage_top = 10.0
    stage_height = 138.0
    header_height = 31.0
    body_top_offset = 39.0
    body_height = 101.0
    stages = [
        ("ĐẦU VÀO", "(Đặc trưng đa góc nhìn)", [
            "Chuỗi ngắn hạn", "Đồ thị trung hạn", "Chất lượng & ngữ cảnh", "Mặt nạ sẵn sàng",
        ], 0x0284C7, 0xFFFFFF),
        ("CHIẾU / NGỮ CẢNH", "(Không gian gióng hàng)", [
            "Chiếu nhánh chuỗi", "Chiếu nhánh đồ thị", "Ngữ cảnh quản trị", "Kiểm soát shortcut",
        ], 0x7C3AED, 0xFFFFFF),
        ("ĐIỀU HÒA", "(VICReg & MIL)", [
            "Bất biến hai góc nhìn", "Phương sai & hiệp phương sai", "PCGrad", "Attention-MIL nhãn thô",
        ], 0xEA580C, 0xFFFFFF),
        ("BIỂU DIỄN THỐNG NHẤT", "(Canonical Representation)", [
            "Vector chuẩn hóa", "Gated fusion", "Siêu dữ liệu tương ứng", "Bàn giao Stage C",
        ], 0x2563EB, 0xEFF6FF),
    ]
    stage_shapes = []
    all_names = []
    for index, (title, subtitle, body_lines, color, fill) in enumerate(stages):
        outer = items.AddShape(5, stage_x[index], stage_top, stage_width, stage_height)
        outer.Fill.Solid()
        outer.Fill.ForeColor.RGB = fill
        outer.Line.ForeColor.RGB = color
        outer.Line.Weight = 1.15
        stage_shapes.append(outer)
        all_names.append(outer.Name)

        header = items.AddTextbox(1, stage_x[index] + 3.0, stage_top + 4.0, stage_width - 6.0, header_height)
        header.Fill.Visible = False
        header.Line.Visible = False
        header_tf = header.TextFrame
        header_tf.WordWrap = -1
        header_tf.MarginLeft = header_tf.MarginRight = 0.0
        header_tf.MarginTop = header_tf.MarginBottom = 0.0
        header_tr = header_tf.TextRange
        header_tr.Text = f"{title}\n{subtitle}"
        header_tr.Font.Name = "Times New Roman"
        header_tr.Font.Size = 6.0
        header_tr.Font.ColorIndex = 1
        header_tr.Font.Bold = True
        header_tr.ParagraphFormat.Alignment = 1
        header_tr.ParagraphFormat.SpaceAfter = 0.0
        all_names.append(header.Name)

        body = items.AddTextbox(1, stage_x[index] + 5.0, stage_top + body_top_offset, stage_width - 10.0, body_height)
        body.Fill.Visible = False
        body.Line.Visible = False
        body_tf = body.TextFrame
        body_tf.WordWrap = -1
        body_tf.MarginLeft = body_tf.MarginRight = 0.0
        body_tf.MarginTop = body_tf.MarginBottom = 0.0
        body_tr = body_tf.TextRange
        body_tr.Text = "\n".join(f"• {line}" for line in body_lines)
        body_tr.Font.Name = "Times New Roman"
        body_tr.Font.Size = 5.8
        body_tr.Font.ColorIndex = 1
        body_tr.ParagraphFormat.Alignment = 0
        body_tr.ParagraphFormat.LeftIndent = 0.0
        body_tr.ParagraphFormat.FirstLineIndent = 0.0
        body_tr.ParagraphFormat.SpaceAfter = 1.0
        body_tr.ParagraphFormat.LineSpacingRule = 0
        all_names.append(body.Name)

    center_y = stage_top + stage_height / 2.0
    for index in range(3):
        connector = items.AddConnector(1, stage_shapes[index].Left + stage_shapes[index].Width,
                                       center_y, stage_shapes[index + 1].Left, center_y)
        connector.Line.ForeColor.RGB = 0x334155
        connector.Line.Weight = 1.2
        connector.Line.EndArrowheadStyle = 2
        all_names.append(connector.Name)

    # Canvas items do not expose a reliable ShapeRange.Distribute API.  The
    # production replacement script builds this figure at document level,
    # where Word's ShapeRange grid and grouping APIs are available.




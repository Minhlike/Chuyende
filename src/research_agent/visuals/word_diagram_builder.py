"""
Công cụ sơ đồ gốc của Word (Quy tắc 1 & Quy tắc 2A)
Trực tiếp xây dựng các sơ đồ khoa học đơn sắc, tối giản, sắc nét bằng cách sử dụng Mô hình đối tượng Microsoft Word 2016 (COM).
Thực thi: Hình chữ nhật/Hình chữ nhật tròn, Mũi tên nối màu đen, Nền màu trắng, Đường viền 1pt màu đen, Times New Roman, Không có bóng/3D.
"""

import os
from typing import Any, Dict, List, Optional

try:
    import win32com.client as win32
    HAS_WIN32COM = True
except ImportError:
    win32 = None
    HAS_WIN32COM = False
from research_agent.visuals.schemas import (
    DiagramSpecification,
    ShapeNodeSpec,
    ConnectorSpec,
    VisualRecord,
    VisualType,
    CreationMethod,
)


class WordDiagramBuilder:
    """
    Hiển thị Sơ đồ Word gốc bằng cách sử dụng Hình dạng, Canvas vẽ và Trình kết nối thông qua Word COM.
    """

    MSO_SHAPE_RECTANGLE = 1
    MSO_SHAPE_ROUNDED_RECTANGLE = 5
    MSO_SHAPE_OVAL = 9
    MSO_SHAPE_DIAMOND = 4

    MSO_CONNECTOR_STRAIGHT = 1
    MSO_CONNECTOR_ELBOW = 2
    MSO_CONNECTOR_CURVE = 3

    MSO_ARROWHEAD_NONE = 1
    MSO_ARROWHEAD_TRIANGLE = 2

    WD_ALIGN_PARAGRAPH_CENTER = 1
    WD_WRAP_INLINE = 7
    WD_WRAP_TOP_BOTTOM = 4

    def __init__(self):
        pass

    def build_diagram_in_docx(
        self,
        doc_com: Any,
        target_range: Any,
        spec: DiagramSpecification,
        caption_seq: int = 1,
        chapter_num: int = 1,
    ) -> Dict[str, Any]:
        """
        Chèn Canvas vẽ gốc chứa các nút và trình kết nối ở phạm vi mục tiêu trong Word COM.
        """
        shapes_dict: Dict[str, Any] = {}
        nodes_dict: Dict[str, ShapeNodeSpec] = {n.shape_id: n for n in spec.nodes}

        # Nếu use_canvas được bật, hãy tạo khung vẽ
        if spec.use_canvas:
            # Thêm Canvas vào tài liệu
            canvas = doc_com.Shapes.AddCanvas(
                Left=10,
                Top=10,
                Width=spec.canvas_width_pt,
                Height=spec.canvas_height_pt,
                Anchor=target_range
            )
            canvas.WrapFormat.Type = self.WD_WRAP_TOP_BOTTOM
            canvas.Line.Visible = False  # Ranh giới canvas vô hình
            canvas.Fill.Visible = False

            # Thêm các nút hình dạng vào Canvas
            for node in spec.nodes:
                shape_type = self._resolve_shape_type(node.shape_type)
                s = canvas.CanvasItems.AddShape(
                    Type=shape_type,
                    Left=node.left_pt,
                    Top=node.top_pt,
                    Width=node.width_pt,
                    Height=node.height_pt,
                )
                self._apply_minimal_shape_style(s, node)
                shapes_dict[node.shape_id] = s

            # Thêm trình kết nối vào Canvas
            for conn in spec.connectors:
                c_type = self.MSO_CONNECTOR_ELBOW if conn.connector_type == "ELBOW" else self.MSO_CONNECTOR_STRAIGHT
                
                src_node = nodes_dict.get(conn.source_shape_id)
                tgt_node = nodes_dict.get(conn.target_shape_id)

                if src_node and tgt_node:
                    x1 = src_node.left_pt + src_node.width_pt
                    y1 = src_node.top_pt + (src_node.height_pt / 2.0)
                    x2 = tgt_node.left_pt
                    y2 = tgt_node.top_pt + (tgt_node.height_pt / 2.0)
                else:
                    x1, y1, x2, y2 = 10, 10, 100, 100

                c = canvas.CanvasItems.AddConnector(
                    Type=c_type,
                    BeginX=x1,
                    BeginY=y1,
                    EndX=x2,
                    EndY=y2
                )
                self._apply_minimal_connector_style(c, conn)

                # Thử kết nối neo động
                src_shape = shapes_dict.get(conn.source_shape_id)
                tgt_shape = shapes_dict.get(conn.target_shape_id)
                if src_shape and tgt_shape:
                    try:
                        c.ConnectorFormat.BeginConnect(src_shape, int(conn.start_connection_site))
                        c.ConnectorFormat.EndConnect(tgt_shape, int(conn.end_connection_site))
                        c.RerouteConnections()
                    except Exception:
                        pass

            # Nhóm tùy chọn
            if spec.group_shapes and len(shapes_dict) > 1:
                try:
                    shape_names = [s.Name for s in shapes_dict.values()]
                    canvas.CanvasItems.Range(shape_names).Group()
                except Exception:
                    pass

            return {"canvas": canvas, "shapes": shapes_dict, "success": True}

        else:
            # Hình dạng trực tiếp trên tài liệu
            for node in spec.nodes:
                shape_type = self._resolve_shape_type(node.shape_type)
                s = doc_com.Shapes.AddShape(
                    Type=shape_type,
                    Left=node.left_pt,
                    Top=node.top_pt,
                    Width=node.width_pt,
                    Height=node.height_pt,
                    Anchor=target_range
                )
                self._apply_minimal_shape_style(s, node)
                shapes_dict[node.shape_id] = s

            return {"shapes": shapes_dict, "success": True}

    def _resolve_shape_type(self, type_str: str) -> int:
        type_str = type_str.upper()
        if "ROUND" in type_str:
            return self.MSO_SHAPE_ROUNDED_RECTANGLE
        elif "OVAL" in type_str or "CIRCLE" in type_str:
            return self.MSO_SHAPE_OVAL
        elif "DIAMOND" in type_str or "DECISION" in type_str:
            return self.MSO_SHAPE_DIAMOND
        return self.MSO_SHAPE_RECTANGLE

    def _apply_minimal_shape_style(self, shape: Any, node: ShapeNodeSpec):
        """Áp dụng phong cách học thuật đơn sắc nghiêm ngặt (không có gradient, bóng, 3D)."""        # Điền: Trắng
        shape.Fill.Solid()
        shape.Fill.ForeColor.RGB = 0xFFFFFF  # trắng
        shape.Fill.Transparency = 0.0

        # Dòng: Đen 1pt
        shape.Line.Visible = True
        shape.Line.ForeColor.RGB = 0x000000  # Đen
        shape.Line.Weight = node.line_weight_pt

        # Tắt bóng và 3D
        try:
            shape.Shadow.Visible = False
        except Exception:
            pass
        try:
            shape.ThreeD.Visible = False
        except Exception:
            pass

        # văn bản
        tf = shape.TextFrame
        tf.WordWrap = True
        tf.MarginLeft = 4.0
        tf.MarginRight = 4.0
        tf.MarginTop = 4.0
        tf.MarginBottom = 4.0

        full_text = node.label
        if node.sub_label:
            full_text += "\n" + node.sub_label

        tr = tf.TextRange
        tr.Text = full_text
        tr.Font.Name = "Times New Roman"
        tr.Font.Size = node.font_size_pt
        try:
            tr.Font.ColorIndex = 1  # wdĐen
        except Exception:
            pass
        tr.Font.Bold = node.is_bold
        tr.ParagraphFormat.Alignment = self.WD_ALIGN_PARAGRAPH_CENTER
        tr.ParagraphFormat.SpaceBefore = 0
        tr.ParagraphFormat.SpaceAfter = 0
        tr.ParagraphFormat.LineSpacingRule = 0  # Độc thân

    def _apply_minimal_connector_style(self, connector: Any, conn_spec: ConnectorSpec):
        """Áp dụng kiểu mũi tên màu đen rõ nét cho đầu nối."""
        connector.Line.Visible = True
        connector.Line.ForeColor.RGB = 0x000000
        connector.Line.Weight = conn_spec.line_weight_pt

        if conn_spec.arrow_head:
            connector.Line.EndArrowheadStyle = self.MSO_ARROWHEAD_TRIANGLE
            connector.Line.EndArrowheadLength = 2
            connector.Line.EndArrowheadWidth = 2
        else:
            connector.Line.EndArrowheadStyle = self.MSO_ARROWHEAD_NONE

        try:
            connector.Shadow.Visible = False
        except Exception:
            pass

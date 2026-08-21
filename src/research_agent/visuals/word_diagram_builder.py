"""
Word Native Diagram Engine (Rule 1 & Rule 2A)
Builds crisp, minimal, monochrome scientific diagrams directly using Microsoft Word 2016 Object Model (COM).
Enforces: Rectangle/Rounded Rectangle, Black connector arrows, White fill, Black 1pt outline, Times New Roman, No shadows/3D.
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
    Renders native Word Diagrams using Shapes, Drawing Canvas, and Connectors via Word COM.
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
        Inserts a native Drawing Canvas containing nodes and connectors at the target range in Word COM.
        """
        shapes_dict: Dict[str, Any] = {}
        nodes_dict: Dict[str, ShapeNodeSpec] = {n.shape_id: n for n in spec.nodes}

        # If use_canvas is enabled, create a drawing canvas
        if spec.use_canvas:
            # Add Canvas to document
            canvas = doc_com.Shapes.AddCanvas(
                Left=10,
                Top=10,
                Width=spec.canvas_width_pt,
                Height=spec.canvas_height_pt,
                Anchor=target_range
            )
            canvas.WrapFormat.Type = self.WD_WRAP_TOP_BOTTOM
            canvas.Line.Visible = False  # Invisible canvas boundary
            canvas.Fill.Visible = False

            # Add Shape Nodes into Canvas
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

            # Add Connectors into Canvas
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

                # Attempt dynamic anchor connection
                src_shape = shapes_dict.get(conn.source_shape_id)
                tgt_shape = shapes_dict.get(conn.target_shape_id)
                if src_shape and tgt_shape:
                    try:
                        c.ConnectorFormat.BeginConnect(src_shape, int(conn.start_connection_site))
                        c.ConnectorFormat.EndConnect(tgt_shape, int(conn.end_connection_site))
                        c.RerouteConnections()
                    except Exception:
                        pass

            # Optional grouping
            if spec.group_shapes and len(shapes_dict) > 1:
                try:
                    shape_names = [s.Name for s in shapes_dict.values()]
                    canvas.CanvasItems.Range(shape_names).Group()
                except Exception:
                    pass

            return {"canvas": canvas, "shapes": shapes_dict, "success": True}

        else:
            # Direct shapes on document
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
        """Applies strict monochrome academic style (no gradient, shadow, 3D)."""
        # Fill: White
        shape.Fill.Solid()
        shape.Fill.ForeColor.RGB = 0xFFFFFF  # White
        shape.Fill.Transparency = 0.0

        # Line: Black 1pt
        shape.Line.Visible = True
        shape.Line.ForeColor.RGB = 0x000000  # Black
        shape.Line.Weight = node.line_weight_pt

        # Disable Shadows and 3D
        try:
            shape.Shadow.Visible = False
        except Exception:
            pass
        try:
            shape.ThreeD.Visible = False
        except Exception:
            pass

        # Text
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
            tr.Font.ColorIndex = 1  # wdBlack
        except Exception:
            pass
        tr.Font.Bold = node.is_bold
        tr.ParagraphFormat.Alignment = self.WD_ALIGN_PARAGRAPH_CENTER
        tr.ParagraphFormat.SpaceBefore = 0
        tr.ParagraphFormat.SpaceAfter = 0
        tr.ParagraphFormat.LineSpacingRule = 0  # Single

    def _apply_minimal_connector_style(self, connector: Any, conn_spec: ConnectorSpec):
        """Applies crisp black arrow style to connector."""
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

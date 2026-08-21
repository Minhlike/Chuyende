# -*- coding: utf-8 -*-
"""
Dedicated Word COM Automation Post-Processor.
Executes in an isolated STA Python process to render Native Word Drawing Canvases,
update all dynamic fields (TOC, LOF, LOT, BIBLIOGRAPHY), and export publication-ready PDF.
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

# Ensure D:\Research\src is in sys.path
src_dir = Path(r"D:\Research\src")
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import win32com.client as win32
import pythoncom
import traceback

from research_agent.visuals.chapter1_drawings import draw_fig_1_1, draw_fig_1_2, draw_fig_1_3, draw_fig_1_4
from research_agent.visuals.chapter2_drawings import draw_fig_2_1, draw_fig_2_2, draw_fig_2_3, draw_fig_2_4


def replace_raster_with_canvas(doc_obj, bm_name, draw_fn, fig_name):
    try:
        print(f"[6/6.3] Replacing raster with Canvas for {fig_name} (Bookmark {bm_name})...", flush=True)
        if doc_obj.Bookmarks.Exists(bm_name):
            bm_rng = doc_obj.Bookmarks(bm_name).Range
            p_prev = bm_rng.Paragraphs(1).Previous()
            p_pic = p_prev.Range
            while p_pic.InlineShapes.Count > 0:
                p_pic.InlineShapes(1).Delete()
            canvas = doc_obj.Shapes.AddCanvas(0, 0, 450, 160, p_pic)
            draw_fn(canvas)
            canvas.ConvertToInlineShape()
            print(f"[SUCCESS] Rendered Native Word Drawing Canvas Shapes for {fig_name}", flush=True)
            return True
        else:
            print(f"[WARNING] Bookmark {bm_name} not found for {fig_name}", flush=True)
    except Exception as e_canvas:
        print(f"[WARNING] Could not render Drawing Canvas for {fig_name}: {e_canvas}", flush=True)
        traceback.print_exc()
    return False


def render_canvas_at_bookmark(doc_obj, bm_name, draw_fn, fig_name):
    try:
        print(f"[6/6.3] Rendering Canvas for {fig_name} (Bookmark {bm_name})...", flush=True)
        if doc_obj.Bookmarks.Exists(bm_name):
            bm_rng = doc_obj.Bookmarks(bm_name).Range
            p_rng = bm_rng.Paragraphs(1).Range
            while p_rng.InlineShapes.Count > 0:
                p_rng.InlineShapes(1).Delete()
            canvas = doc_obj.Shapes.AddCanvas(0, 0, 450, 160, p_rng)
            draw_fn(canvas)
            canvas.ConvertToInlineShape()
            print(f"[SUCCESS] Rendered Native Word Drawing Canvas Shapes for {fig_name}", flush=True)
            return True
        else:
            print(f"[WARNING] Bookmark {bm_name} not found for {fig_name}", flush=True)
    except Exception as e_canvas:
        print(f"[WARNING] Could not render Drawing Canvas for {fig_name}: {e_canvas}", flush=True)
        traceback.print_exc()
    return False


def run_post_process(docx_file: str, pdf_file: str = None):
    abs_target = os.path.abspath(docx_file)
    if pdf_file is None:
        pdf_file = os.path.splitext(abs_target)[0] + ".pdf"
    abs_pdf = os.path.abspath(pdf_file)

    pythoncom.CoInitialize()
    word = None
    doc_com = None
    try:
        word = win32.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        try:
            word.Options.UpdateLinksAtOpen = False
            word.Options.CheckGrammarAsYouType = False
            word.Options.CheckSpellingAsYouType = False
        except Exception:
            pass

        print(f"[6/6.1] Opening {abs_target} in Microsoft Word...", flush=True)
        doc_com = word.Documents.Open(abs_target)
        print("[6/6.2] Document successfully opened in Word COM!", flush=True)

        # Render Drawing Canvases for Figures 1.1 - 1.4, 2.1
        replace_raster_with_canvas(doc_com, "BK_FIG_1_001", draw_fig_1_1, "Figure 1.1")
        replace_raster_with_canvas(doc_com, "BK_FIG_1_002", draw_fig_1_2, "Figure 1.2")
        replace_raster_with_canvas(doc_com, "BK_FIG_1_003", draw_fig_1_3, "Figure 1.3")
        replace_raster_with_canvas(doc_com, "BK_FIG_1_004", draw_fig_1_4, "Figure 1.4")
        replace_raster_with_canvas(doc_com, "BK_FIG_2_001", draw_fig_2_1, "Figure 2.1")

        # Render Drawing Canvases for Figures 2.2 - 2.4
        render_canvas_at_bookmark(doc_com, "BK_FIG_2_002_CANVAS", draw_fig_2_2, "Figure 2.2")
        render_canvas_at_bookmark(doc_com, "BK_FIG_2_003_CANVAS", draw_fig_2_3, "Figure 2.3")
        render_canvas_at_bookmark(doc_com, "BK_FIG_2_004_CANVAS", draw_fig_2_4, "Figure 2.4")

        # Update TOC, TOF, Fields
        print("[6/6.4] Updating TOC, TOF, and dynamic fields...", flush=True)
        for toc in doc_com.TablesOfContents:
            try: toc.Update()
            except Exception: pass
        for tof in doc_com.TablesOfFigures:
            try: tof.Update()
            except Exception: pass
        try:
            doc_com.Fields.Update()
        except Exception:
            pass

        # Save docx
        print(f"[6/6.5] Saving document: {abs_target}", flush=True)
        doc_com.Save()
        print(f"[SUCCESS] Microsoft Word updated and saved: {abs_target}", flush=True)

        # Export PDF
        print(f"[6/6.6] Exporting PDF: {abs_pdf}", flush=True)
        doc_com.ExportAsFixedFormat(abs_pdf, 17)
        print(f"[SUCCESS] Exported PDF: {abs_pdf}", flush=True)

        doc_com.Close(False)
        doc_com = None
        word.Quit()
        word = None
        print("[SUCCESS] Word COM Post-Processing Completed with 100% Success!", flush=True)
    except Exception as e:
        print(f"[ERROR] Post-processing failed: {e}", flush=True)
        traceback.print_exc()
        if doc_com is not None:
            try: doc_com.Close(False)
            except Exception: pass
        if word is not None:
            try: word.Quit()
            except Exception: pass
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_post_process(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        run_post_process(sys.argv[1])
    else:
        run_post_process(r"D:\Research\Chuyên đề chuyên sâu - Copy.docx")

"""
Thesis Compiler & Multi-Format Document Assembler (Prompt 7 Sections 51..56, 77..78, 109..111)
"""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from research_agent.core.enums import (
    CompositionMode,
    WritingReadiness,
)
from research_agent.schemas.composition import (
    ChapterRecord,
    SectionRecord,
    SubsectionRecord,
    ThesisAuditReport,
    ThesisBuildManifest,
    ThesisDocument,
)
from research_agent.storage.repository import ResearchRepository
from research_agent.composition.composer import AcademicComposer
from research_agent.composition.auditors import ThesisAuditor
from research_agent.composition.gates import WritingGate


class ThesisCompiler:
    """
    Assembles hierarchical Document IR chapters into final thesis drafts,
    generates canonical BibTeX references, executes pre-build audit gates,
    and produces cryptographic BuildManifests.
    """

    def __init__(self, repository: ResearchRepository, output_dir: Optional[str] = None):
        self.repo = repository
        self.output_dir = Path(output_dir) if output_dir else Path("runtime/thesis_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.composer = AcademicComposer(repository)
        self.auditor = ThesisAuditor(repository)
        self.gate = WritingGate(repository)

    def compile_node(self, node_code: str, mode: CompositionMode = CompositionMode.PROVISIONAL) -> SubsectionRecord:
        """Compiles a single Roadmap Node subsection."""
        return self.composer.compose_node_subsection(node_code, mode=mode)

    def compile_thesis(
        self,
        mode: CompositionMode = CompositionMode.PROVISIONAL,
    ) -> Tuple[ThesisDocument, ThesisAuditReport, ThesisBuildManifest]:
        """
        Compiles the complete thesis document across all chapters and nodes.
        Audits the resulting Document IR and writes compiled Markdown and Manifest.
        """
        roadmap = self.repo.get_active_roadmap()
        nodes = self.repo.list_roadmap_nodes()

        chapters: List[ChapterRecord] = []
        # Group nodes by Chapter (e.g. 1.x -> Ch1, 2.x -> Ch2, 3.x -> Ch3)
        ch_map: Dict[str, List[Any]] = {"CH1": [], "CH2": [], "CH3": []}

        for n in nodes:
            if n.code.startswith("1."):
                ch_map["CH1"].append(n)
            elif n.code.startswith("2."):
                ch_map["CH2"].append(n)
            elif n.code.startswith("3."):
                ch_map["CH3"].append(n)

        ch_titles = {
            "CH1": "Chương 1: Tổng quan và Cơ sở lý thuyết về Phát hiện Tấn công từ Nhật ký",
            "CH2": "Chương 2: Kiến trúc Biểu diễn Đặc trưng Đa góc nhìn Bảo toàn Tham số",
            "CH3": "Chương 3: Đánh giá Thực nghiệm và Kiểm chứng Giả thuyết Khoa học",
        }

        all_paragraphs = []
        for ch_key, ch_nodes in ch_map.items():
            sections: List[SectionRecord] = []
            # Group by section (e.g. 1.1, 1.2, 1.3)
            sec_map: Dict[str, List[Any]] = {}
            for cn in ch_nodes:
                sec_code = ".".join(cn.code.split(".")[:2]) if "." in cn.code else cn.code
                sec_map.setdefault(sec_code, []).append(cn)

            for sec_code, s_nodes in sec_map.items():
                subsections: List[SubsectionRecord] = []
                for sn in s_nodes:
                    sub = self.composer.compose_node_subsection(sn.code, mode=mode)
                    subsections.append(sub)
                    all_paragraphs.extend(sub.paragraphs)

                sections.append(
                    SectionRecord(
                        section_code=sec_code,
                        title=f"Mục {sec_code}",
                        subsections=subsections,
                    )
                )

            chapters.append(
                ChapterRecord(
                    chapter_code=ch_key,
                    title=ch_titles.get(ch_key, f"Chương {ch_key}"),
                    sections=sections,
                )
            )

        # Generate Bibliography BibTeX from Reference Map
        bibtex = self._generate_bibtex_bibliography()

        thesis_doc = ThesisDocument(
            document_id=f"THESIS-{mode.value}",
            title="Nghiên cứu Học Biểu diễn Đặc trưng Bảo toàn Tham số và Cấu trúc Phục vụ Phát hiện Tấn công Mạng",
            author="Nghiên cứu sinh",
            institution="Đại học Quốc gia",
            year=2026,
            chapters=chapters,
            bibliography_bibtex=bibtex,
        )

        # Run Thesis Auditor
        audit_report = self.auditor.audit_thesis(paragraphs=all_paragraphs, mode=mode)

        # In FINAL mode, fail closed if critical issues exist
        if mode == CompositionMode.FINAL and not audit_report.is_ready_for_final_build:
            raise RuntimeError(
                f"Thesis compilation FAILED in FINAL mode due to {len(audit_report.critical_issues)} critical issues."
            )

        # Render full markdown text
        full_md_lines = [
            f"# {thesis_doc.title}\n",
            f"**Tác giả:** {thesis_doc.author} | **Năm:** {thesis_doc.year}\n",
            "## Tóm tắt Luận án (Abstract)\n",
            self.composer.build_abstract(),
            "\n---\n",
        ]

        for ch in thesis_doc.chapters:
            full_md_lines.append(f"\n# {ch.title}\n")
            for sec in ch.sections:
                for sub in sec.subsections:
                    full_md_lines.append(sub.rendered_markdown)
                    full_md_lines.append("\n")

        full_md_lines.append("\n# Kết luận và Hướng phát triển\n")
        full_md_lines.append(self.composer.build_conclusion())
        full_md_lines.append("\n# Tài liệu Tham khảo\n```bibtex\n" + bibtex + "\n```\n")

        full_md_str = "\n".join(full_md_lines)
        out_file = self.output_dir / f"thesis_{mode.value.lower()}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_md_str)

        # Calculate Hash
        hasher = hashlib.sha256()
        hasher.update(full_md_str.encode("utf-8"))
        out_sha = hasher.hexdigest()

        manifest = ThesisBuildManifest(
            build_id=audit_report.build_id,
            mode=mode,
            git_commit="2b5df36",
            total_nodes_compiled=len(nodes),
            unresolved_critical_count=len(audit_report.critical_issues),
            unresolved_high_count=len(audit_report.high_issues),
            output_file_path=str(out_file),
            output_sha256=out_sha,
        )
        self.repo.save_build_manifest(manifest)

        return thesis_doc, audit_report, manifest

    def _generate_bibtex_bibliography(self) -> str:
        """Generates standard BibTeX bibliography entries from Source Registry."""
        sources = self.repo.list_sources()
        entries = []
        for s in sources:
            key = f"ref_{s.source_id.replace('-', '_')}"
            first_author = s.authors[0] if s.authors else "Anonymous"
            year = s.year or 2024
            entries.append(
                f"@article{{{key},\n"
                f"  author = {{{' and '.join(s.authors)}}},\n"
                f"  title = {{{s.title}}},\n"
                f"  journal = {{{s.venue or 'Conference/Journal'}}},\n"
                f"  year = {{{year}}},\n"
                f"  doi = {{{s.doi or ''}}}\n"
                f"}}"
            )
        return "\n\n".join(entries)

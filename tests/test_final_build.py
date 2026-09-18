"""
Bài kiểm tra đơn vị & tích hợp để biên soạn luận văn cuối cùng và xây dựng bao bì (Nhắc 7)
"""

import pytest
from pathlib import Path
from research_agent.core.enums import CompositionMode
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.composition.compiler import ThesisCompiler
from research_agent.composition.packaging import ResearchArtifactPackager


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_build.db"
    db = DatabaseManager(f"sqlite:///{db_file}")
    db.init_schema()
    return db


@pytest.fixture
def repo(test_db):
    return ResearchRepository(test_db)


@pytest.fixture
def compiler(repo, tmp_path):
    out_dir = tmp_path / "thesis_output"
    return ThesisCompiler(repository=repo, output_dir=str(out_dir))


@pytest.fixture
def packager(repo):
    return ResearchArtifactPackager(repo)


def test_final_01_provisional_build_produces_artifacts(compiler):
    """Bản dựng luận án tạm thời tạo ra Tài liệu IR, đầu ra đánh dấu và bản kê (manifest) bản dựng."""
    doc, report, manifest = compiler.compile_thesis(mode=CompositionMode.PROVISIONAL)
    assert doc is not None
    assert manifest is not None
    assert Path(manifest.output_file_path).exists()
    assert manifest.output_sha256 is not None
    assert len(manifest.output_sha256) == 64
    assert len(doc.chapters) >= 1


def test_final_02_packager_generates_complete_manifest(packager):
    """Trình đóng gói tạo phẩm (artifact) tạo tệp kê khai gói với hàm băm tính toàn vẹn SHA-256."""
    pkg = packager.build_package_manifest()
    assert pkg.package_id.startswith("PKG-")
    assert pkg.package_sha256 is not None
    assert len(pkg.package_sha256) == 64
    assert pkg.roadmap_file == "data/canonical/canonical_roadmap.json"

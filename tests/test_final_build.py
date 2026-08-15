"""
Unit & Integration Tests for Final Thesis Compilation & Build Packaging (Prompt 7)
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
    """Provisional thesis build produces Document IR, markdown output, and build manifest."""
    doc, report, manifest = compiler.compile_thesis(mode=CompositionMode.PROVISIONAL)
    assert doc is not None
    assert manifest is not None
    assert Path(manifest.output_file_path).exists()
    assert manifest.output_sha256 is not None
    assert len(manifest.output_sha256) == 64
    assert len(doc.chapters) >= 1


def test_final_02_packager_generates_complete_manifest(packager):
    """Artifact packager creates package manifest with SHA-256 integrity hash."""
    pkg = packager.build_package_manifest()
    assert pkg.package_id.startswith("PKG-")
    assert pkg.package_sha256 is not None
    assert len(pkg.package_sha256) == 64
    assert pkg.roadmap_file == "data/canonical/canonical_roadmap.json"

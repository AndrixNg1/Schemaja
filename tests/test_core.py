"""Valide le scan de dossiers et l'extraction de métadonnées de police,
sur les polices factices générées par generate_samples.py."""
import shutil
import zipfile

import pytest

from core.font_metadata import InvalidFontError, read_font_info
from core.scanner import cleanup_extracted_dirs, scan
from tests.generate_samples import SAMPLES_DIR, build_font, generate_all


@pytest.fixture(scope="module", autouse=True)
def samples():
    generate_all()
    yield
    shutil.rmtree(SAMPLES_DIR, ignore_errors=True)


def test_scan_finds_only_supported_extensions_recursively():
    found = list(scan(SAMPLES_DIR, recursive=True))
    names = {p.name for p in found}
    assert "TestSans-Regular.ttf" in names
    assert "TestSerif-Regular.ttf" in names  # dans sous_dossier/
    assert "pas_une_police.ttf" in names  # scan ne valide pas le contenu


def test_scan_non_recursive_ignores_subfolders():
    found = list(scan(SAMPLES_DIR, recursive=False))
    names = {p.name for p in found}
    assert "TestSerif-Regular.ttf" not in names


def test_scan_single_file():
    target = SAMPLES_DIR / "TestSans-Regular.ttf"
    found = list(scan(target))
    assert found == [target]


def test_scan_rejects_unsupported_extension(tmp_path):
    (tmp_path / "notes.txt").write_text("bonjour")
    assert list(scan(tmp_path)) == []


def test_read_font_info_extracts_real_family_name_not_filename():
    info = read_font_info(SAMPLES_DIR / "TestSans-Regular.ttf")
    assert info.family == "ZZTestSans Vektor"
    assert info.subfamily == "Regular"
    assert info.full_name == "ZZTestSans Vektor Regular"
    assert info.is_truetype is True


def test_registry_name_suffix_reflects_truetype():
    info = read_font_info(SAMPLES_DIR / "TestSans-Regular.ttf")
    assert info.registry_name == "ZZTestSans Vektor Regular (TrueType)"


def test_two_different_files_same_family_have_same_registry_name():
    a = read_font_info(SAMPLES_DIR / "TestSans-Regular.ttf")
    b = read_font_info(SAMPLES_DIR / "TestSans-Duplicate.ttf")
    assert a.path != b.path
    assert a.registry_name == b.registry_name  # base du dédoublonnage


def test_invalid_font_file_raises():
    with pytest.raises(InvalidFontError):
        read_font_info(SAMPLES_DIR / "pas_une_police.ttf")


def test_scan_extracts_font_from_zip(tmp_path):
    font_path = tmp_path / "_build" / "Polices" / "TestZip-Regular.ttf"
    build_font(font_path, "ZZTestZip Vektor", "Regular")
    zip_path = tmp_path / "pack.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(font_path, arcname="Polices/TestZip-Regular.ttf")

    extracted_dirs = []
    found = list(scan(zip_path, extracted_dirs=extracted_dirs))

    assert len(found) == 1
    assert found[0].name == "TestZip-Regular.ttf"
    assert len(extracted_dirs) == 1
    assert extracted_dirs[0].exists()

    cleanup_extracted_dirs(extracted_dirs)
    assert extracted_dirs == []


def test_scan_finds_zip_inside_a_folder(tmp_path):
    font_path = tmp_path / "_build" / "TestZip2-Regular.ttf"
    build_font(font_path, "ZZTestZip2 Vektor", "Regular")
    pack_dir = tmp_path / "pack_dir"
    pack_dir.mkdir()
    with zipfile.ZipFile(pack_dir / "pack.zip", "w") as zf:
        zf.write(font_path, arcname="TestZip2-Regular.ttf")
    (pack_dir / "readme.txt").write_text("pas une police")

    extracted_dirs = []
    found = list(scan(pack_dir, extracted_dirs=extracted_dirs))

    assert [p.name for p in found] == ["TestZip2-Regular.ttf"]
    cleanup_extracted_dirs(extracted_dirs)


def test_scan_ignores_corrupt_zip(tmp_path):
    (tmp_path / "corrompu.zip").write_bytes(b"pas un vrai zip")

    extracted_dirs = []
    found = list(scan(tmp_path, extracted_dirs=extracted_dirs))

    assert found == []
    cleanup_extracted_dirs(extracted_dirs)


def test_scan_ignores_zip_slip_entries(tmp_path):
    """Une entrée d'archive qui tente de sortir du dossier d'extraction
    (../../evil.ttf) doit être ignorée, jamais extraite sur le disque."""
    font_path = tmp_path / "_build" / "evil.ttf"
    build_font(font_path, "ZZEvil Vektor", "Regular")
    zip_path = tmp_path / "evil.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(font_path, arcname="../../evil_escaped.ttf")

    extracted_dirs = []
    found = list(scan(zip_path, extracted_dirs=extracted_dirs))

    assert found == []
    cleanup_extracted_dirs(extracted_dirs)

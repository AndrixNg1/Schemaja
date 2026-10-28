"""Recherche des fichiers de police dans un fichier, un dossier, ou une
archive .zip (extraite dans un dossier temporaire puis scannée pareil)."""
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterator, List, Optional

# .woff/.woff2 volontairement exclus : Windows ne sait pas les installer
# nativement via AddFontResource + registre, contrairement à .ttf/.otf.
SUPPORTED_EXTENSIONS = {".ttf", ".otf"}
ARCHIVE_EXTENSIONS = {".zip"}


def scan(
    source: Path,
    recursive: bool = True,
    extracted_dirs: Optional[List[Path]] = None,
) -> Iterator[Path]:
    """Retourne les chemins des polices trouvées, triés par nom.

    Les fichiers .zip rencontrés sont extraits dans un dossier temporaire
    et leur contenu est scanné à son tour (toujours récursivement, quel
    que soit `recursive`). Si `extracted_dirs` est fourni, chaque dossier
    temporaire créé y est ajouté ; l'appelant est responsable de les
    supprimer via `cleanup_extracted_dirs()` une fois l'installation
    terminée.
    """
    source = Path(source)

    if source.is_file():
        yield from _scan_file(source, extracted_dirs)
        return

    pattern = "**/*" if recursive else "*"
    for p in sorted(source.glob(pattern)):
        if p.is_file():
            yield from _scan_file(p, extracted_dirs)


def _scan_file(path: Path, extracted_dirs: Optional[List[Path]]) -> Iterator[Path]:
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_EXTENSIONS:
        yield path
    elif suffix in ARCHIVE_EXTENSIONS:
        yield from _extract_zip(path, extracted_dirs)


def _extract_zip(zip_path: Path, extracted_dirs: Optional[List[Path]]) -> Iterator[Path]:
    extract_dir = Path(tempfile.mkdtemp(prefix="schemaja_zip_"))
    if extracted_dirs is not None:
        extracted_dirs.append(extract_dir)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            _safe_extract_all(zf, extract_dir)
    except zipfile.BadZipFile:
        return

    yield from scan(extract_dir, recursive=True, extracted_dirs=extracted_dirs)


def _safe_extract_all(zf: zipfile.ZipFile, dest: Path) -> None:
    """Extrait en ignorant les entrées qui sortiraient de `dest` (zip
    slip / chemins malveillants) — une archive de polices téléchargée
    reste une entrée non fiable."""
    dest = dest.resolve()
    for member in zf.infolist():
        target = (dest / member.filename).resolve()
        if target.is_relative_to(dest):
            zf.extract(member, dest)


def cleanup_extracted_dirs(extracted_dirs: List[Path]) -> None:
    """Supprime les dossiers temporaires créés pour extraire des .zip."""
    for d in extracted_dirs:
        shutil.rmtree(d, ignore_errors=True)
    extracted_dirs.clear()

"""Lecture des métadonnées d'un fichier de police (.ttf / .otf).

On ne se fie jamais au nom de fichier : le nom de famille réel est lu
dans la table 'name' du fichier, comme Windows le fait lui-même.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fontTools.ttLib import TTFont


class InvalidFontError(Exception):
    """Levée quand le fichier n'est pas une police .ttf/.otf valide ou est corrompu."""


@dataclass
class FontInfo:
    path: Path
    family: str
    subfamily: str
    full_name: str
    is_truetype: bool  # False => police OpenType/CFF (.otf classique)

    @property
    def registry_name(self) -> str:
        """Nom exact attendu par le registre Windows pour cette police."""
        suffix = "(TrueType)" if self.is_truetype else "(OpenType)"
        return f"{self.full_name} {suffix}"


def _get_name(name_table, name_id: int) -> Optional[str]:
    """Cherche un enregistrement de nom, priorité Windows/anglais puis Mac, puis n'importe lequel."""
    record = name_table.getName(name_id, 3, 1, 0x409)
    if record is None:
        record = name_table.getName(name_id, 1, 0, 0)
    if record is None:
        for rec in name_table.names:
            if rec.nameID == name_id:
                record = rec
                break
    return record.toUnicode() if record else None


def read_font_info(path: Path) -> FontInfo:
    """Ouvre le fichier et en extrait famille, style et nom complet réels."""
    try:
        font = TTFont(str(path), lazy=True, fontNumber=0)
    except Exception as e:
        raise InvalidFontError(f"{path.name} n'est pas une police valide : {e}") from e

    try:
        try:
            name_table = font["name"]
        except KeyError as e:
            raise InvalidFontError(f"{path.name} n'a pas de table de noms") from e

        family = _get_name(name_table, 16) or _get_name(name_table, 1) or path.stem
        subfamily = _get_name(name_table, 17) or _get_name(name_table, 2) or ""
        full_name = _get_name(name_table, 4) or f"{family} {subfamily}".strip()
        is_truetype = "glyf" in font
    finally:
        font.close()

    return FontInfo(
        path=path,
        family=family,
        subfamily=subfamily,
        full_name=full_name,
        is_truetype=is_truetype,
    )

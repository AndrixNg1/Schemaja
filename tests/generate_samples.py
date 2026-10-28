"""Génère des polices .ttf factices pour les tests (aucune vraie police
n'est nécessaire au développement/test)."""
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

SAMPLES_DIR = Path(__file__).parent / "samples"


def build_font(path: Path, family: str, subfamily: str) -> None:
    fb = FontBuilder(1000, isTTF=True)
    glyph_order = [".notdef", "A", "B"]
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({65: "A", 66: "B"})

    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((0, 500))
    pen.lineTo((500, 500))
    pen.lineTo((500, 0))
    pen.closePath()
    glyph = pen.glyph()
    empty_glyph = TTGlyphPen(None).glyph()

    fb.setupGlyf({".notdef": empty_glyph, "A": glyph, "B": glyph})
    fb.setupHorizontalMetrics({name: (600, 0) for name in glyph_order})
    fb.setupHorizontalHeader(ascent=800, descent=-200)

    full_name = f"{family} {subfamily}".strip()
    fb.setupNameTable(dict(
        familyName=family,
        styleName=subfamily,
        uniqueFontIdentifier=f"{full_name}-test",
        fullName=full_name,
        psName=full_name.replace(" ", ""),
        version="Version 1.0",
    ))
    fb.setupOS2()
    fb.setupPost()

    path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(path))


def generate_all(out_dir: Path = SAMPLES_DIR) -> None:
    build_font(out_dir / "TestSans-Regular.ttf", "ZZTestSans Vektor", "Regular")
    build_font(out_dir / "TestSans-Bold.ttf", "ZZTestSans Vektor", "Bold")
    build_font(out_dir / "sous_dossier" / "TestSerif-Regular.ttf", "ZZTestSerif Vektor", "Regular")
    build_font(out_dir / "TestSans-Duplicate.ttf", "ZZTestSans Vektor", "Regular")
    (out_dir / "pas_une_police.ttf").write_bytes(b"ceci n'est pas une police")


if __name__ == "__main__":
    generate_all()
    print(f"Polices de test générées dans {SAMPLES_DIR.resolve()}")

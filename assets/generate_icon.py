"""Génère assets/icon.ico (plusieurs résolutions) pour la fenêtre et l'exe.
À relancer si le design de l'icône doit changer — le résultat est commité,
ce script n'a pas besoin de tourner à chaque build."""
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImageWriter,
    QLinearGradient,
    QPainter,
    QPixmap,
)

OUT_PATH = Path(__file__).parent / "icon.ico"
SIZE = 256


def render(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QLinearGradient(0, 0, 0, size)
    gradient.setColorAt(0, QColor("#4F7CFF"))
    gradient.setColorAt(1, QColor("#2E4FCC"))
    radius = size * 0.22
    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRect(0, 0, size, size), radius, radius)

    font = QFont("Georgia")
    font.setPixelSize(int(size * 0.56))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "Aa")

    painter.end()
    return pixmap


def main() -> None:
    app = QGuiApplication([])

    image = render(SIZE).toImage()
    writer = QImageWriter(str(OUT_PATH), b"ico")
    if not writer.write(image):
        raise SystemExit(f"Échec de la sauvegarde de l'icône : {writer.errorString()}")

    print(f"Icône générée : {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()

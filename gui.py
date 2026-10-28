"""Schémaja — installeur de polices en masse pour Windows (version graphique, PySide6).

Usage :
    python gui.py
"""
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

ICON_PATH = Path(__file__).parent / "assets" / "icon.ico"


def main() -> None:
    # sys.stdout est None en build PyInstaller --windowed (pas de console).
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8")

    if sys.platform != "win32":
        print("Cet outil ne fonctionne que sous Windows.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""Exécute lecture des métadonnées + installation en arrière-plan, pour ne
pas geler l'UI le temps de traiter un gros pack de polices."""
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from core.font_installer import Scope, install_font, notify_system
from core.font_metadata import InvalidFontError, read_font_info
from core.models import InstallStatus


class InstallWorker(QThread):
    item_done = Signal(int, str, str)  # index, nom de police (ou fichier), statut
    finished_all = Signal(int, int, int)  # installées, déjà là, échouées

    def __init__(self, paths: list[Path], scope: Scope, force: bool, parent=None):
        super().__init__(parent)
        self.paths = paths
        self.scope = scope
        self.force = force

    def run(self) -> None:
        installed = skipped = failed = 0

        for i, path in enumerate(self.paths):
            try:
                info = read_font_info(path)
            except InvalidFontError as e:
                self.item_done.emit(i, path.name, f"Fichier invalide : {e}")
                failed += 1
                continue

            result = install_font(info, scope=self.scope, force=self.force)
            self.item_done.emit(i, info.full_name, result.message)

            if result.status is InstallStatus.INSTALLED:
                installed += 1
            elif result.status is InstallStatus.SKIPPED_DUPLICATE:
                skipped += 1
            else:
                failed += 1

        notify_system()
        self.finished_all.emit(installed, skipped, failed)

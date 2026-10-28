"""Installation d'une police dans Windows : copie, registre, activation.

Par défaut on installe pour l'utilisateur courant (aucun droit admin requis,
Windows 10 1809+). Le mode "système" (tous les utilisateurs) demande les
droits administrateur.
"""
import ctypes
import os
import shutil
import winreg
from enum import Enum
from pathlib import Path

from .font_metadata import FontInfo
from .models import InstallResult, InstallStatus

HWND_BROADCAST = 0xFFFF
WM_FONTCHANGE = 0x001D
SMTO_ABORTIFHUNG = 0x0002

REGISTRY_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"


class Scope(Enum):
    USER = "user"
    SYSTEM = "system"


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def fonts_dir(scope: Scope) -> Path:
    if scope is Scope.SYSTEM:
        return Path(os.environ["WINDIR"]) / "Fonts"
    return Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts"


def _registry_root(scope: Scope):
    return winreg.HKEY_LOCAL_MACHINE if scope is Scope.SYSTEM else winreg.HKEY_CURRENT_USER


def is_already_registered(registry_name: str, scope: Scope) -> bool:
    try:
        with winreg.OpenKey(_registry_root(scope), REGISTRY_PATH) as key:
            winreg.QueryValueEx(key, registry_name)
            return True
    except FileNotFoundError:
        return False


def _unique_destination(target_dir: Path, filename: str) -> Path:
    """Évite d'écraser un fichier différent qui porterait le même nom."""
    dest = target_dir / filename
    if not dest.exists():
        return dest
    stem, ext = Path(filename).stem, Path(filename).suffix
    n = 1
    while dest.exists():
        dest = target_dir / f"{stem}_{n}{ext}"
        n += 1
    return dest


def install_font(info: FontInfo, scope: Scope = Scope.USER, force: bool = False) -> InstallResult:
    already_registered = is_already_registered(info.registry_name, scope)
    if not force and already_registered:
        return InstallResult(
            info.path, InstallStatus.SKIPPED_DUPLICATE, f"{info.full_name} est déjà installée"
        )

    target_dir = fonts_dir(scope)
    target_dir.mkdir(parents=True, exist_ok=True)

    if force and already_registered:
        # Réutilise le fichier déjà enregistré au lieu d'en créer un nouveau :
        # sinon chaque --force laisse une copie orpheline dans Fonts.
        with winreg.OpenKey(_registry_root(scope), REGISTRY_PATH) as key:
            existing_filename, _ = winreg.QueryValueEx(key, info.registry_name)
        dest = target_dir / existing_filename
    else:
        dest = _unique_destination(target_dir, info.path.name)

    try:
        shutil.copy2(info.path, dest)

        # Dans le dossier Fonts (système ou utilisateur, tous deux
        # reconnus par Windows), le nom de fichier seul suffit comme
        # valeur de registre.
        with winreg.OpenKey(_registry_root(scope), REGISTRY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, info.registry_name, 0, winreg.REG_SZ, dest.name)

        ctypes.windll.gdi32.AddFontResourceW(str(dest))

        return InstallResult(info.path, InstallStatus.INSTALLED, f"{info.full_name} installée")

    except PermissionError:
        return InstallResult(
            info.path,
            InstallStatus.FAILED,
            "Droits insuffisants — relance en administrateur pour une installation système",
        )
    except OSError as e:
        return InstallResult(info.path, InstallStatus.FAILED, f"Erreur système : {e}")


def notify_system() -> None:
    """Prévient les applications ouvertes qu'il y a de nouvelles polices."""
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None
    )

"""Installateur/désinstallateur de Schémaja.

Copie l'exe dans %LOCALAPPDATA%\\Programs\\Schémaja, crée un raccourci dans
le menu Démarrer, et enregistre une entrée dans "Applications et
fonctionnalités" (registre Uninstall) pour permettre la désinstallation
standard Windows.

Packagé en exe autonome via PyInstaller avec le vrai Schémaja.exe déjà
construit embarqué comme donnée (voir CLAUDE.md pour la commande de
build). Lancé sans argument : installe. Lancé avec --uninstall : c'est ce
que Windows appelle depuis "Applications et fonctionnalités".

Peut aussi être exécuté directement en développement (`py
installer\\setup_app.py`) sans être compilé : dans ce cas il installe
`dist/Schémaja.exe` tel quel, pratique pour tester ce script sans
reconstruire l'exe d'installation à chaque fois.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import winreg
from pathlib import Path

APP_NAME = "Schémaja"
EXE_FILENAME = "Schémaja.exe"
SETUP_FILENAME = "Schémaja_Setup.exe"
UNINSTALL_KEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"

MB_ICONINFORMATION = 0x40
MB_ICONERROR = 0x10


def _base_dir() -> Path:
    """Dossier contenant l'exe principal à installer."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent / "dist"


def install_dir() -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "Programs" / APP_NAME


def _message_box(text: str, is_error: bool = False) -> None:
    icon = MB_ICONERROR if is_error else MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(0, text, APP_NAME, icon)


def _start_menu_shortcut_path() -> Path:
    start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return start_menu / f"{APP_NAME}.lnk"


def _create_start_menu_shortcut(target_exe: Path) -> None:
    shortcut_path = _start_menu_shortcut_path()
    vbs = (
        'Set oWS = WScript.CreateObject("WScript.Shell")\n'
        f'Set oLink = oWS.CreateShortcut("{shortcut_path}")\n'
        f'oLink.TargetPath = "{target_exe}"\n'
        f'oLink.WorkingDirectory = "{target_exe.parent}"\n'
        f'oLink.IconLocation = "{target_exe}"\n'
        "oLink.Save\n"
    )
    vbs_path = Path(tempfile.gettempdir()) / "schemaja_shortcut.vbs"
    vbs_path.write_text(vbs, encoding="utf-16")
    try:
        subprocess.run(["cscript", "//nologo", str(vbs_path)], check=True)
    finally:
        vbs_path.unlink(missing_ok=True)


def _remove_start_menu_shortcut() -> None:
    _start_menu_shortcut_path().unlink(missing_ok=True)


def _register_uninstall(installed_exe: Path, uninstall_cmd: str) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(installed_exe))
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Vektor")
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)


def _unregister_uninstall() -> None:
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    except FileNotFoundError:
        pass


def install() -> None:
    dest_dir = install_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_exe = dest_dir / EXE_FILENAME
    shutil.copy2(_base_dir() / EXE_FILENAME, dest_exe)

    if getattr(sys, "frozen", False):
        dest_setup = dest_dir / SETUP_FILENAME
        shutil.copy2(sys.executable, dest_setup)
        uninstall_cmd = f'"{dest_setup}" --uninstall'
    else:
        uninstall_cmd = f'"{sys.executable}" "{Path(__file__).resolve()}" --uninstall'

    _create_start_menu_shortcut(dest_exe)
    _register_uninstall(dest_exe, uninstall_cmd)

    _message_box(f"{APP_NAME} a été installé.\n\nRaccourci ajouté au menu Démarrer.")


def uninstall() -> None:
    _remove_start_menu_shortcut()
    _unregister_uninstall()
    _message_box(f"{APP_NAME} a été désinstallé.")

    dest_dir = install_dir()
    if getattr(sys, "frozen", False):
        # Ce process tourne depuis dest_dir : impossible de supprimer le
        # dossier pendant qu'il s'exécute. On programme la suppression via
        # une commande détachée qui attend notre sortie, puis on quitte
        # tout de suite (la boîte de message ci-dessus a déjà bloqué le
        # temps que l'utilisateur la lise). `ping` sert de délai portable :
        # `timeout` plante/reste bloqué sans console attachée (le cas ici,
        # DETACHED_PROCESS), alors que `ping` n'en a pas besoin. Le
        # bootloader PyInstaller onefile met un moment à nettoyer sa
        # propre extraction temporaire après notre sortie, d'où le délai
        # généreux et une deuxième tentative en cas d'échec.
        rmdir_cmd = f'rmdir /s /q "{dest_dir}"'
        script = (
            f"ping -n 6 127.0.0.1 >nul & {rmdir_cmd} "
            f"|| (ping -n 6 127.0.0.1 >nul & {rmdir_cmd})"
        )
        popen_kwargs = dict(
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            # CREATE_BREAKAWAY_FROM_JOB : si ce process tourne dans un job
            # Windows qui tue ses enfants à sa fermeture, le rmdir différé
            # serait sinon tué en même temps que nous sans avoir pu agir.
            subprocess.Popen(
                ["cmd", "/c", script],
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    | subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_BREAKAWAY_FROM_JOB
                ),
                **popen_kwargs,
            )
        except OSError:
            # Le job object refuse le breakaway : on retente sans ce flag
            # (mieux vaut tenter sans que ne pas nettoyer du tout).
            subprocess.Popen(
                ["cmd", "/c", script],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                **popen_kwargs,
            )
    else:
        shutil.rmtree(dest_dir, ignore_errors=True)


def main() -> None:
    try:
        if "--uninstall" in sys.argv:
            uninstall()
        else:
            install()
    except Exception as e:
        _message_box(f"Erreur : {e}", is_error=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

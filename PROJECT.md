# Schémaja — project overview

**Schémaja** is a Windows application that bulk-installs `.ttf` / `.otf`
fonts, instead of installing them one by one from File Explorer. It was
born from a real need as a video maker: quickly making large downloaded
font packs available.

- Author: Victoire NDALA
- Repository: https://github.com/VictoireNdala/Schemaja
- License: Apache-2.0 (see `LICENSE`), third-party notices in `NOTICE`
- Platform: Windows 10 (1809 or later) / Windows 11

## Features

- Scans a folder (recursive by default), individual files, or `.zip`
  archives of fonts (extracted automatically to a temporary folder, with
  protection against malicious "zip slip" paths).
- Reads the **real font name** from its metadata (`name` table, via
  fontTools), never from the file name.
- De-duplicates by real family + style: two different files containing the
  same font are detected as duplicates.
- **Per-user** installation by default (`HKEY_CURRENT_USER`, no
  administrator rights); `--system` mode (all users, `HKEY_LOCAL_MACHINE`)
  available with elevation.
- Fonts are available immediately, no reboot needed (`AddFontResourceW`
  is called after the registry write).
- `--force` option to reinstall an already installed font (the existing
  file is overwritten, no orphan copies).
- Graphical interface with drag and drop, a results table (file / font
  name / status) and a final summary; installation runs in a background
  thread so the window never freezes.

## Ways to use it

| Mode | Command / file |
|---|---|
| Command line | `py main.py "C:\path\MyFonts"` |
| Graphical interface | `py gui.py` |
| Portable exe | `dist/Schémaja.exe` |
| Installer exe | `dist/Schémaja_Setup.exe` (Start menu shortcut + uninstall from "Apps & features") |

CLI options: `--system`, `--no-recursive`, `--force` (equivalent to the
checkboxes in the interface).

## Architecture

```
core/            Business logic (no UI dependency)
  scanner.py       Font discovery, .zip extraction
  font_metadata.py Metadata reading (fontTools)
  font_installer.py Copy, Windows registry, GDI registration
  models.py        Statuses and install results
ui/              PySide6 interface (only calls core/)
  main_window.py   Main window, drag and drop
  install_worker.py Background installation thread
installer/
  setup_app.py     Install / uninstall program for the app itself
main.py          CLI entry point
gui.py           GUI entry point
assets/          Icon (official logo)
tests/           Automated tests
```

Principle: the CLI and the graphical interface are two thin layers on top
of the same `core/`.

## Technologies

- Python 3.12
- fontTools (font metadata)
- PySide6 / Qt for Python (graphical interface)
- PyInstaller (builds the `.exe` files, build tool only)
- pytest (tests)

## Tests

```
py -m pip install -r requirements-dev.txt
py -m pytest tests -v
```

Tests use real dummy fonts (generated with fontTools, prefixed `ZZTest`)
and really write to `HKEY_CURRENT_USER` and the user's Fonts folder, with
automatic cleanup afterwards. The interface tests run without a visible
window (`QT_QPA_PLATFORM=offscreen`). `installer/setup_app.py`
deliberately has no automated test (blocking message boxes) and was
validated manually.

## Known limitations

- `.woff` / `.woff2` deliberately unsupported (Windows does not install
  them natively with this method).
- `.ttc` collections are not handled.
- Windows only (registry and GDI APIs).
- The deferred removal of the install folder on uninstall
  (`Schémaja_Setup.exe`) still needs to be reconfirmed on a machine
  outside the development environment.

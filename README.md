# Schémaja

Bulk-installs `.ttf`/`.otf` font files on Windows with a single command,
without going through the native dialog one font at a time. Also accepts
folders or `.zip` archives of fonts: they are extracted and scanned
automatically.

## Installation

```
pip install -r requirements.txt
```

## Usage

### Graphical interface

```
python gui.py
```

Pick a folder or files, adjust the options if needed, then click "Scan"
and "Install".

### Command line

```
python main.py "C:\Users\you\Downloads\MyFonts"
```

Installs for the current user, no admin rights required. Fonts that are
already installed (same family) are skipped automatically.

Options: `--system` (all users, requires an administrator terminal),
`--no-recursive` (ignore subfolders), `--force` (reinstall even if already
present). The same options are available as checkboxes in the graphical
interface.

### Standalone exe

`dist/Schémaja.exe`: portable version, runs directly without installing
Python. `dist/Schémaja_Setup.exe`: installable version — copies the app to
`%LOCALAPPDATA%\Programs\Schémaja`, adds a Start menu shortcut, and
registers itself in "Apps & features" for a standard uninstall.

## Project status

The core (`core/`) is tested and validated end to end on a real Windows
machine. The CLI (`main.py`) and the PySide6 graphical interface
(`gui.py`) are both built on top of it, without duplicating the
installation logic. See [PROJECT.md](PROJECT.md) for details.

## License

Code licensed under Apache-2.0 (see [LICENSE](LICENSE)). Third-party
component notices are in [NOTICE](NOTICE).

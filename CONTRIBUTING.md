# Contributing to Schémaja

Thanks for your interest in Schémaja! Contributions are welcome under the
terms of the Apache-2.0 license (see [LICENSE](LICENSE)).

## Getting started

Schémaja is Windows-only (it uses the Windows registry and GDI APIs).

```
git clone https://github.com/VictoireNdala/Schemaja.git
cd Schemaja
py -m pip install -r requirements-dev.txt
```

Requires Python 3.12 and Windows 10 (1809) or later.

## Running the project

```
py gui.py                          # graphical interface
py main.py "C:\path\to\fonts"      # command line
```

## Running the tests

```
py -m pytest tests -v
```

Note that the installer tests really write to `HKEY_CURRENT_USER` and to
your user Fonts folder while they run. They use dummy fonts prefixed
`ZZTest` and clean up after themselves, including on failure.

If you write a test that waits on a `QThread`, wait with a `QEventLoop`
connected to the worker's signal. Never use a bare
`while worker.isRunning(): processEvents()` loop: it can crash the process.

## Project structure

- `core/`: all business logic (scanning, metadata, installation).
- `ui/`: PySide6 interface. It must contain no business logic and only
  call into `core/`.
- `main.py` / `gui.py`: thin entry points (CLI / GUI) on top of `core/`.

See [PROJECT.md](PROJECT.md) for the full overview.

## Guidelines

- Read a font's name from its metadata (fontTools), never from its file name.
- Keep the CLI and the GUI behavior in sync by putting logic in `core/`.
- Add or update tests for any behavior change.
- Public documentation and commit messages are written in English.
- Keep pull requests focused: one change per pull request.

## Reporting issues

Open an issue on GitHub with your Windows version, the steps to
reproduce, and the output or error message if any.

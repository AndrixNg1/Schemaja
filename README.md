# Schémaja

Installe en masse des fichiers `.ttf`/`.otf` sur Windows, en une seule commande,
sans passer par la boîte de dialogue native une police à la fois. Accepte
aussi les dossiers ou fichiers `.zip` de polices : ils sont extraits puis
scannés automatiquement.

## Installation

```
pip install -r requirements.txt
```

## Utilisation

### Interface graphique

```
python gui.py
```

Choisir un dossier ou des fichiers, ajuster les options si besoin, cliquer
sur "Scanner" puis "Installer".

### Ligne de commande

```
python main.py "C:\Users\vous\Downloads\MesPolices"
```

Installe pour l'utilisateur courant, sans droits admin requis. Les polices
déjà installées (même famille) sont automatiquement ignorées.

Options : `--system` (tous les utilisateurs, nécessite un terminal
administrateur), `--no-recursive` (ignore les sous-dossiers), `--force`
(réinstalle même si déjà présente). Les mêmes options existent en cases à
cocher dans l'interface graphique.

### Exe autonome

`dist/Schémaja.exe` : version portable, se lance directement sans
installer Python. `dist/Schémaja_Setup.exe` : version installable — copie
l'app dans `%LOCALAPPDATA%\Programs\Schémaja`, ajoute un raccourci au menu
Démarrer, et s'enregistre dans "Applications et fonctionnalités" pour une
désinstallation standard.

## Où en est le projet

Le noyau (`core/`) est testé et validé de bout en bout sur une vraie
machine Windows. Le CLI (`main.py`) et l'interface graphique PySide6
(`gui.py`) sont tous deux construits par-dessus, sans dupliquer la logique
d'installation.

## Licence

Code sous licence Apache-2.0 (voir [LICENSE](LICENSE)). Les notices des
composants tiers (fontTools, PySide6/Qt, PyInstaller) sont dans
[NOTICE](NOTICE).

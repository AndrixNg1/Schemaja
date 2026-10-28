# Schémaja — contexte projet

## Objectif

**Schémaja** est le nom du logiciel (renommé le 2026-08-28, précédemment
sans nom propre — juste appelé "Installeur de polices"). Logiciel Windows
pour installer en masse des fichiers `.ttf`/`.otf`, au lieu de les
installer un par un via l'explorateur. Développé par Vektor pour son usage
personnel de vidéographe (rendre vite disponibles de gros packs de polices
téléchargés).

## Stack

- Python 3.12
- `fontTools` pour lire les vraies métadonnées de police
- PySide6 (6.11.2) pour l'UI graphique — construite par-dessus `core/`,
  en plus du CLI (`main.py`), pas à la place

## État actuel

- **Le noyau (`core/`) est testé et validé de bout en bout sur une vraie
  machine Windows, y compris `font_installer.py` et `main.py`.** Les 19
  tests de `tests/` passent (`py -m pytest tests`), plus une vérification
  manuelle du CLI complet (`main.py` avec un vrai scan + installation +
  désinstallation de polices factices).
- Fichiers du noyau : `core/scanner.py`, `core/font_metadata.py`,
  `core/models.py`, `core/font_installer.py`, et `main.py` (CLI).
  **Correction 2026-08-28** : `font_installer.py` et `models.py` avaient
  été écrits dans un dossier `format/` au lieu de `core/` — `main.py` ne
  démarrait donc pas du tout (`ModuleNotFoundError`). Déplacés dans
  `core/`, le dossier `format/` a été supprimé.
- Un `__init__.py` vide à la racine du projet a été supprimé (il aurait
  faussé la résolution des packages par pytest) et un `conftest.py` vide
  a été ajouté à la racine à la place, pour que `pytest` mette bien la
  racine du projet sur `sys.path`.
- Le dossier `tests/` avait été vidé entre deux sessions (`generate_samples.py`
  et `test_core.py` mentionnés ci-dessous n'existaient plus sur disque) —
  recréés, plus un nouveau `tests/test_installer.py` qui n'existait pas
  encore.
- **Bug réel trouvé et corrigé** dans `install_font()` : avec `force=True`
  sur une police déjà installée, le code créait une nouvelle copie
  (`nom_1.ttf`, `nom_2.ttf`, ...) au lieu de réutiliser le fichier déjà
  enregistré — chaque réinstallation forcée laissait une copie orpheline
  dans le dossier Fonts. Corrigé : en cas de `force` sur une police déjà
  enregistrée, on relit le nom de fichier déjà présent dans le registre et
  on écrase ce même fichier. Test de non-régression :
  `test_install_font_force_does_not_leak_orphan_files`.
- **UI PySide6 construite (2026-08-28)** : `gui.py` (point d'entrée),
  `ui/main_window.py` (fenêtre principale) et `ui/install_worker.py`
  (thread d'installation en arrière-plan, pour ne pas geler l'UI sur un
  gros pack de polices). Aucune logique métier dans `ui/` — tout passe par
  `core/`, exactement comme `main.py`. Fonctionnalités : choix
  dossier/fichiers, options `--system`/`--no-recursive`/`--force`
  équivalentes en cases à cocher, tableau des résultats (fichier / nom de
  police réel / statut), résumé final. Testée avec un vrai scan + une
  vraie installation/désinstallation de polices factices (voir
  `tests/test_gui.py`) et un aperçu visuel (screenshot) du rendu.
- Le CLI (`main.py`) et l'UI (`gui.py`) coexistent, tous deux au-dessus du
  même `core/` inchangé.
- **Glisser-déposer ajouté** sur la fenêtre (`MainWindow.dragEnterEvent`/
  `dropEvent`) : accepte fichiers et dossiers mélangés, réutilise le même
  chemin que les boutons "Choisir…" (`_set_sources`). Testé avec de faux
  événements de drop (`tests/test_gui.py`).
- **Icône = logo officiel (2026-08-28)** : `assets/icon.ico` contient le
  logo officiel du logiciel fourni par Vektor (`Schemaja.jpg`, wordmark
  "Schémaja" sur fond sombre, canvas carré 1024×1024, converti en `.ico`
  256×256). Un premier essai avec un autre logo (`Inspiration Infiniti
  black.jpg`) a été fait puis remplacé par celui-ci, le vrai logo
  officiel du projet. `generate_icon.py` (glyphe "Aa" généré par code)
  n'est plus le design actif, gardé seulement comme référence/fallback.
  Pour remplacer l'icône à nouveau : donner un chemin d'image (n'importe
  quel format courant, PNG/JPG/etc.), pas besoin de la convertir en
  `.ico` à la main — Qt (`QImage` + `QImageWriter`) s'en charge, script
  de conversion réutilisable (redimensionne en 256×256 et écrit le
  `.ico`). Vérifié en rechargeant `icon.ico` et en l'affichant (rendu
  direct du fichier, fiable) et en relançant l'exe reconstruit (titre de
  fenêtre "Schémaja" confirmé) ; la capture d'écran de la fenêtre réelle
  de l'exe ne fonctionne pas de façon fiable dans cet environnement
  (capture une fenêtre superposée au lieu de la bonne — probablement un
  souci de coordonnées lié à l'affichage distant), donc ne pas s'y fier
  pour valider visuellement un changement d'icône côté exe.
- **Packaging en `.exe` autonome** via PyInstaller (`--onefile --windowed
  --icon assets/icon.ico`), pour usage sans installer Python/pip sur la
  machine cible. Commande complète :
  `py -m PyInstaller --noconfirm --windowed --onefile --name "Schémaja" --icon "assets\icon.ico" gui.py`
  → produit `dist/Schémaja.exe` (~47 Mo, autonome). L'accent dans
  `--name` fonctionne sans problème avec PyInstaller sur cette machine
  (testé et vérifié par capture d'écran).
  **Bug réel trouvé et corrigé** : `gui.py` appelait
  `sys.stdout.reconfigure(encoding="utf-8")` sans condition — en mode
  `--windowed` (pas de console), PyInstaller met `sys.stdout` à `None`,
  donc l'exe crashait immédiatement (`AttributeError: 'NoneType' object
  has no attribute 'reconfigure'`) à chaque lancement. Corrigé par
  `if sys.stdout is not None:` avant l'appel. Vérifié en relançant l'exe
  buildé et en confirmant l'ouverture de la fenêtre (capture d'écran).
  Le dossier `build/` et le fichier `Schémaja.spec` sont des artefacts
  PyInstaller (le `.spec` peut être réédité si besoin de personnaliser le
  build — ex. ajouter des données embarquées).
- **Logiciel renommé « Schémaja » (2026-08-28)** : titre de fenêtre
  (`ui/main_window.py`), docstrings de `main.py`/`gui.py`, `README.md` et
  nom de l'exe (`dist/Schémaja.exe`) mis à jour. Le nom interne des
  modules (`core/`, `ui/`, noms de fichiers Python) n'a pas changé — seul
  le nom affiché/commercial du logiciel change.
- **Support des `.zip` dans le scan (2026-09-08/09)** : `core/scanner.py`
  détecte maintenant les fichiers `.zip` (au même titre qu'un fichier ou
  un dossier) et les extrait dans un dossier temporaire
  (`tempfile.mkdtemp`) avant de scanner ce dossier comme d'habitude —
  totalement transparent pour l'appelant, un zip se comporte comme un
  dossier de polices. Extraction toujours récursive à l'intérieur du zip,
  quel que soit `--no-recursive` (qui ne s'applique qu'à la structure de
  dossiers réels autour). Protection **zip slip** : toute entrée dont le
  chemin résolu sortirait du dossier d'extraction est ignorée
  (`Path.is_relative_to`), un zip de police téléchargé restant une entrée
  non fiable. Un zip corrompu est silencieusement ignoré (pas de crash).
  `scan()` a un nouveau paramètre optionnel `extracted_dirs: list[Path]`
  — l'appelant y récupère les dossiers temporaires créés et doit les
  nettoyer via `cleanup_extracted_dirs()` une fois l'installation
  terminée (jamais avant, les chemins scannés pointent dedans). Branché
  dans `main.py` (nettoyage dans un `finally`) et `ui/main_window.py`
  (nettoyage au début de chaque nouveau scan + à la fin de
  `_on_finished`). Filtre de sélection de fichiers de l'UI mis à jour
  pour proposer les `.zip`. Testé : 4 nouveaux tests dans
  `tests/test_core.py` (extraction simple, zip dans un dossier, zip
  corrompu, protection zip slip) + un test end-to-end réel via `main.py`
  (scan → extraction → installation → dédoublonnage, tout correct,
  aucun résidu de dossier temporaire après coup).
- **Exe installable sur la machine (2026-09-09)** : nouveau
  `installer/setup_app.py`, packagé en exe autonome séparé
  `dist/Schémaja_Setup.exe` (le vrai `Schémaja.exe` déjà construit y est
  embarqué via `--add-data`). Lancé sans argument, il copie l'app dans
  `%LOCALAPPDATA%\Programs\Schémaja`, crée un raccourci dans le menu
  Démarrer (via un petit script VBScript temporaire exécuté par
  `cscript` — pas de dépendance `pywin32` ajoutée juste pour ça), et
  enregistre une entrée dans "Applications et fonctionnalités"
  (`HKCU\...\Uninstall\Schémaja`) dont la commande de désinstallation
  réinvoque ce même exe avec `--uninstall`. Peut aussi tourner non
  compilé (`py installer\setup_app.py`) directement sur `dist/Schémaja.exe`,
  pratique pour itérer sans reconstruire l'exe d'installation à chaque
  fois — c'est ce qui a servi à tout mettre au point avant de compiler.
  Commande de build complète :
  `py -m PyInstaller --noconfirm --onefile --windowed --name "Schémaja_Setup" --icon "assets\icon.ico" --add-data "dist\Schémaja.exe;." installer\setup_app.py`
  (nécessite que `dist/Schémaja.exe` existe déjà — build l'app d'abord).
  **Deux bugs réels trouvés et corrigés** pendant la mise au point du
  self-delete du dossier d'installation à la désinstallation (le process
  d'uninstall tourne depuis ce dossier, donc ne peut pas se supprimer
  lui-même pendant qu'il s'exécute — trick classique : programmer la
  suppression via un `cmd /c` détaché qui attend la sortie du process
  puis fait `rmdir /s /q`) :
  1. `timeout /t 2` reste bloqué indéfiniment sans console attachée
     (le cas ici, `DETACHED_PROCESS`) — remplacé par `ping -n 6
     127.0.0.1 >nul`, qui ne dépend d'aucune console.
  2. `subprocess.Popen(...)` sans `stdin`/`stdout`/`stderr` explicites
     échoue parfois silencieusement depuis un exe `--windowed` (pas de
     handles standard à hériter) — corrigé en passant `stdin=stdout=
     stderr=subprocess.DEVNULL`. Ajouté aussi `CREATE_BREAKAWAY_FROM_JOB`
     (avec repli sans ce flag si refusé) au cas où l'environnement
     d'exécution assigne le process à un job Windows qui tuerait ses
     enfants à sa fermeture.
  Testé manuellement en conditions réelles (exe compilé, pas juste le
  script) sur plusieurs cycles install → uninstall : copie de l'exe,
  création du raccourci Démarrer, entrée registre "Applications et
  fonctionnalités", puis à la désinstallation : raccourci supprimé,
  entrée registre supprimée — **confirmés fiables et reproductibles à
  chaque cycle**. Le `rmdir` différé du dossier d'installation lui-même
  rapporte un exit code 0 (succès) à chaque fois, mais sa disparition
  effective n'a pas pu être confirmée de façon fiable *depuis cette
  session Claude Code* (le dossier reste visible dans une invocation
  PowerShell ultérieure de la même session, alors que tout le reste —
  raccourci, registre, y compris des fichiers écrits directement sans
  passer par un process détaché — est toujours vu correctement et
  immédiatement). Tout pointe vers une particularité de sandboxing/
  virtualisation de cet environnement de dev spécifique vis-à-vis des
  process détachés/breakaway, pas vers un bug du script : **à
  reconfirmer par Vektor sur sa machine normale** (lancer
  `dist/Schémaja_Setup.exe`, puis le désinstaller depuis "Applications
  et fonctionnalités" dans les Paramètres Windows, et vérifier que
  `%LOCALAPPDATA%\Programs\Schémaja` a bien disparu après quelques
  secondes).
- **Résumé** : le projet a maintenant quatre façons de l'utiliser — CLI
  (`main.py`), UI PySide6 en Python (`gui.py`), exe portable autonome
  (`dist/Schémaja.exe`), et exe d'installation (`dist/Schémaja_Setup.exe`)
  qui installe l'app avec raccourci Démarrer et désinstallation standard.
  Le scan (CLI, UI, et donc les deux exe) accepte maintenant aussi les
  `.zip` de polices, en plus des dossiers et fichiers `.ttf`/`.otf`. Pas
  de prochaine étape définie — à discuter avec Vektor, notamment pour
  confirmer le point ouvert sur le self-delete ci-dessus une fois testé
  sur sa machine.

## Décisions prises (et pourquoi)

- **Nom de police lu via `fontTools` (table `name`), jamais via le nom de
  fichier.** Les noms de fichiers réels sont souvent trompeurs
  (`font1_export_final_v3.ttf`).
- **Installation par défaut pour l'utilisateur courant
  (`HKEY_CURRENT_USER`), pas tout le système.** Évite d'exiger les droits
  admin à chaque lancement. Le mode "tous les utilisateurs" (`--system`,
  `HKEY_LOCAL_MACHINE`) reste disponible mais demande une élévation.
- **`AddFontResourceW` appelé après l'écriture registre.** Sans ça, la
  police n'apparaît qu'après redémarrage — inacceptable pour un usage
  quotidien.
- **`.woff`/`.woff2` volontairement exclus** de `SUPPORTED_EXTENSIONS`.
  Windows ne les installe pas nativement via cette méthode (registre +
  `AddFontResource`) ; les inclure créerait des entrées qui ne
  fonctionnent pas.
- **Dédoublonnage basé sur `registry_name` (famille + style réels), pas
  sur le nom de fichier.** Deux fichiers différents contenant la même
  police doivent être détectés comme doublons.

## Pièges connus / à surveiller

- Les emojis dans les `print()` peuvent faire planter la console Windows
  par défaut (`cmd.exe` en cp1252) — `sys.stdout.reconfigure(encoding=
  "utf-8")` est déjà en place dans `main.py`, ne pas l'enlever.
- L'installation par utilisateur (`%LOCALAPPDATA%\Microsoft\Windows\Fonts`)
  nécessite Windows 10 1809 ou plus récent.
- Pas de gestion des `.ttc` (collections de polices) pour l'instant — hors
  scope V1.
- `InvalidFontError` est levée sur un fichier texte renommé en `.ttf`,
  mais n'a pas été testée sur un vrai fichier de police réellement
  corrompu.
- **Pour désinstaller/nettoyer une police de test manuellement** : appeler
  `RemoveFontResourceW` (GDI) **avant** de supprimer le fichier physique,
  pas après — sinon GDI ne retrouve plus la ressource à désenregistrer et
  la police peut rester visible (dans les sélecteurs de polices) jusqu'à
  la prochaine session, même si le fichier et le registre sont propres.
  Vécu pendant les tests de cette session.
- `python`/`pip` seuls ne fonctionnent pas dans ce Git Bash (alias
  Windows Store cassé) — utiliser `py` (le lanceur officiel Windows) à la
  place, notamment via PowerShell.
- Aucun vrai environnement virtuel dans le projet : `fonttools`, `pytest`
  et `PySide6` sont installés globalement via `py -m pip install`.
- **Crash natif trouvé dans les tests GUI** (`STATUS_STACK_BUFFER_OVERRUN`,
  exit code Windows `-1073740791`) : attendre la fin de `InstallWorker`
  (le `QThread` d'installation) avec une boucle manuelle
  `while worker.isRunning(): qapp.processEvents()` fait planter le
  process Python au bout de quelques tests enchaînés dans la même
  session. Corrigé dans `tests/test_gui.py` en attendant via un vrai
  `QEventLoop` connecté au signal `finished_all` du worker (pattern Qt
  standard). L'app réelle (`gui.py`) n'est pas concernée : elle utilise
  `app.exec()` normalement, jamais ce polling manuel — mais si un futur
  test ou script attend un `QThread` à la main, reproduire ce piège est
  facile, donc toujours utiliser `QEventLoop`/signal, jamais une boucle
  `processEvents()` nue.

## Tests

- `tests/generate_samples.py` génère des polices factices avec
  `fontTools.fontBuilder` (aucune vraie police n'est nécessaire).
- `tests/test_core.py` valide le scan (`scanner.py`) et l'extraction de
  métadonnées (`font_metadata.py`).
- `tests/test_installer.py` (nouveau) valide `font_installer.py` de bout
  en bout **avec de vraies écritures registre `HKCU` et de vrais fichiers
  copiés** dans le dossier Fonts utilisateur — noms de police toujours
  préfixés `ZZTest...` pour ne jamais entrer en collision avec une vraie
  police, et nettoyage automatique (registre + fichier + désenregistrement
  GDI) après chaque test, y compris en cas d'échec.
- Dépendances de dev (`pytest`, `pyinstaller`) listées dans
  `requirements-dev.txt` : `py -m pip install -r requirements-dev.txt`.
- `tests/test_gui.py` : test de fumée de l'UI PySide6, piloté sans fenêtre
  visible (`QT_QPA_PLATFORM=offscreen`) donc utilisable en CI/headless.
  Vérifie scan → table peuplée, installation réelle → statuts et résumé
  corrects, glisser-déposer (fichiers/dossiers + chemins inexistants
  ignorés), et l'avertissement (pas de crash) si `--system` est coché sans
  droits admin.
- 4 nouveaux tests de scan de `.zip` dans `tests/test_core.py` (extraction
  simple, zip dans un dossier, zip corrompu ignoré, protection zip slip)
  — voir entrée "Support des .zip" ci-dessus.
- Lancer toute la suite : `py -m pytest tests -v` (25 tests au 09/09/2026,
  tous verts).
- Ces tests écrivent réellement dans `HKEY_CURRENT_USER` et dans
  `%LOCALAPPDATA%\Microsoft\Windows\Fonts` le temps de leur exécution — à
  garder en tête si on les lance sur une machine où d'autres polices
  utilisent un nom commençant par `ZZTest` (improbable).
- **`installer/setup_app.py` n'a volontairement aucun test automatisé** :
  `install()`/`uninstall()` affichent un `MessageBoxW` bloquant, ce qui
  ferait pendre indéfiniment un run `pytest` (personne pour cliquer sur
  OK). Validé uniquement manuellement (voir "Exe installable" ci-dessus).
  Si un jour on veut l'automatiser, il faudrait d'abord extraire la
  logique des boîtes de message pour pouvoir les mocker/désactiver en
  test.

---
Garder ce fichier à jour à mesure que le projet avance.

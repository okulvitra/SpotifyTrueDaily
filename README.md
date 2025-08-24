# SpotifyTrueDaily : Playlist "Mon Daily" plus personnalisable

SpotifyTrueDaily est une application de bureau Windows conçue pour créer et mettre à jour quotidiennement une playlist Spotify personnelle nommée "Journalière". Cette playlist est un mélange dynamique de vos podcasts préférés (uniquement les derniers épisodes non lus et non-audiobook), de vos écoutes musicales récentes et récurrentes, de découvertes aléatoires issues de votre bibliothèque, ainsi que de nouvelles suggestions musicales optionnelles fournies par l'API SoundStat. Le contenu est ensuite intelligemment entrelacé pour une expérience d'écoute variée.

L'application dispose d'une interface graphique simple pour configurer vos clés API, ajuster la quantité de chaque type de contenu pour chaque mise à jour, et lancer le processus.

## Fonctionnalités Principales

  * **Interface Graphique Utilisateur (GUI) :**
      * Onglet "Application" pour lancer les mises à jour et visualiser les logs.
      * Champs pour ajuster dynamiquement le nombre de titres récents, top titres, épisodes de podcasts, et recommandations SoundStat pour chaque exécution.
      * Onglet "Settings" pour une configuration sécurisée de vos clés API (Spotify, SoundStat) et des paramètres de contenu par défaut.
  * **Création/Mise à Jour Automatique :** Génère une playlist "Journalière" ou rafraîchit son contenu si elle existe déjà.
  * **Podcasts à Jour et Filtrés :**
      * Intègre les derniers épisodes de vos podcasts Spotify suivis.
      * Vérifie si un épisode a déjà été écouté en entier et l'exclut si c'est le cas.
      * Filtre et ignore les chapitres d'audiobooks qui pourraient apparaître comme des "émissions".
  * **Musique Personnalisée :**
      * Inclut vos titres les plus écoutés récemment.
      * Ajoute vos titres favoris (top écoutes).
      * Propose des morceaux aléatoires de votre bibliothèque Spotify.
  * **Nouvelles Découvertes (Optionnel) :** Utilise l'API [SoundStat.info](http://soundstat.info/) pour suggérer de nouvelles pistes basées sur vos écoutes récentes (configurable).
  * **Contenu Entrelacé :** Organise la playlist avec une alternance de podcasts et de musiques (par défaut : 1 podcast suivi de 3 musiques).
  * **Automatisation Facilitée :** Conçu pour être exécuté quotidiennement via le Planificateur de Tâches Windows en utilisant l'exécutable fourni ou un script batch.

## Stack Technique

  * **Python 3.x**
  * **Tkinter :** Pour l'interface graphique utilisateur.
  * **Spotipy :** Bibliothèque Python pour interagir avec l'API Web Spotify.
  * **SoundStat API :** API tierce pour obtenir des recommandations musicales.
  * **Requests :** Bibliothèque Python pour effectuer des appels HTTP à l'API SoundStat.
  * **PyInstaller :** (Utilisé pour empaqueter l'application en `.exe` - pour les développeurs souhaitant reconstruire).

## Installation et Utilisation

Il y a deux façons d'utiliser SpotifyTrueDaily : en utilisant l'exécutable `.exe` pré-compilé (pour les utilisateurs Windows) ou en exécutant le script Python depuis les sources (pour les développeurs ou les utilisateurs sur d'autres plateformes).

### Méthode 1 : Pour les Utilisateurs Windows (Utilisation de l'`.exe`)

1.  **Télécharger l'Application :**

      * Rendez-vous dans la section [Releases](https://github.com/okulvitra/SpotifyTrueDaily/releases) de ce dépôt GitHub.
      * Téléchargez la dernière version de `SpotifyTrueDaily.exe` (ou le `.zip` le contenant).
      * Téléchargez également le fichier `config_template.py` depuis la racine du dépôt.

2.  **Préparation :**

      * Créez un dossier sur votre ordinateur où vous souhaitez placer l'application (par exemple, `C:\SpotifyTrueDailyApp`).
      * Placez `SpotifyTrueDaily.exe` dans ce dossier.
      * Placez `config_template.py` dans le **même dossier** que `SpotifyTrueDaily.exe`.

3.  **Configuration Initiale (via la GUI) :**

      * Lancez `SpotifyTrueDaily.exe`.
      * Allez dans l'onglet "**Settings**".
      * **Application Spotify :**
          * Si ce n'est pas déjà fait, allez sur le [Spotify Developer Dashboard](community.spotify.com), créez une nouvelle application.
          * Notez votre `Client ID` et votre `Client Secret`.
          * Dans les paramètres de votre application Spotify (sur le dashboard), ajoutez un "**Redirect URI**". Une valeur comme `http://127.0.0.1:8888/callback` est recommandée.
          * Entrez votre `Client ID`, `Client Secret`, et le `Redirect URI` (exactement le même que celui configuré sur le dashboard Spotify) dans les champs correspondants de l'onglet "Settings".
      * **Clé API SoundStat (Optionnel) :**
          * Si vous souhaitez utiliser les recommandations SoundStat, rendez-vous sur [SoundStat.info](https://soundstat.info/) pour obtenir une clé API et entrez-la. Sinon, laissez ce champ vide (les recommandations SoundStat seront désactivées si les compteurs associés sont à 0).
      * **Paramètres de Contenu par Défaut :** Ajustez les valeurs pour le nombre de titres récents, top titres, etc., selon vos préférences. Ces valeurs seront sauvegardées dans `config.py` et utilisées comme valeurs par défaut au démarrage de l'application.
      * Cliquez sur "**Sauvegarder Toute la Configuration**". Cela créera (ou mettra à jour) un fichier `config.py` dans le même dossier que l'`.exe`.

4.  **Première Authentification Spotify :**

      * Allez dans l'onglet "**Application**".
      * Ajustez si besoin les compteurs pour le nombre de titres/podcasts pour *cette exécution spécifique*.
      * Cliquez sur "**Start Playlist Update**".
      * Une page de votre navigateur s'ouvrira pour vous demander d'autoriser l'application Spotify. Acceptez.
      * Après autorisation, vous serez redirigé vers votre `Redirect URI`. **Copiez l'URL complète** de cette page de redirection.
      * **Collez cette URL complète dans la petite fenêtre de console** qui s'est peut-être ouverte avec l'application (ou si l'application vous le demande directement via une popup - la méthode actuelle utilise la console pour cette étape).
      * Une fois cela fait, un fichier `.spotipyoauthcache` sera créé à côté de l'`.exe`, permettant les authentifications futures sans cette étape manuelle.

5.  **Utilisation Quotidienne :**

      * Lancez `SpotifyTrueDaily.exe`.
      * Ajustez les paramètres de contenu dans l'onglet "Application" si désiré pour la session en cours.
      * Cliquez sur "Start Playlist Update". Les logs s'afficheront dans la fenêtre.

### Méthode 2 : Pour les Développeurs (Utilisation des Scripts Python)

1.  **Prérequis :** Python 3.x et pip.
2.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/okulvitra/SpotifyTrueDaily.git](https://github.com/okulvitra/SpotifyTrueDaily.git)
    cd SpotifyTrueDaily
    ```
3.  **Créer et activer un environnement virtuel :**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1  # PowerShell
    # .\.venv\Scripts\activate.bat # CMD
    ```
4.  **Installer les dépendances :**
    (Assurez-vous que le fichier `requirements.txt` est à jour)
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configurer les Clés API :**
      * Copiez `config_template.py` en `config.py`.
      * Ouvrez `config.py` et remplissez vos identifiants Spotify et SoundStat, ainsi que les paramètres de contenu par défaut.
6.  **Première Authentification & Lancement :**
      * Exécutez l'application GUI :
        ```bash
        python app_gui.py
        ```
      * Suivez les étapes 3 et 4 de la "Méthode 1" pour la configuration via la GUI et la première authentification Spotify. Vous pouvez aussi lancer `python playlist_manager.py` directement après avoir configuré `config.py` pour la première authentification si vous préférez la console pour cette étape.

## Optionnel : Automatisation avec le Planificateur de Tâches Windows

Pour que l'application mette à jour votre playlist automatiquement :

1.  **Fichier Batch (Optionnel mais recommandé pour l'`.exe`) :**
    Créez un fichier `run_spotifytrueDaily_exe.bat` dans le même dossier que `SpotifyTrueDaily.exe` :

    ```batch
    @echo off
    REM S'assure que le script est exécuté depuis le bon répertoire
    cd /D "%~dp0" 
    echo Lancement de SpotifyTrueDaily.exe...
    SpotifyTrueDaily.exe
    echo Tâche terminée.
    ```

    `%~dp0` se développe en chemin du dossier contenant le fichier batch.

2.  **Configurer la Tâche Planifiée :**

      * Ouvrez le **Planificateur de tâches**.
      * Créez une nouvelle tâche.
      * **Déclencheur :** "Tous les jours" à l'heure souhaitée.
      * **Action :** "Démarrer un programme".
          * **Programme/script :** Chemin vers `SpotifyTrueDaily.exe` OU chemin vers `run_spotifytrueDaily_exe.bat`.
          * **Démarrer dans (facultatif) :** **TRÈS IMPORTANT \!** Mettez ici le chemin complet du dossier où se trouve `SpotifyTrueDaily.exe` (et donc `config.py` et `.spotipyoauthcache`). Par exemple : `C:\SpotifyTrueDailyApp`.
      * Configurez les options supplémentaires (ex: "Exécuter même si l'utilisateur n'est pas connecté").

## Structure des Fichiers Principaux

  * `app_gui.py` : Le script Python pour l'interface graphique Tkinter.
  * `playlist_manager.py` : Le script Python contenant toute la logique de base pour interagir avec Spotify et SoundStat, et pour construire la playlist.
  * `config.py` (local, non versionné) : Contient vos clés API et paramètres. Généré/Utilisé par la GUI.
  * `config_template.py` : Modèle pour `config.py`.
  * `requirements.txt` : Liste des dépendances Python.
  * `.gitignore` : Spécifie les fichiers à ignorer par Git.
  * `run_playlist_updater.bat` (si vous l'utilisez pour automatiser la version script Python plutôt que l'exe) ou `run_spotifytrueDaily_exe.bat` (pour l'exe).


## Disclaimer

Ce script a été développé avec l'assistance de Google Gemini 2.5 Pro dans un esprit de "vibe coding" et d'exploration collaborative. L'IA a aidé à la structuration du code, au débogage, à l'explication de concepts et à la rédaction de documentation.

# English

# SpotifyTrueDaily: Personalized "Daily Drive" playlist


SpotifyTrueDaily is a Windows desktop application designed to create and update a personal Spotify playlist named "Journalière" (Daily) on a daily basis. This playlist is a dynamic mix of your favorite podcasts (only the latest unplayed, non-audiobook episodes), your recent and most frequent music listens, random discoveries from your library, and optional new music suggestions provided by the SoundStat API. The content is then intelligently interleaved for a varied listening experience.

The application features a simple graphical user interface (GUI) to configure your API keys, adjust the quantity of each type of content for each update, and launch the process.

## Key Features

  * **Graphical User Interface (GUI):**
      * "Application" tab to initiate updates and view logs.
      * Fields to dynamically adjust the number of recent tracks, top tracks, podcast episodes, and SoundStat recommendations for each run.
      * "Settings" tab for secure configuration of your API keys (Spotify, SoundStat) and default content parameters.
  * **Automatic Creation/Update:** Generates a "Journalière" playlist or refreshes its content if it already exists.
  * **Up-to-Date and Filtered Podcasts:**
      * Integrates the latest episodes from your followed Spotify podcasts.
      * Checks if an episode has been fully played and excludes it if so.
      * Filters out and ignores audiobook chapters that might appear as "shows."
  * **Personalized Music:**
      * Includes your most recently played tracks.
      * Adds your favorite (top) tracks.
      * Suggests random tracks from your Spotify library.
  * **New Discoveries (Optional):** Uses the [SoundStat.info](http://soundstat.info/) API to suggest new tracks based on your recent listens (configurable).
  * **Interleaved Content:** Organizes the playlist with an alternation of podcasts and music (default: 1 podcast followed by 3 songs).
  * **Easy Automation:** Designed to be run daily via Windows Task Scheduler using the provided executable or a batch script.

## Tech Stack

  * **Python 3.x**
  * **Tkinter:** For the graphical user interface.
  * **Spotipy:** Python library to interact with the Spotify Web API.
  * **SoundStat API:** Third-party API to get music recommendations.
  * **Requests:** Python library to make HTTP calls to the SoundStat API.
  * **PyInstaller:** (Used to package the application into an `.exe` - for developers wishing to rebuild).

## Installation and Usage

There are two ways to use SpotifyTrueDaily: by using the pre-compiled `.exe` executable (for Windows users) or by running the Python script from the source (for developers or users on other platforms).

### Method 1: For Windows Users (Using the `.exe`)

1.  **Download the Application:**

      * Go to the [Releases](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/okulvitra/SpotifyTrueDaily/releases) section of this GitHub repository.
      * Download the latest version of `SpotifyTrueDaily.exe` (or the `.zip` file containing it).
      * Also, download the `config_template.py` file from the root of the repository.

2.  **Preparation:**

      * Create a folder on your computer where you want to place the application (e.g., `C:\SpotifyTrueDailyApp`).
      * Place `SpotifyTrueDaily.exe` in this folder.
      * Place `config_template.py` in the **same folder** as `SpotifyTrueDaily.exe`.

3.  **Initial Configuration (via the GUI):**

      * Launch `SpotifyTrueDaily.exe`.
      * Go to the "**Settings**" tab.
      * **Spotify Application:**
          * If you haven't already, go to the [Spotify Developer Dashboard](community.spotify.com), create a new application.
          * Note your `Client ID` and `Client Secret`.
          * In your Spotify application settings (on the dashboard), add a "**Redirect URI**." A value like `http://127.0.0.1:8888/callback` is recommended.
          * Enter your `Client ID`, `Client Secret`, and the `Redirect URI` (exactly the same as configured on the Spotify dashboard) into the corresponding fields in the "Settings" tab.
      * **SoundStat API Key (Optional):**
          * If you wish to use SoundStat recommendations, go to [SoundStat.info](https://soundstat.info/) to obtain an API key and enter it. Otherwise, leave this field blank (SoundStat recommendations will be disabled if the related counts are 0).
      * **Default Content Parameters:** Adjust the values for the number of recent tracks, top tracks, etc., according to your preferences. These values will be saved in `config.py` and used as defaults when the application starts.
      * Click "**Sauvegarder Toute la Configuration**" (Save All Configuration). This will create (or update) a `config.py` file in the same folder as the `.exe`.

4.  **First Spotify Authentication:**

      * Go to the "**Application**" tab.
      * If needed, adjust the counts for tracks/podcasts for *this specific run*.
      * Click "**Start Playlist Update**".
      * A page in your browser will open asking you to authorize the Spotify application. Accept.
      * After authorization, you will be redirected to your `Redirect URI`. **Copy the full URL** from your browser's address bar.
      * **Paste this full URL into the small console window** that may have opened with the application (or if the application prompts you directly via a popup - the current method uses the console for this step).
      * Once done, a `.spotipyoauthcache` file will be created next to the `.exe`, allowing future authentications without this manual step.

5.  **Daily Usage:**

      * Launch `SpotifyTrueDaily.exe`.
      * Adjust content parameters in the "Application" tab if desired for the current session.
      * Click "Start Playlist Update". Logs will be displayed in the window.

### Method 2: For Developers (Using Python Scripts)

1.  **Prerequisites:** Python 3.x and pip.
2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/okulvitra/SpotifyTrueDaily.git](https://github.com/okulvitra/SpotifyTrueDaily.git)
    cd SpotifyTrueDaily
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1  # PowerShell
    # .\.venv\Scripts\activate.bat # CMD
    ```
4.  **Install dependencies:**
    (Ensure the `requirements.txt` file is up-to-date)
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure API Keys:**
      * Copy `config_template.py` to `config.py`.
      * Open `config.py` and fill in your Spotify and SoundStat credentials, as well as default content parameters.
6.  **First Authentication & Launch:**
      * Run the GUI application:
        ```bash
        python app_gui.py
        ```
      * Follow steps 3 and 4 from "Method 1" for GUI-based configuration and first Spotify authentication. You can also run `python playlist_manager.py` directly after setting up `config.py` for the first authentication if you prefer the console for that step.

## Optional: Automation with Windows Task Scheduler

To have the application update your playlist automatically:

1.  **Batch File (Optional but recommended for the `.exe`):**
    Create a file `run_spotifytrueDaily_exe.bat` in the same folder as `SpotifyTrueDaily.exe`:

    ```batch
    @echo off
    REM Ensures the script runs from the correct directory
    cd /D "%~dp0"
    echo Launching SpotifyTrueDaily.exe...
    SpotifyTrueDaily.exe
    echo Task finished.
    ```

    `%~dp0` expands to the path of the directory containing the batch file.

2.  **Configure the Scheduled Task:**

      * Open **Task Scheduler** on Windows.
      * Create a new task.
      * **Trigger:** "Daily" at the desired time.
      * **Action:** "Start a program".
          * **Program/script:** Path to `SpotifyTrueDaily.exe` OR path to `run_spotifytrueDaily_exe.bat`.
          * **Start in (optional):** **VERY IMPORTANT\!** Enter the full path to your project's root folder here (e.g., `C:\Path\To\Your\Project\spotiapp\`). This ensures that relative paths and files like `config.py` and `.spotipyoauthcache` are found correctly.
      * Configure additional options (e.g., "Run whether user is logged on or not").

## Key Project Files

  * `app_gui.py`: The Python script for the Tkinter GUI.
  * `playlist_manager.py`: The Python script containing all core logic for Spotify/SoundStat interaction and playlist building.
  * `config.py` (local, not versioned): Contains your API keys and parameters. Generated/Used by the GUI.
  * `config_template.py`: Template for `config.py`.
  * `requirements.txt`: List of Python dependencies.
  * `.gitignore`: Specifies files to be ignored by Git.
  * `run_playlist_updater.bat` (if used for automating the Python script version) or `run_spotifytrueDaily_exe.bat` (for the .exe).

## Disclaimer

This script was developed with the assistance of Google Gemini 2.5 Pro in a spirit of "vibe coding" and collaborative exploration. The AI assisted with code structuring, debugging, explaining concepts, and drafting documentation.

# SpotifyTrueDaily : Playlist "Mon Daily" plus personnalisable

SpotifyTrueDaily est un script Python conçu pour créer et mettre à jour quotidiennement une playlist Spotify personnelle nommée "Journalière". Cette playlist est un mélange dynamique de vos podcasts préférés (avec les derniers épisodes), de vos écoutes musicales récentes et récurrentes, de découvertes aléatoires issues de votre bibliothèque, ainsi que de nouvelles suggestions musicales fournies par l'API SoundStat. Le contenu est ensuite intelligemment entrelacé pour une expérience d'écoute variée.

## Fonctionnalités

* **Création/Mise à Jour Automatique :** Génère une playlist "Journalière" ou rafraîchit son contenu si elle existe déjà.
* **Podcasts à Jour :** Intègre les derniers épisodes publiés de vos podcasts Spotify suivis.
* **Musique Personnalisée :**
    * Inclut vos titres les plus écoutés récemment.
    * Ajoute vos titres favoris (top écoutes).
    * Propose des morceaux aléatoires de votre bibliothèque Spotify.
* **Nouvelles Découvertes :** Utilise l'API [SoundStat.info](http://soundstat.info/) pour suggérer de nouvelles pistes basées sur vos écoutes récentes.
* **Contenu Entrelacé :** Organise la playlist avec une alternance de podcasts et de musiques (par défaut : 1 podcast suivi de 3 musiques).
* **Planification Flexible :** Conçu pour être exécuté quotidiennement via une tâche planifiée (par exemple, avec le Planificateur de Tâches Windows).

## Stack Utilisée

* **Python 3.x**
* **Spotipy :** Bibliothèque Python pour interagir avec l'API Web Spotify.
* **SoundStat API :** API tierce pour obtenir des recommandations musicales basées sur des pistes de référence.
* **Requests :** Bibliothèque Python pour effectuer des appels HTTP à l'API SoundStat.
* **Schedule :** (Utilisé initialement pour la planification interne, mais l'automatisation finale est recommandée via un planificateur système).

## Marche à Suivre : Installation et Configuration

Suivez ces étapes pour configurer et lancer le script sur votre machine Windows.

### 1. Prérequis

* **Python 3.x :** Assurez-vous que Python est installé sur votre système. Vous pouvez le télécharger depuis [python.org](https://www.python.org/). Lors de l'installation, cochez "Add Python to PATH".
* **pip :** Le gestionnaire de paquets Python (généralement inclus avec Python).
* **Compte Spotify :** Un compte Spotify (gratuit ou Premium).
* **Compte Spotify Développeur :** Nécessaire pour créer une application et obtenir les identifiants API.
* **Clé API SoundStat :** Nécessaire pour obtenir des recommandations de nouvelles musiques.

### 2. Installation

1.  **Cloner le dépôt (si vous l'avez sur GitHub) ou télécharger les fichiers :**
    Si vous avez publié le projet sur GitHub, clonez-le :
    ```bash
    git clone [https://github.com/okulvitra/SpotifyTrueDaily.git](https://github.com/okulvitra/SpotifyTrueDaily.git)
    cd SpotifyTrueDaily
    ```
    Sinon, assurez-vous que tous les fichiers du projet (`playlist_manager.py`, `config_template.py`, etc.) sont dans un même dossier.

2.  **Créer un environnement virtuel (recommandé) :**
    Ouvrez un terminal (PowerShell ou CMD) dans le dossier du projet et exécutez :
    ```bash
    python -m venv .venv
    ```

3.  **Activer l'environnement virtuel :**
    ```bash
    # Sur Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # Sur Windows (CMD)
    # .\.venv\Scripts\activate.bat
    ```
    Vous devriez voir `(.venv)` au début de votre invite de commande.

4.  **Installer les dépendances :**
    Créez un fichier `requirements.txt` à la racine de votre projet avec le contenu suivant :
    ```txt
    spotipy
    schedule
    requests
    ```
    Puis, installez ces dépendances :
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration des Clés API

Le script a besoin d'identifiants pour accéder aux API de Spotify et SoundStat. Ces informations sont confidentielles et doivent être stockées localement dans un fichier `config.py`.

1.  **Application Spotify :**
    * Allez sur le [Spotify Developer Dashboard](community.spotify.com).
    * Créez une nouvelle application.
    * Notez votre `Client ID` et votre `Client Secret`.
    * Dans les paramètres de votre application Spotify, ajoutez un "Redirect URI". Pour un usage local, `http://127.0.0.1:8888/callback` ou `http://localhost:8888/callback` sont des choix courants. **Assurez-vous que cet URI correspond exactement à celui que vous mettrez dans votre fichier de configuration.**

2.  **Clé API SoundStat :**
    * Rendez-vous sur [SoundStat.info](https://soundstat.info/) et suivez leurs instructions pour obtenir une clé API.

3.  **Créer le fichier `config.py` :**
    * À la racine de votre projet, vous devriez trouver un fichier nommé `config_template.py`.
    * **Copiez** ce fichier et **renommez la copie** en `config.py`.
    * Ouvrez `config.py` avec un éditeur de texte et **remplissez vos propres identifiants** à la place des placeholders :

        ```python
        # config.py - REMPLISSEZ AVEC VOS INFORMATIONS
        
        # Configuration Spotify
        SPOTIPY_CLIENT_ID = 'VOTRE_SPOTIFY_CLIENT_ID_ICI'
        SPOTIPY_CLIENT_SECRET = 'VOTRE_SPOTIFY_CLIENT_SECRET_ICI'
        SPOTIPY_REDIRECT_URI = '[http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)' # Ou l'URI que vous avez configuré

        # Configuration SoundStat
        SOUNDSTAT_API_KEY = 'VOTRE_CLE_API_SOUNDSTAT_ICI'
        ```
    * **Important :** Le fichier `config.py` est ignoré par Git (via le fichier `.gitignore`) pour ne pas exposer vos clés si vous partagez le projet. Ne supprimez pas `config.py` de votre `.gitignore` si vous utilisez Git.

### 4. Première Exécution et Authentification Spotify

Avant de pouvoir automatiser le script, vous devez l'exécuter manuellement au moins une fois pour autoriser l'accès à votre compte Spotify :

1.  Assurez-vous que votre environnement virtuel est activé.
2.  Exécutez le script :
    ```bash
    python playlist_manager.py
    ```
3.  Lors de la première exécution, une page de votre navigateur s'ouvrira pour vous demander d'autoriser l'application Spotify que vous avez créée. Acceptez.
4.  Après autorisation, vous serez redirigé vers votre `SPOTIPY_REDIRECT_URI` (par exemple, `http://127.0.0.1:8888/callback?code=...`). **Copiez l'URL complète** de cette page de redirection depuis la barre d'adresse de votre navigateur.
5.  **Collez cette URL complète dans le terminal** où le script Python vous le demande, puis appuyez sur Entrée.

Une fois cette étape franchie, le script créera un fichier `.cache` (ou similaire) dans votre dossier projet. Ce fichier stocke votre token d'accès Spotify, permettant au script de se réauthentifier automatiquement lors des exécutions suivantes sans redemander cette manipulation. **N'oubliez pas que ce fichier `.cache` est également listé dans `.gitignore` pour ne pas être partagé.**

## Utilisation Manuelle

Après la configuration et la première authentification, vous pouvez lancer le script manuellement à tout moment (avec l'environnement virtuel activé) :

```bash
python playlist_manager.py
```
Le script effectuera une mise à jour de la playlist "Journalière".

## Optionnel : Automatisation avec le Planificateur de Tâches Windows
Pour que le script mette à jour votre playlist automatiquement tous les jours sans intervention manuelle, vous pouvez utiliser le Planificateur de tâches Windows.

1.  Créer un fichier batch (run_playlist_updater.bat) :
    À la racine de votre projet, créez un fichier nommé run_playlist_updater.bat avec le contenu suivant (adaptez les chemins si votre projet n'est pas à C:\Users\Name\Desktop\spotiapp) :
```bash
    @echo off
REM Change directory to the script's location
cd /D "C:\Users\M\Desktop\spotiapp"

REM Activate virtual environment
echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

REM Run the Python script
echo Running Python script...
python "playlist_manager.py"

echo Script finished.
```
2.  Configurer la Tâche Planifiée :
* Ouvrez le Planificateur de tâches sur Windows.
* Cliquez sur "Créer une tâche de base...".
* Nom : Mise à jour Playlist Spotify Journalière (ou similaire).
* Déclencheur : Choisissez "Tous les jours" et réglez l'heure de début souhaitée (par exemple, 06:00:00 ou 22:00:00). Vous pourrez ajouter d'autres déclencheurs plus tard si besoin.
* Action : Choisissez "Démarrer un programme".
* Programme/script : Indiquez le chemin complet vers votre fichier run_playlist_updater.bat.
* Démarrer dans (facultatif) : Indiquez le chemin de votre dossier projet (ex: C:\Users\M\Desktop\spotiapp\).
* Suivez les instructions pour finaliser la création.
* Dans les propriétés avancées de la tâche (cochez la case "Ouvrir les propriétés..." à la fin de l'assistant), vous pouvez configurer des options comme "Exécuter même si l'utilisateur n'est pas connecté" (nécessitera votre mot de passe Windows) et "Exécuter avec les autorisations maximales".

## Disclaimer

Ce script a été développé avec l'assistance de Google Gemini 2.5 Pro dans un esprit de "vibe coding" et d'exploration collaborative. L'IA a aidé à la structuration du code, au débogage, à l'explication de concepts et à la rédaction de documentation.

# English

# SpotifyTrueDaily: Personalized "Daily Drive" playlist

SpotifyTrueDaily is a Python script designed to create and update a personal Spotify playlist named "Journalière" (Daily) on a daily basis. This playlist is a dynamic mix of your favorite podcasts (featuring the latest episodes), your recent and most frequent music listens, random discoveries from your library, and new music suggestions provided by the SoundStat API. The content is then intelligently interleaved for a varied listening experience.

## Features

* **Automatic Creation/Update:** Generates a "Journalière" playlist or refreshes its content if it already exists.
* **Up-to-Date Podcasts:** Integrates the latest published episodes of your followed Spotify podcasts.
* **Personalized Music:**
    * Includes your most recently played tracks.
    * Adds your favorite (top) tracks.
    * Suggests random tracks from your Spotify library.
* **New Discoveries:** Uses the [SoundStat.info](http://soundstat.info/) API to suggest new tracks based on your recent listens.
* **Interleaved Content:** Organizes the playlist with an alternation of podcasts and music (default: 1 podcast followed by 3 songs).
* **Flexible Scheduling:** Designed to be run daily via a scheduled task (e.g., using Windows Task Scheduler).

## Tech Stack

* **Python 3.x**
* **Spotipy:** Python library to interact with the Spotify Web API.
* **SoundStat API:** Third-party API to get music recommendations based on reference tracks.
* **Requests:** Python library to make HTTP calls to the SoundStat API.
* **Schedule:** (Initially used for internal scheduling, but final automation is recommended via a system scheduler).

## Getting Started: Installation and Configuration

Follow these steps to set up and run the script on your Windows machine.

### 1. Prerequisites

* **Python 3.x:** Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/). During installation, check "Add Python to PATH."
* **pip:** The Python package manager (usually included with Python).
* **Spotify Account:** A Spotify account (free or Premium).
* **Spotify Developer Account:** Required to create an application and obtain API credentials.
* **SoundStat API Key:** Required to get new music recommendations.

### 2. Installation

1.  **Clone the repository (if you have it on GitHub) or download the files:**
    If you have published the project on GitHub, clone it:
    ```bash
    git clone [https://github.com/okulvitra/SpotifyTrueDaily.git](https://github.com/okulvitra/SpotifyTrueDaily.git)
    cd SpotifyTrueDaily
    ```
    Otherwise, ensure all project files (`playlist_manager.py`, `config_template.py`, etc.) are in the same folder.

2.  **Create a virtual environment (recommended):**
    Open a terminal (PowerShell or CMD) in the project folder and run:
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    # On Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # On Windows (CMD)
    # .\.venv\Scripts\activate.bat
    ```
    You should see `(.venv)` at the beginning of your command prompt.

4.  **Install dependencies:**
    Create a `requirements.txt` file in the root of your project with the following content:
    ```txt
    spotipy
    schedule
    requests
    ```
    Then, install these dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 3. API Key Configuration

The script needs credentials to access the Spotify and SoundStat APIs. This information is confidential and should be stored locally in a `config.py` file.

1.  **Spotify Application:**
    * Go to the [Spotify Developer Dashboard](community.spotify.com).
    * Create a new application.
    * Note your `Client ID` and `Client Secret`.
    * In your Spotify application settings, add a "Redirect URI." For local use, `http://127.0.0.1:8888/callback` or `http://localhost:8888/callback` are common choices. **Ensure this URI exactly matches the one you will put in your configuration file.**

2.  **SoundStat API Key:**
    * Go to [SoundStat.info](https://soundstat.info/) and follow their instructions to obtain an API key.

3.  **Create the `config.py` file:**
    * In the root of your project, you should find a file named `config_template.py`.
    * **Copy** this file and **rename the copy** to `config.py`.
    * Open `config.py` with a text editor and **fill in your own credentials** in place of the placeholders:

        ```python
        # config.py - FILL IN WITH YOUR INFORMATION
        
        # Spotify Configuration
        SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID_HERE'
        SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET_HERE'
        SPOTIPY_REDIRECT_URI = '[http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)' # Or your configured URI

        # SoundStat Configuration
        SOUNDSTAT_API_KEY = 'YOUR_SOUNDSTAT_API_KEY_HERE'
        ```
    * **Important:** The `config.py` file is ignored by Git (via the `.gitignore` file) to avoid exposing your keys if you share the project. Do not remove `config.py` from your `.gitignore` if you are using Git.

### 4. First Run and Spotify Authentication

Before you can automate the script, you must run it manually at least once to authorize access to your Spotify account:

1.  Ensure your virtual environment is activated.
2.  Run the script:
    ```bash
    python playlist_manager.py
    ```
3.  On the first run, a page in your browser will open asking you to authorize the Spotify application you created. Accept.
4.  After authorization, you will be redirected to your `SPOTIPY_REDIRECT_URI` (e.g., `http://127.0.0.1:8888/callback?code=...`). **Copy the full URL** of this redirect page from your browser's address bar.
5.  **Paste this full URL into the terminal** where the Python script prompts you, then press Enter.

Once this step is completed, the script will create a `.cache` file (or similar) in your project folder. This file stores your Spotify access token, allowing the script to re-authenticate automatically on subsequent runs without requiring this manual step. **Remember that this `.cache` file is also listed in `.gitignore` to prevent it from being shared.**

## Manual Usage

After setup and the first authentication, you can run the script manually at any time (with the virtual environment activated):

```bash
python playlist_manager.py
```

Optional: Automation with Windows Task Scheduler
To have the script update your playlist automatically every day without manual intervention, you can use Windows Task Scheduler.

Create a batch file (run_playlist_updater.bat):
    In the root of your project, create a file named run_playlist_updater.bat with the following content (adjust paths if your project is not at C:\Users\YourUser\Desktop\spotiapp):
```bash
@echo off
REM Change directory to the script's location
cd /D "C:\Path\To\Your\Project\spotiapp"

REM Activate virtual environment
echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

REM Run the Python script
echo Running Python script...
python "playlist_manager.py"

echo Script finished.
```
2.  Configure the Scheduled Task:
*Open Task Scheduler on Windows.
    *Click "Create Basic Task...".
    *Name: Update Spotify Daily Playlist (or similar).
    *Trigger: Choose "Daily" and set the desired start time (e.g., 06:00:00 or 22:00:00). You can add more triggers later if needed.
    *Action: Choose "Start a program".
    *Program/script: Enter the full path to your run_playlist_updater.bat file.
    *Start in (optional): Enter the path to your project folder (e.g., C:\Path\To\Your\Project\spotiapp\).
    *Follow the prompts to finalize creation.
    *In the advanced properties of the task (check the "Open the Properties dialog..." box at the end of the wizard), you can configure options like "Run whether user is logged on or not" (will require your Windows password) and "Run with highest privileges."

## Disclaimer

This script was developed with the assistance of Google Gemini 2.5 Pro in a spirit of "vibe coding" and collaborative exploration. The AI assisted with code structuring, debugging, explaining concepts, and drafting documentation.

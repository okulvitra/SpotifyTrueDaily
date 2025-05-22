# SpotifyTrueDaily : Votre Playlist Spotify Journalière Personnalisée et Automatisée

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

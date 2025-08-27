# SpotifyTrueDaily - Modern UI Edition

## 🎵 Playlist "Journalière" Personnalisée et Automatisée

SpotifyTrueDaily est une application de bureau moderne conçue pour créer et mettre à jour quotidiennement une playlist Spotify personnelle nommée "Journalière". Cette playlist est un mélange dynamique de vos podcasts préférés, de vos écoutes musicales récentes, de vos titres favoris, et de nouvelles suggestions musicales optionnelles.

L'application dispose d'une **interface utilisateur moderne** avec une sidebar de navigation, des cartes distinctes, et un panneau de logs intégré pour une expérience utilisateur améliorée. L'application utilise l'icône `truedaily.ico` pour une identification facile dans la barre des tâches.

## 🎨 Interface Utilisateur avec Icônes Lucide

L'application utilise des icônes basées sur la bibliothèque [Lucide Icons](https://lucide.dev/) pour une expérience visuelle cohérente :
* **Navigation** : 🏠 Dashboard, 🎵 Configuration, ⚙️ Settings, ℹ️ About
* **Actions** : ➕ Créer, 🔄 Rafraîchir, 🗑️ Supprimer
* **Statuts** : ✅ Succès, ❌ Erreur, ⚠️ Avertissement
* **Contenu** : 🎵 Musique, 🎙️ Podcasts, 📚 Bibliothèque

### 🖼️ Icône d'Application

L'application utilise le fichier `truedaily.ico` pour une identification facile dans la barre des tâches et le gestionnaire de fenêtres. Le système supporte plusieurs formats d'icônes et inclut des méthodes de fallback pour une compatibilité maximale.

## 🚀 Fonctionnalités Principales

### 🎨 Interface Utilisateur Moderne
* **Sidebar de Navigation** : Accès rapide aux différentes sections avec icônes
* **Cartes Distinctes** : Interface organisée en cartes visuellement séparées
* **Panneau de Logs** : Affichage des messages système avec icônes et couleurs
* **Sidebar Rétractable** : Bouton pour cacher/afficher la sidebar
* **Raccourcis Clavier** : Ctrl+R pour rafraîchir, Ctrl+L pour basculer les logs

### 📋 Configuration de la Playlist
* **Ajustement Dynamique** : Modification en temps réel du nombre de titres/épisodes
* **Cartes de Configuration** : Interface intuitive pour chaque type de contenu
* **Validation Intégrée** : Vérification des valeurs numériques

### 🎵 Contenu Personnalisé
* **Podcasts à Jour** : Derniers épisodes non lus de vos podcasts suivis
* **Filtrage Intelligent** : Exclusion des audiobooks et épisodes déjà écoutés
* **Musique Récente** : Vos titres les plus écoutés récemment
* **Top Titres** : Vos favoris selon Spotify
* **Bibliothèque Aléatoire** : Découvertes parmi vos morceaux sauvegardés
* **Recommandations SoundStat** : Suggestions basées sur vos goûts musicaux

### 🔧 Automatisation
* **Exécutable Windows** : Application standalone facile à utiliser
* **Planification** : Compatibilité avec le Planificateur de Tâches Windows
* **Authentification Persistante** : Cache OAuth pour éviter les réauthentifications

## 🛠 Stack Technique

* **Python 3.x**
* **CustomTkinter** : Framework moderne pour l'interface utilisateur
* **Spotipy** : Bibliothèque Python pour l'API Web Spotify
* **SoundStat API** : API tierce pour les recommandations musicales
* **Requests** : Bibliothèque HTTP pour les appels API
* **PyInstaller** : Packaging en `.exe` pour distribution

## 📥 Installation et Utilisation

### Pour les Utilisateurs Windows (Exécutable)

1. **Télécharger l'Application :**
   * Rendez-vous dans la section [Releases](https://github.com/okulvitra/SpotifyTrueDaily/releases)
   * Téléchargez `SpotifyTrueDaily.exe`, `config_template.py`, et `truedaily.ico`

2. **Préparation :**
   * Créez un dossier pour l'application
   * Placez tous les fichiers dans le même dossier
   * L'icône `truedaily.ico` sera automatiquement utilisée par l'application

3. **Configuration Initiale :**
   * Lancez `SpotifyTrueDaily.exe`
   * Cliquez sur "API Settings" dans la sidebar
   * Entrez vos identifiants Spotify Developer
   * Configurez votre clé SoundStat (optionnel)
   * Sauvegardez la configuration

4. **Première Authentification :**
   * Cliquez sur "Refresh Now" dans le dashboard
   * Autorisez l'application dans votre navigateur
   * La playlist "Journalière" est créée automatiquement

### Pour les Développeurs (Scripts Python)

1. **Prérequis :** Python 3.x et pip
2. **Installation :**
   ```bash
   git clone https://github.com/okulvitra/SpotifyTrueDaily.git
   cd SpotifyTrueDaily
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\Activate.ps1  # Windows PowerShell
   pip install -r requirements.txt
   ```
3. **Configuration :**
   * Copiez `config_template.py` en `config.py`
   * Remplissez vos identifiants API
4. **Lancement :**
   ```bash
   python app_modern.py
   ```

## 🎯 Nouvelles Fonctionnalités de l'Interface Moderne

### Sidebar de Navigation
* 🏠 **Dashboard** : Vue d'ensemble et actions rapides
* 🎵 **Playlist Configuration** : Ajustement des paramètres de contenu
* ⚙️ **API Settings** : Configuration des clés API
* ℹ️ **About** : Informations sur l'application

### Panneau de Logs Amélioré
* 📝 **Affichage en temps réel** des opérations
* 🎨 **Coloration par type** (info, succès, avertissement, erreur)
* ⌨️ **Raccourci** : Ctrl+L pour afficher/masquer
* 🗑️ **Nettoyage** : Bouton pour vider les logs

### Cartes de Configuration
* ➕ **Boutons +/-** : Ajustement intuitif des valeurs
* 📊 **Indicateurs visuels** : Min/max et valeurs actuelles
* 🎯 **Validation automatique** : Respect des limites définies

## ⌨️ Raccourcis Clavier

* **Ctrl+R** : Rafraîchir la playlist
* **Ctrl+L** : Afficher/masquer le panneau de logs
* **ESC** : Fermer les dialogues

## 🔧 Automatisation avec Planificateur de Tâches

1. **Créer un fichier batch :**
   ```batch
   @echo off
   cd /D "%~dp0"
   SpotifyTrueDaily.exe
   ```

2. **Configurer la tâche planifiée :**
   * **Déclencheur** : Quotidien à l'heure souhaitée
   * **Action** : Démarrer le programme `SpotifyTrueDaily.exe`
   * **Démarrer dans** : Dossier contenant l'application

## 📁 Structure des Fichiers

* `app_modern.py` : Application principale avec interface moderne
* `modern_ui.py` : Composants d'interface utilisateur modernes
* `playlist_manager.py` : Logique de gestion des playlists
* `config.py` : Configuration utilisateur (généré)
* `config_template.py` : Modèle de configuration
* `requirements.txt` : Dépendances Python

## 🤝 Credits

* Créé par okulvitra
* Interface moderne avec CustomTkinter
* Intégration Spotify via Spotipy
* Recommandations SoundStat API

## ⚠️ Disclaimer

Cette application a été développée avec l'assistance de Google Gemini dans un esprit de "vibe coding" et d'exploration collaborative. L'IA a aidé à la structuration du code, au débogage, et à la rédaction de documentation.
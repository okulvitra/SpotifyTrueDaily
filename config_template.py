# config_template.py
# Copiez ce fichier en config.py et remplissez vos informations personnelles.
# NE PARTAGEZ PAS VOTRE FICHIER config.py !

# Configuration Spotify
SPOTIPY_CLIENT_ID = 'VOTRE_SPOTIFY_CLIENT_ID_ICI'
SPOTIPY_CLIENT_SECRET = 'VOTRE_SPOTIFY_CLIENT_SECRET_ICI'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback' # Ou votre URI de redirection

# Configuration SoundStat
SOUNDSTAT_API_KEY = 'VOTRE_CLE_API_SOUNDSTAT_ICI'

# \--- Paramètres de contenu de la Playlist Journalière ---

# Valeurs par défaut suggérées, ajustez selon vos préférences.

# Un avertissement s'affichera dans l'application si les totaux sont élevés.

MAX_RECENT_TRACKS = 5
MAX_TOP_TRACKS = 5
MAX_PODCAST_EPISODES = 3
MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = 2
MAX_SOUNDSTAT_RECOMMENDATIONS = 3
SOUNDSTAT_SEED_TRACK_COUNT = 2

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime
import schedule
import time
import random
import requests
import os
import sys
# import logging

# logging.basicConfig() # Nécessaire si pas déjà configuré ailleurs
# logging.getLogger('spotipy').setLevel(logging.DEBUG)
# logging.getLogger('requests.packages.urllib3').setLevel(logging.DEBUG) # Pour voir les logs de la bibliothèque HTTP sous-jacente
# ou essayez logging.getLogger('urllib3').setLevel(logging.DEBUG) si le chemin ci-dessus ne fonctionne pas

# --- CHARGEMENT DE LA CONFIGURATION ---
class ConfigError(Exception): # Définir une exception personnalisée
    pass
try:
    import config # Essaie d'importer config.py

    SPOTIPY_CLIENT_ID = config.SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET = config.SPOTIPY_CLIENT_SECRET
    SPOTIPY_REDIRECT_URI = config.SPOTIPY_REDIRECT_URI
    SOUNDSTAT_API_KEY = config.SOUNDSTAT_API_KEY

    # Vérifier que les clés ont été remplies et ne sont pas les valeurs par défaut du template
    if 'VOTRE_' in SPOTIPY_CLIENT_ID or \
       'VOTRE_' in SPOTIPY_CLIENT_SECRET or \
       'VOTRE_' in SOUNDSTAT_API_KEY:
        print("ERREUR: Veuillez remplir vos clés API dans le fichier 'config.py'.")
        print("Ne pas utiliser les valeurs du template 'VOTRE_..._ICI'.")
         # Lever une exception au lieu de print et exit
        raise ConfigError("ERREUR: Veuillez remplir vos clés API dans le fichier 'config.py'.\n"
                          "Ne pas utiliser les valeurs du template 'VOTRE_..._ICI'.")

except ImportError:
    raise ConfigError("ERREUR: Fichier de configuration 'config.py' introuvable.\n"
                      "Veuillez copier 'config_template.py' en 'config.py' et y mettre vos clés API.")
except AttributeError as e:
    raise ConfigError(f"ERREUR: Une variable de configuration est manquante dans 'config.py': {e}")

# Nom de la playlist à gérer
PLAYLIST_NAME = "Journalière"

# Scopes (permissions) nécessaires pour l'application
# Tu peux trouver la liste complète ici : https://developer.spotify.com/documentation/web-api/concepts/scopes
SCOPES = [
    "user-read-recently-played",    # Pour les écoutes récentes
    "user-top-read",                # Pour les titres et artistes favoris
    "playlist-read-private",        # Pour lire les playlists privées
    "playlist-modify-public",       # Pour créer/modifier des playlists publiques
    "playlist-modify-private",      # Pour créer/modifier des playlists privées (choisis l'un ou l'autre ou les deux)
    "user-library-read",            # Pour lire la bibliothèque de l'utilisateur
    "user-follow-read",             # Pour les podcasts suivis (si besoin)
    "user-read-private", #pour accéder aux données comme la localisation
    "user-read-playback-position"
    
]

# Heures de mise à jour (format 24h)
UPDATE_TIMES = ["06:00", "22:00"]

# URL de l'API SoundStat
SOUNDSTAT_API_URL = 'https://soundstat.info/api/v1/recommendations/similar'

# --- CHARGEMENT DES PARAMÈTRES DE CONTENU DEPUIS CONFIG.PY ---
# Fournir des valeurs par défaut robustes si config.py est manquant ou incomplet.
DEFAULT_CONTENT_SETTINGS_PM = {
    "MAX_RECENT_TRACKS": 1, # Valeurs minimales par défaut pour le fonctionnement
    "MAX_TOP_TRACKS": 1,
    "MAX_PODCAST_EPISODES": 1,
    "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": 1,
    "MAX_SOUNDSTAT_RECOMMENDATIONS": 0, # Par défaut désactivé si non configuré
    "SOUNDSTAT_SEED_TRACK_COUNT": 0
}
def get_config_value(config_module, key, default_value):
    try:
        return getattr(config_module, key)
    except AttributeError:
        print(f"Avertissement: '{key}' non trouvé dans config.py, utilisation de la valeur par défaut: {default_value}")
        return default_value

# S'assurer que 'config' a bien été importé
if 'config' in locals() or 'config' in globals():
    MAX_RECENT_TRACKS = get_config_value(config, 'MAX_RECENT_TRACKS', DEFAULT_CONTENT_SETTINGS_PM['MAX_RECENT_TRACKS'])
    MAX_TOP_TRACKS = get_config_value(config, 'MAX_TOP_TRACKS', DEFAULT_CONTENT_SETTINGS_PM['MAX_TOP_TRACKS'])
    MAX_PODCAST_EPISODES = get_config_value(config, 'MAX_PODCAST_EPISODES', DEFAULT_CONTENT_SETTINGS_PM['MAX_PODCAST_EPISODES'])
    MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = get_config_value(config, 'MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY', DEFAULT_CONTENT_SETTINGS_PM['MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY'])
    MAX_SOUNDSTAT_RECOMMENDATIONS = get_config_value(config, 'MAX_SOUNDSTAT_RECOMMENDATIONS', DEFAULT_CONTENT_SETTINGS_PM['MAX_SOUNDSTAT_RECOMMENDATIONS'])
    SOUNDSTAT_SEED_TRACK_COUNT = get_config_value(config, 'SOUNDSTAT_SEED_TRACK_COUNT', DEFAULT_CONTENT_SETTINGS_PM['SOUNDSTAT_SEED_TRACK_COUNT'])
else:
    # Cas où l'import de config a échoué plus tôt (géré par ConfigError)
    # On définit quand même les globales avec les valeurs par défaut pour que le module soit importable par la GUI
    print("Avertissement (playlist_manager): Le module config n'a pas pu être chargé. Utilisation des valeurs par défaut internes pour le contenu.")
    MAX_RECENT_TRACKS = DEFAULT_CONTENT_SETTINGS_PM['MAX_RECENT_TRACKS']
    MAX_TOP_TRACKS = DEFAULT_CONTENT_SETTINGS_PM['MAX_TOP_TRACKS']
    MAX_PODCAST_EPISODES = DEFAULT_CONTENT_SETTINGS_PM['MAX_PODCAST_EPISODES']
    MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = DEFAULT_CONTENT_SETTINGS_PM['MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY']
    MAX_SOUNDSTAT_RECOMMENDATIONS = DEFAULT_CONTENT_SETTINGS_PM['MAX_SOUNDSTAT_RECOMMENDATIONS']
    SOUNDSTAT_SEED_TRACK_COUNT = DEFAULT_CONTENT_SETTINGS_PM['SOUNDSTAT_SEED_TRACK_COUNT']

# Supprimez ou commentez les anciennes définitions en dur de ces constantes
# si elles étaient plus bas dans playlist_manager.py.

# --- FONCTIONS SPOTIFY ---

def authenticate_spotify():
    """Authentifie l'utilisateur et retourne un objet Spotify."""
    # Validate credentials before attempting auth
    if 'VOTRE_' in SPOTIPY_CLIENT_ID or 'VOTRE_' in SPOTIPY_CLIENT_SECRET:
        raise ConfigError("Invalid Spotify credentials detected - update config.py with your credentials from Spotify Developer Dashboard")
    
    print(f"Authentication attempt with Client ID: {SPOTIPY_CLIENT_ID[:3]}...{SPOTIPY_CLIENT_SECRET[-3:]}")
    if getattr(sys, 'frozen', False):
        application_path_auth = os.path.dirname(sys.executable)
    else:
        application_path_auth = os.path.dirname(os.path.abspath(__file__))

    cache_file_path = os.path.join(application_path_auth, ".spotipyoauthcache") # Nom de fichier cache explicite

    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=" ".join(SCOPES), # Les scopes doivent être une chaîne séparée par des espaces
        cache_path=cache_file_path
    )
    sp = spotipy.Spotify(auth_manager=auth_manager, retries=0, requests_timeout=10,)
    print("Authentification réussie!")
    return sp

def get_or_create_playlist(sp, user_id, playlist_name):
    """Récupère l'ID d'une playlist existante ou la crée si elle n'existe pas."""
    playlists = sp.current_user_playlists(limit=20) # Augmenter la limite pour être plus sûr
    target_playlist_id = None
    # --- DEBUG START ---
    print(f"DEBUG: Searching for playlist '{playlist_name}' among {len(playlists['items'])} playlists returned by API.")
    # --- DEBUG END ---
    for playlist in playlists['items']:
        # --- DEBUG START ---
        print(f"DEBUG: Checking playlist: '{playlist['name']}' (ID: {playlist['id']})")
        # --- DEBUG END ---
        if playlist['name'] == playlist_name:
            target_playlist_id = playlist['id']
            print(f"Playlist '{playlist_name}' trouvée avec l'ID: {target_playlist_id}")
            break

    if not target_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=f"Votre playlist {playlist_name} auto-générée.")
        target_playlist_id = new_playlist['id']
        print(f"Playlist '{playlist_name}' créée avec l'ID: {target_playlist_id}")

    return target_playlist_id

def get_user_playlists(sp=None):
    """Récupère toutes les playlists de l'utilisateur."""
    if sp is None:
        sp = authenticate_spotify()
    
    try:
        playlists_data = sp.current_user_playlists(limit=50)
        return playlists_data
    except Exception as e:
        print(f"Erreur lors de la récupération des playlists: {e}")
        return {'items': []}

def get_recent_tracks_uris(sp, limit=5):
    """Récupère les URIs des titres écoutés récemment."""
    results = sp.current_user_recently_played(limit=limit)
    track_uris = []
    print(f"\n--- Titres Récents (max {limit}) ---")
    for item in results['items']:
        track = item['track']
        if track and track['uri'] not in track_uris: # Éviter les doublons si écouté plusieurs fois de suite
             track_uris.append(track['uri'])
    return track_uris

def get_top_tracks_uris(sp, limit=5, time_range='short_term'):
    """Récupère les URIs des titres les plus écoutés (short_term, medium_term, long_term)."""
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    track_uris = []
    print(f"\n--- Top Titres ({time_range}, max {limit}) ---")
    for track in results['items']:
        if track and track['uri'] not in track_uris:
            track_uris.append(track['uri'])
    return track_uris

def get_saved_shows_latest_episodes_uris(sp, limit_shows, market=None):
    """
    Récupère un nombre défini (`limit_shows`) de derniers épisodes de podcasts NON LUS.
    Parcourt les émissions suivies par l'utilisateur par pagination jusqu'à ce que le nombre souhaité
    d'épisodes valides (non-lus et non-audiobook) soit atteint, ou jusqu'à ce que toutes les émissions
    aient été vérifiées.
    """
    print(f"\n--- Recherche de {limit_shows} épisode(s) de podcast non lu(s) (hors audiobooks) ---")

    episode_uris_to_add = []

    if limit_shows == 0:
        print("Récupération des podcasts désactivée (MAX_PODCAST_EPISODES est 0).")
        return episode_uris_to_add

    offset = 0
    shows_per_page = 20  # Nombre d'émissions à récupérer par appel API (max 50). Ajustable si besoin.

    # Boucle de pagination pour parcourir les émissions sauvegardées
    while len(episode_uris_to_add) < limit_shows:
        try:
            # Appel pour récupérer un lot d'émissions
            saved_shows_results = sp.current_user_saved_shows(limit=shows_per_page, offset=offset)
        except spotipy.SpotifyException as e:
            print(f"Erreur Spotipy lors de la récupération des émissions sauvegardées à l'offset {offset}: {e}")
            break  # Arrêter la recherche en cas d'erreur
        except Exception as e:
            print(f"Erreur inattendue lors de la récupération des émissions sauvegardées: {e}")
            break

        # Si Spotify ne retourne plus d'émissions, on a parcouru toute la bibliothèque
        if not saved_shows_results or not saved_shows_results['items']:
            print("Toutes les émissions sauvegardées ont été vérifiées.")
            break

        # Itérer sur le lot d'émissions récupéré
        for item in saved_shows_results['items']:
            # Ancien 'break' ici a été supprimé pour une logique plus claire
            # La condition de la boucle 'while' externe gère la limite.

            show = item['show']
            show_id = show['id']
            show_name = show['name']

            try:
                # Appel API pour récupérer le dernier épisode de CETTE émission spécifique
                show_episodes_data = sp.show_episodes(show_id, limit=1, market=market)
                time.sleep(0.3)  # Petite pause après chaque appel `show_episodes` pour être prudent

                if show_episodes_data and show_episodes_data['items']:
                    latest_item = show_episodes_data['items'][0]
                    item_type = latest_item.get('type', 'unknown')

                    # 1. Filtrer les chapitres d'audiobooks
                    if item_type == 'chapter':
                        print(f"  -> Ignoré: '{latest_item['name']}' de '{show_name}' est un audiobook.")
                        continue  # Passe à l'émission suivante de la boucle

                    # 2. Vérifier si l'épisode a été lu
                    is_fully_played = False
                    resume_point = latest_item.get('resume_point')
                    # --- DEBUG START ---
                    print(f"DEBUG: Episode '{latest_item['name']}' (ID: {latest_item['id']})")
                    print(f"DEBUG: resume_point data: {resume_point}")
                    # --- DEBUG END ---
                    if isinstance(resume_point, dict) and resume_point.get('fully_played') is True:
                        is_fully_played = True

                    if not is_fully_played:
                        if latest_item['uri'] not in episode_uris_to_add:
                            print(f"  -> Ajouté: '{latest_item['name']}' (non lu) de '{show_name}'.")
                            episode_uris_to_add.append(latest_item['uri'])
                            # Vérifier immédiatement si la limite est atteinte
                            if len(episode_uris_to_add) >= limit_shows:
                                break # Sortir de la boucle 'for' pour arrêter le traitement de cette page
                    else:
                        print(f"  -> Ignoré: '{latest_item['name']}' de '{show_name}' a déjà été écouté.")
                else:
                    print(f"  -> Aucun épisode trouvé pour l'émission '{show_name}'.")

            except spotipy.SpotifyException as e_spot:
                print(f"Erreur Spotipy en récupérant les épisodes de '{show_name}': {e_spot}")
            except Exception as e:
                print(f"Erreur inattendue pour l'émission '{show_name}': {e}")

        # Si on a déjà assez d'épisodes, on sort de la boucle principale `while`
        if len(episode_uris_to_add) >= limit_shows:
            print(f"Limite de {limit_shows} épisodes atteinte.")
            break

        # Mettre à jour l'offset pour la prochaine page d'émissions
        offset += shows_per_page

    # Fin de la boucle while

    if not episode_uris_to_add:
        print("Aucun nouvel épisode de podcast valide et non lu n'a été trouvé après vérification.")
    else:
        print(f"\n{len(episode_uris_to_add)} épisode(s) de podcast valide(s) sélectionné(s).")

    return episode_uris_to_add


def get_soundstat_similar_tracks(api_key, seed_spotify_track_id, limit=5, min_popularity=None, genre_match=False):
    """
    Récupère des pistes similaires depuis l'API SoundStat pour un seed_track_id Spotify donné.
    Retourne une liste d'URIs de pistes Spotify recommandées, ou une liste vide en cas d'erreur.
    """
    if not api_key or api_key == 'TA_CLE_API_SOUNDSTAT': # Vérifie si la clé a été changée
        print("ERREUR SoundStat: Clé API non configurée ou valeur par défaut non modifiée.")
        return []

    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }
    params = {
        'seed_track_id': seed_spotify_track_id, # Doit être l'ID Spotify pur, ex: "3vjnuagiopTRGWIBNaZJF0"
        'limit': limit
    }
    if min_popularity is not None and 0 <= min_popularity <= 100:
        params['min_popularity'] = min_popularity
    if genre_match: # booléen
        params['genre_match'] = str(genre_match).lower() # 'true' ou 'false' en string

    print(f"\n--- Appel SoundStat pour seed ID: {seed_spotify_track_id}, limit: {limit} ---")
    recommended_spotify_uris = []
    try:
        response = requests.get(SOUNDSTAT_API_URL, headers=headers, params=params)
        response.raise_for_status() 
        
        data = response.json()
        
        # La documentation que tu as fournie indique "Returns: TrackIDList - List of recommended track IDs"
        # On va supposer que 'data' est cette liste directement, ou un objet la contenant.
        raw_track_ids = []
        if isinstance(data, list):
            raw_track_ids = data
        elif isinstance(data, dict) and 'TrackIDList' in data and isinstance(data['TrackIDList'], list):
            raw_track_ids = data['TrackIDList']
        elif isinstance(data, dict) and 'track_ids' in data and isinstance(data['track_ids'], list): # Autre possibilité
            raw_track_ids = data['track_ids']
        else:
            print(f"SoundStat: Réponse inattendue ou format de 'TrackIDList' non trouvé. Réponse reçue: {data}")
            return []

        for track_id in raw_track_ids:
            if isinstance(track_id, str) and track_id.strip(): # S'assurer que c'est une chaîne non vide
                if track_id.startswith("spotify:track:"):
                    recommended_spotify_uris.append(track_id)
                else:
                    # Convertir l'ID simple en URI Spotify complet
                    recommended_spotify_uris.append(f"spotify:track:{track_id.strip()}") 
            else:
                print(f"SoundStat: ID de piste non valide ou format inattendu reçu: '{track_id}'")
            
        print(f"SoundStat: {len(recommended_spotify_uris)} URIs de recommandations valides traités.")
        return recommended_spotify_uris

    except requests.exceptions.HTTPError as http_err:
        print(f"SoundStat: Erreur HTTP: {http_err} - URL: {response.url} - Réponse: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"SoundStat: Erreur de requête: {req_err} - URL: {SOUNDSTAT_API_URL}")
    except ValueError as json_err: 
        print(f"SoundStat: Erreur de décodage JSON: {json_err} - Réponse: {response.text}")
    except Exception as e:
        print(f"SoundStat: Une erreur inattendue est survenue: {e}")
    
    return []

def update_playlist_content(sp, playlist_id, track_uris):
    """Vide la playlist et y ajoute les nouveaux titres/épisodes."""
    if not track_uris:
        print("Aucun contenu à ajouter à la playlist.")
        # Optionnel: vider la playlist même si rien à ajouter
        try:
            sp.playlist_replace_items(playlist_id, [])
            print(f"Playlist '{PLAYLIST_NAME}' vidée car aucun nouveau contenu.")
        except Exception as e:
            print(f"Erreur en tentant de vider la playlist '{PLAYLIST_NAME}': {e}")
        return

    # Spotify API limite à 100 items par requête pour add_items
    # Et replace_items remplace tout en une fois (max 100 aussi implicitement si on passe les URIs)
    # Pour plus de 100 items, il faudrait appeler add_items en plusieurs fois après avoir vidé.
    # Ici on suppose qu'on aura moins de 100 items au total.
    print(f"\n--- Mise à jour de la playlist '{PLAYLIST_NAME}' (ID: {playlist_id}) ---")
    try:
        # D'abord, vider la playlist
        sp.playlist_replace_items(playlist_id, []) # Envoie une liste vide pour tout supprimer
        print(f"Playlist '{PLAYLIST_NAME}' vidée.")
        
        # Ensuite, ajouter les nouveaux items par lots de 100 maximum
        for i in range(0, len(track_uris), 50):
            batch = track_uris[i:i + 50]
            sp.playlist_add_items(playlist_id, batch)
        print(f"{len(track_uris)} éléments ajoutés à la playlist '{PLAYLIST_NAME}'.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la playlist '{PLAYLIST_NAME}': {e}")
        # Affichage détaillé de l'erreur pour aider au débogage
        import traceback
        traceback.print_exc() 
        if "too short" in str(e).lower():
            print("Cela peut arriver si la liste des URIs est vide ou si un URI est malformé.")
        elif "premium only" in str(e).lower():
            print("Certaines actions API peuvent être limitées pour les comptes non-Premium.")

# --- FONCTION PRINCIPALE DE MISE À JOUR ---

def refresh_daily_playlist():
    """Fonction principale pour rafraîchir la playlist."""
    print(f"\n--- {datetime.datetime.now()}: Début de la mise à jour de la playlist '{PLAYLIST_NAME}' ---")

    try:
        sp = authenticate_spotify()

        current_user_data = sp.current_user()
        user_id = current_user_data['id']
        user_market = current_user_data['country']

        playlist_id = get_or_create_playlist(sp, user_id, PLAYLIST_NAME)
        

        # Collecte des contenus
        all_uris_to_add = []

        # 1. Podcasts (derniers épisodes)
        # Note: l'ordre d'ajout est important si tu veux les podcasts en premier
        # podcast_episode_uris = []
        podcast_episode_uris = get_saved_shows_latest_episodes_uris(sp, limit_shows=MAX_PODCAST_EPISODES, market=user_market)
        print(f"DEBUG: {len(podcast_episode_uris)} épisodes de podcast récupérés.") # Log de débogage
        time.sleep(1)
        all_uris_to_add.extend(podcast_episode_uris)
        # time.sleep(1)

        # 2. Musiques basées sur les écoutes
        recent_tracks_uris = get_recent_tracks_uris(sp, limit=MAX_RECENT_TRACKS)
        print(f"DEBUG: {len(recent_tracks_uris)} titres récents récupérés.") # Log de débogage
        all_uris_to_add.extend(recent_tracks_uris)
        time.sleep(1)

        top_tracks_uris = get_top_tracks_uris(sp, limit=MAX_TOP_TRACKS, time_range='short_term') # 'short_term', 'medium_term', 'long_term'
        print(f"DEBUG: {len(top_tracks_uris)} top titres récupérés.") # Log de débogage
        all_uris_to_add.extend(top_tracks_uris)
        time.sleep(1)
        
        print(f"\n--- Titres Aléatoires de la Bibliothèque (max {MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY}) ---")
        library_recommendation_uris = []
        saved_tracks_results = sp.current_user_saved_tracks(limit=50)
        if saved_tracks_results and saved_tracks_results['items']:
            user_library_track_uris = [item['track']['uri'] for item in saved_tracks_results['items'] if item['track']]
            # Éviter de sélectionner des titres déjà présents dans les récents ou tops pour la partie "biblio aléatoire"
            eligible_library_tracks = [uri for uri in user_library_track_uris if uri not in recent_tracks_uris and uri not in top_tracks_uris]
            
            selected_count = min(MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY, len(eligible_library_tracks))
            
            
            if selected_count > 0:
                selected_library_tracks = random.sample(eligible_library_tracks, selected_count)
                print(f" - (Biblio) Ajout de {len(selected_library_tracks)} titre(s) aléatoire(s) de la bibliothèque.") # Log simplifié
                # for uri in selected_library_tracks:
                #     try:
                #         track_info = sp.track(uri) # `sp.track` pour obtenir les infos
                #         print(f" - (Biblio) {track_info['name']} par {', '.join([art['name'] for art in track_info['artists']])}")
                #     except Exception as e_log_biblio:
                #         print(f" - (Biblio) Erreur affichage URI {uri}: {e_log_biblio}")
                library_recommendation_uris.extend(selected_library_tracks)
        if not library_recommendation_uris: # Message si la liste est vide
             print("Aucun titre de la bibliothèque ajouté comme recommandation aléatoire.")
             all_uris_to_add.extend(library_recommendation_uris)
             time.sleep(1)

        # --- NOUVELLES RECOMMANDATIONS VIA SOUNDSTAT ---
        soundstat_reco_uris = [] # Liste finale des URIs SoundStat à ajouter à la playlist
        
        # Préparer les seeds pour SoundStat en priorisant les plus récents (cette partie est bonne)
        ordered_potential_seed_uris = []
        seen_uris_for_seed_selection = set()
        for uri in recent_tracks_uris:
            if uri not in seen_uris_for_seed_selection:
                ordered_potential_seed_uris.append(uri)
                seen_uris_for_seed_selection.add(uri)
        if len(ordered_potential_seed_uris) < SOUNDSTAT_SEED_TRACK_COUNT * 2: # Assurer un pool suffisant de seeds potentiels
            for uri in top_tracks_uris:
                if uri not in seen_uris_for_seed_selection:
                    ordered_potential_seed_uris.append(uri)
                    seen_uris_for_seed_selection.add(uri)
        potential_seed_spotify_ids = [uri.split(':')[-1] for uri in ordered_potential_seed_uris]
        
        # Variables pour la boucle SoundStat
        successful_soundstat_seed_calls = 0 # Compteur de seeds qui ont obtenu une réponse (pas une erreur "seed non trouvé")
        # `soundstat_processed_seed_count` remplacé par `successful_soundstat_seed_calls` implicitement
        collected_uris_from_all_soundstat_seeds = [] # Pour stocker toutes les recos de tous les appels

        if potential_seed_spotify_ids:
            print(f"\nRecherche de recommandations SoundStat à partir de {len(potential_seed_spotify_ids)} seeds potentiels (priorité aux récents)...")
            
            seeds_actually_tried_count = 0 # Pour limiter le nombre total de seeds testés si on ne trouve rien

            for seed_id in potential_seed_spotify_ids:
                # Condition d'arrêt 1: Avons-nous fait assez d'appels *fructueux* ?
                if successful_soundstat_seed_calls >= SOUNDSTAT_SEED_TRACK_COUNT:
                    print(f"Limite de {SOUNDSTAT_SEED_TRACK_COUNT} seeds SoundStat interrogés avec succès atteinte.")
                    break 
                
                # Condition d'arrêt 2: Avons-nous déjà collecté énormément de recommandations intermédiaires ?
                # (Sécurité pour ne pas faire trop d'appels si les premiers sont très prolifiques et qu'on a déjà de quoi faire)
                # On vise MAX_SOUNDSTAT_RECOMMENDATIONS au final. Si on a déjà 3* ce nombre, c'est bien.
                if len(collected_uris_from_all_soundstat_seeds) >= MAX_SOUNDSTAT_RECOMMENDATIONS * 3: 
                    print("Volume suffisant de recommandations intermédiaires collecté depuis SoundStat.")
                    break

                # Condition d'arrêt 3: Limiter le nombre total de seeds testés (pour éviter trop d'appels si SoundStat ne connaît aucun de nos N premiers seeds)
                if seeds_actually_tried_count >= SOUNDSTAT_SEED_TRACK_COUNT * 2 and successful_soundstat_seed_calls == 0 : # Ex: essayer jusqu'à 8 seeds si on en veut 4 qui marchent
                     print("Nombre maximum de seeds testés sans succès atteint.")
                     break
                if seeds_actually_tried_count >= len(potential_seed_spotify_ids): # On a épuisé tous les seeds potentiels
                     break


                # Combien de recommandations demander à SoundStat pour ce seed ?
                # Demandons un nombre fixe (ex: 5-10) pour avoir un bon pool de chaque seed qui fonctionne.
                # Le maximum de l'API SoundStat est 100, ne soyons pas excessifs.
                limit_per_api_call = max(5, MAX_SOUNDSTAT_RECOMMENDATIONS + 2) # Demander au moins 5, ou le total désiré + une marge
                limit_per_api_call = min(limit_per_api_call, 15) # Ne pas demander plus de 15 par seed pour rester raisonnable

                seeds_actually_tried_count += 1
                recs_uri_list_from_soundstat = get_soundstat_similar_tracks(
                    api_key=SOUNDSTAT_API_KEY,
                    seed_spotify_track_id=seed_id,
                    limit=limit_per_api_call,
                    genre_match=True 
                )

                # Si get_soundstat_similar_tracks retourne une liste (même vide), cela signifie que le seed a été "accepté"
                # (pas d'erreur HTTP majeure comme "seed non analysé" qui est gérée DANS la fonction).
                # La fonction get_soundstat_similar_tracks retourne [] si le seed n'est pas trouvé/analysé par SoundStat (suite à l'erreur 500 avec message JSON).
                # Donc on compte un appel comme "fructueux" si la fonction ne retourne pas une erreur avant même de faire l'appel
                # ou si elle retourne une liste (même vide, car le seed a été traité).
                # Pour cette logique, on va dire qu'un appel est "fructueux" pour notre compteur si SoundStat retourne des pistes.
                if recs_uri_list_from_soundstat: # Si la liste n'est pas vide, le seed a donné des résultats
                    successful_soundstat_seed_calls += 1
                    print(f"  Seed {seed_id} a retourné {len(recs_uri_list_from_soundstat)} recommandations.")
                    collected_uris_from_all_soundstat_seeds.extend(recs_uri_list_from_soundstat)
                # Si recs_uri_list_from_soundstat est vide (parce que le seed n'a pas été trouvé/analysé ou n'a juste pas de recos),
                # on ne compte pas `successful_soundstat_seed_calls` mais on a bien "essayé" un seed.
            
            if successful_soundstat_seed_calls == 0 and seeds_actually_tried_count > 0:
                print("Aucun des seeds Spotify testés n'a retourné de recommandations de SoundStat.")
            
            # Filtrage final des recommandations collectées pour obtenir la liste soundstat_reco_uris
            existing_uris_to_avoid = set(recent_tracks_uris + top_tracks_uris + library_recommendation_uris)
            
            # Dédoublonner les URIs collectés de SoundStat tout en conservant l'ordre d'apparition
            unique_collected_soundstat_uris = list(dict.fromkeys(collected_uris_from_all_soundstat_seeds))
            
            for uri in unique_collected_soundstat_uris: 
                if len(soundstat_reco_uris) < MAX_SOUNDSTAT_RECOMMENDATIONS: # Si on n'a pas encore atteint le max de recos à ajouter
                    if uri not in existing_uris_to_avoid and uri not in soundstat_reco_uris: # Si c'est nouveau et pas déjà ajouté
                        soundstat_reco_uris.append(uri)
                        # try: 
                        #     track_info = sp.track(uri)
                        #     print(f"  + (SoundStat Reco retenue) {track_info['name']} par {', '.join([art['name'] for art in track_info['artists']])}")
                        # except:
                        #     print(f"  + (SoundStat Reco retenue) URI: {uri} (infos non récupérables sur Spotify)")
                else:
                    break # On a atteint le nombre max de recommandations SoundStat à ajouter
                if soundstat_reco_uris:
                 print(f"  + {len(soundstat_reco_uris)} recommandation(s) SoundStat retenue(s) pour ajout.")
                 
                if len(soundstat_reco_uris) > MAX_SOUNDSTAT_RECOMMENDATIONS:
                    print(f"Plus de {MAX_SOUNDSTAT_RECOMMENDATIONS} recommandations SoundStat uniques trouvées ({len(soundstat_reco_uris)}), sélection aléatoire...")
                    soundstat_reco_uris = random.sample(soundstat_reco_uris, MAX_SOUNDSTAT_RECOMMENDATIONS)
            print(f"Total de {len(soundstat_reco_uris)} recommandations uniques et nouvelles retenues depuis SoundStat après traitement de {successful_soundstat_seed_calls} seed(s) avec succès (et {seeds_actually_tried_count} seeds testés).")

        else: # Si potential_seed_spotify_ids était vide
            print("Aucun titre récent/top disponible pour servir de seed aux recommandations SoundStat.")

        # --- SECTION D'ENTRELACEMENT ---
        all_music_uris = []
        all_music_uris.extend(recent_tracks_uris)
        all_music_uris.extend(top_tracks_uris)
        all_music_uris.extend(library_recommendation_uris)
        all_music_uris.extend(soundstat_reco_uris) # Ajout des recommandations SoundStat

        unique_podcast_uris = list(dict.fromkeys(podcast_episode_uris))
        unique_music_uris = list(dict.fromkeys(all_music_uris)) # Dédoublonnage final de toutes les musiques

        print(f"\nPodcasts uniques à entrelacer: {len(unique_podcast_uris)}")
        print(f"Musiques uniques à entrelacer (total): {len(unique_music_uris)}")

        # ... (Ta logique d'entrelacement, qui était correcte, vient ici) ...
        interlaced_uris = []
        podcast_idx = 0
        music_idx = 0
        while podcast_idx < len(unique_podcast_uris) or music_idx < len(unique_music_uris):
            if podcast_idx < len(unique_podcast_uris):
                uri_to_add = unique_podcast_uris[podcast_idx]
                if uri_to_add not in interlaced_uris: 
                    interlaced_uris.append(uri_to_add)
                podcast_idx += 1
            for _ in range(3):
                if music_idx < len(unique_music_uris):
                    uri_to_add = unique_music_uris[music_idx]
                    if uri_to_add not in interlaced_uris:
                        interlaced_uris.append(uri_to_add)
                    music_idx += 1
                else:
                    break 
        final_unique_uris = interlaced_uris
        
        print(f"\nTotal d'éléments après entrelacement ({len(unique_podcast_uris)} Podcast(s) /  {len(unique_music_uris) }Musique(s)): {len(final_unique_uris)}")
        time.sleep(1)
        
        update_playlist_content(sp, playlist_id, final_unique_uris) # Mise à jour de la playlist
        print(f"--- Mise à jour terminée pour '{PLAYLIST_NAME}' ---")

    except spotipy.SpotifyException as e:
        print(f"Erreur Spotify: {e}")
        if e.http_status == 401: # Unauthorized
            print("Erreur d'authentification. Vérifie tes identifiants et les scopes.")
            print("Il est possible que ton token d'accès ait expiré. Relance le script pour te réauthentifier.")
        elif e.http_status == 403: # Forbidden
            print("Accès refusé. Vérifie que les scopes demandés sont suffisants pour les actions effectuées.")
        elif e.http_status == 429: # Too Many Requests
            print("Trop de requêtes envoyées à l'API Spotify. Attends un peu avant de réessayer.")
        # Tu peux ajouter d'autres codes d'erreur spécifiques au besoin
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")


# --- PLANIFICATION ---
def run_scheduler():
    """Configure et lance le planificateur."""
    # Planifier la tâche pour chaque heure définie
    for t in UPDATE_TIMES:
        schedule.every().day.at(t).do(refresh_daily_playlist)
        print(f"Tâche planifiée tous les jours à {t}")

    print("\nLe script est en attente pour exécuter les tâches planifiées...")
    print("Laisse cette fenêtre de terminal ouverte.")
    print("Appuie sur Ctrl+C pour quitter.")

    while True:
        schedule.run_pending()
        time.sleep(60) # Vérifie toutes les 60 secondes s'il y a une tâche à exécuter

# --- EXÉCUTION ---
if __name__ == '__main__':
    # Remplis tes identifiants avant de lancer !
    if 'TON_CLIENT_ID' in SPOTIPY_CLIENT_ID or 'TON_CLIENT_SECRET' in SPOTIPY_CLIENT_SECRET:
        print("ERREUR: Configure tes SPOTIPY_CLIENT_ID et SPOTIPY_CLIENT_SECRET en haut du script.")
        exit()

    # Pour le premier lancement et pour tester, tu peux appeler la fonction directement :
    refresh_daily_playlist()

    # Une fois que ça fonctionne, tu peux commenter l'appel direct ci-dessus
    # et décommenter run_scheduler() pour le mode planifié :
    # run_scheduler()

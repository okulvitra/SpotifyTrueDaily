import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime
import schedule
import time
import random
import requests
import os

# --- CHARGEMENT DE LA CONFIGURATION ---
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
        exit()

except ImportError:
    print("ERREUR: Fichier de configuration 'config.py' introuvable.")
    print("Veuillez copier 'config_template.py' en 'config.py' et y mettre vos clés API.")
    exit()
except AttributeError as e:
    print(f"ERREUR: Une variable de configuration est manquante dans 'config.py': {e}")
    exit()

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
    "user-read-private" #pour accéder aux données comme la localisation
    # "streaming" # Si tu voulais contrôler la lecture, non nécessaire ici
]

# Heures de mise à jour (format 24h)
UPDATE_TIMES = ["06:00", "22:00"]

# Nombre maximum de chaque type de contenu
MAX_RECENT_TRACKS = 5
MAX_TOP_TRACKS = 5
MAX_PODCAST_EPISODES = 3 # Derniers épisodes pour X podcasts
MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = 3
MAX_NEW_RECOMMENDATIONS = 4 # Nouveautés basées sur les goûts

# --- CONFIGURATION SOUNDSTAT ---
SOUNDSTAT_API_URL = 'https://soundstat.info/api/v1/recommendations/similar'
MAX_SOUNDSTAT_RECOMMENDATIONS = 4 # Nombre de recommandations à demander à SoundStat
SOUNDSTAT_SEED_TRACK_COUNT = 4    # Nombre de tes titres récents/top à utiliser comme seeds pour SoundStat

# --- FONCTIONS SPOTIFY ---

def authenticate_spotify():
    """Authentifie l'utilisateur et retourne un objet Spotify."""
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=" ".join(SCOPES) # Les scopes doivent être une chaîne séparée par des espaces
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    print("Authentification réussie!")
    return sp

def get_or_create_playlist(sp, playlist_name):
    """Récupère l'ID d'une playlist existante ou la crée si elle n'existe pas."""
    user_id = sp.current_user()['id']
    playlists = sp.current_user_playlists(limit=50)
    target_playlist_id = None

    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            target_playlist_id = playlist['id']
            print(f"Playlist '{playlist_name}' trouvée avec l'ID: {target_playlist_id}")
            break

    if not target_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=f"Votre playlist {playlist_name} auto-générée.")
        target_playlist_id = new_playlist['id']
        print(f"Playlist '{playlist_name}' créée avec l'ID: {target_playlist_id}")

    return target_playlist_id

def get_recent_tracks_uris(sp, limit=5):
    """Récupère les URIs des titres écoutés récemment."""
    results = sp.current_user_recently_played(limit=limit)
    track_uris = []
    print(f"\n--- Titres Récents (max {limit}) ---")
    for item in results['items']:
        track = item['track']
        if track and track['uri'] not in track_uris: # Éviter les doublons si écouté plusieurs fois de suite
             print(f" - {track['name']} par {', '.join([artist['name'] for artist in track['artists']])}")
             track_uris.append(track['uri'])
    return track_uris

def get_top_tracks_uris(sp, limit=5, time_range='short_term'):
    """Récupère les URIs des titres les plus écoutés (short_term, medium_term, long_term)."""
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    track_uris = []
    print(f"\n--- Top Titres ({time_range}, max {limit}) ---")
    for track in results['items']:
        if track and track['uri'] not in track_uris:
            print(f" - {track['name']} par {', '.join([artist['name'] for artist in track['artists']])}")
            track_uris.append(track['uri'])
    return track_uris

def get_saved_shows_latest_episodes_uris(sp, limit_shows=3, market=None):
    """
    Récupère les derniers épisodes des podcasts (émissions) sauvegardés par l'utilisateur.
    """
    print(f"\n--- Derniers Épisodes des Podcasts Sauvegardés (max {limit_shows} émissions) ---")
    user_country = market or sp.current_user()['country']
    saved_shows_results = sp.current_user_saved_shows(limit=limit_shows) # Récupère les émissions les plus récemment sauvegardées/suivies
    
    episode_uris = []
    
    if not saved_shows_results['items']:
        print("Aucune émission de podcast sauvegardée/suivie trouvée.")
        return episode_uris

    for item in saved_shows_results['items']:
        show = item['show']
        show_id = show['id']
        show_name = show['name']
        
        try:
            # Récupérer le dernier épisode de cette émission
            # Certains podcasts peuvent ne pas être disponibles dans tous les marchés, d'où l'importance du 'market'
            show_episodes = sp.show_episodes(show_id, limit=1, market=user_country) 
            if show_episodes['items']:
                latest_episode = show_episodes['items'][0]
                if latest_episode['uri'] not in episode_uris: # Éviter doublons si jamais
                    print(f" - Émission: {show_name} - Dernier épisode: {latest_episode['name']}")
                    episode_uris.append(latest_episode['uri'])
            else:
                print(f" - Aucun épisode trouvé pour l'émission sauvegardée: {show_name} (peut-être pas d'épisode récent ou problème de marché).")
        except Exception as e:
            print(f"Erreur en récupérant les épisodes de {show_name}: {e}")
            # Si une émission spécifique pose problème, on continue avec les suivantes
            
    if not episode_uris:
        print("Aucun dernier épisode récupérable pour les émissions sauvegardées.")
        
    return episode_uris


# def get_recommendations_uris(sp, seed_tracks, seed_artists, limit_library=3, limit_new=3, market=None):

    """
    Récupère des recommandations :
    - Un mix de titres aléatoires de la bibliothèque de l'utilisateur.
    - Des propositions basées sur les goûts (artistes/titres récents/tops ou genres).
    """
    recommendation_uris = []
    user_country = market or sp.current_user()['country']

    # 1. Titres aléatoires de la bibliothèque
    print(f"\n--- Recommandations Aléatoires de la Bibliothèque (max {limit_library}) ---")
    saved_tracks_results = sp.current_user_saved_tracks(limit=50)
    
    # Récupérer les URIs des titres sauvegardés pour les exclure des "nouvelles" recommandations plus tard
    # Et pour pouvoir sélectionner aléatoirement dedans.
    user_library_track_uris = []
    if saved_tracks_results and saved_tracks_results['items']:
        user_library_track_uris = [item['track']['uri'] for item in saved_tracks_results['items'] if item['track']]

    if user_library_track_uris:
        eligible_library_tracks = [uri for uri in user_library_track_uris if uri not in seed_tracks] # Évite de recommander ce qui est déjà dans récents/tops
        
        if len(eligible_library_tracks) > limit_library:
            selected_library_tracks = random.sample(eligible_library_tracks, limit_library)
        else:
            selected_library_tracks = eligible_library_tracks
        
        for uri in selected_library_tracks:
            try: # Ajout d'un try-except pour l'affichage
                track_info = sp.track(uri)
                print(f" - (Biblio) {track_info['name']} par {', '.join([artist['name'] for artist in track_info['artists']])}")
            except Exception as e:
                print(f" - (Biblio) Erreur d'affichage pour URI {uri}: {e}")
        recommendation_uris.extend(selected_library_tracks)
    else:
        print("Aucun titre trouvé dans la bibliothèque pour des recommandations aléatoires.")

    # 2. Nouvelles propositions basées sur les goûts
    print(f"\n--- Nouvelles Recommandations (max {limit_new}) ---")
    
      # --- DÉBUT DU BLOC DE DIAGNOSTIC DÉTAILLÉ ---
    print("\n--- DIAGNOSTIC DÉTAILLÉ RECOMMANDATIONS ---")
    # Assure-toi que user_country est défini (il l'est normalement au début de get_recommendations_uris)
    # user_country = market or sp.current_user()['country'] # Déjà fait plus haut dans la fonction

    # Test 1: Seed avec un genre commun
    print("\nDIAGNOSTIC TEST 1: Seed avec genre 'pop'")
    try:
        # Tentative SANS le paramètre market d'abord
        print("  Test genre 'pop' SANS marché explicite...")
        diag_recs_genre_no_market = sp.recommendations(seed_genres=['pop'], limit=1)
        if diag_recs_genre_no_market and diag_recs_genre_no_market['tracks']:
            print(f"    RÉUSSI (sans marché): Piste (pop): {diag_recs_genre_no_market['tracks'][0]['name']}")
        elif diag_recs_genre_no_market:
            print("    RÉUSSI (appel OK, sans marché) mais aucune piste retournée pour 'pop'.")
        else:
            print("    ÉCHEC (sans marché): Aucune donnée retournée pour seed_genres=['pop'].")
    except spotipy.SpotifyException as e:
        print(f"    ÉCHEC (SpotifyException, sans marché): {e.msg}")
    except Exception as e:
        print(f"    ÉCHEC (Exception générale, sans marché): {e}")

    print(f"\n  Test genre 'pop' AVEC marché '{user_country}'...")
    try:
        diag_recs_genre_with_market = sp.recommendations(seed_genres=['pop'], limit=1, market=user_country)
        if diag_recs_genre_with_market and diag_recs_genre_with_market['tracks']:
            print(f"    RÉUSSI (avec marché): Piste (pop): {diag_recs_genre_with_market['tracks'][0]['name']}")
        elif diag_recs_genre_with_market:
            print("    RÉUSSI (appel OK, avec marché) mais aucune piste retournée pour 'pop'.")
        else:
            print("    ÉCHEC (avec marché): Aucune donnée retournée pour seed_genres=['pop'].")
    except spotipy.SpotifyException as e:
        print(f"    ÉCHEC (SpotifyException, avec marché): {e.msg}")
    except Exception as e:
        print(f"    ÉCHEC (Exception générale, avec marché): {e}")


    # Test 2: Seed avec un titre (utilise le premier URI de seed_tracks si disponible)
    print("\nDIAGNOSTIC TEST 2: Seed avec un titre")
    if seed_tracks: # seed_tracks est un paramètre de get_recommendations_uris
        test_track_seed_uri = seed_tracks[0]
        print(f"  Utilisation du seed titre: {test_track_seed_uri} avec marché '{user_country}'")
        try:
            diag_recs_track = sp.recommendations(seed_tracks=[test_track_seed_uri], limit=1, market=user_country)
            if diag_recs_track and diag_recs_track['tracks']:
                print(f"    RÉUSSI: Piste (seed titre): {diag_recs_track['tracks'][0]['name']}")
            elif diag_recs_track:
                print("    RÉUSSI (appel OK) mais aucune piste retournée pour ce seed titre.")
            else:
                print(f"    ÉCHEC: Aucune donnée retournée pour seed_tracks=['{test_track_seed_uri}'].")
        except spotipy.SpotifyException as e:
            print(f"    ÉCHEC (SpotifyException): {e.msg}")
        except Exception as e:
            print(f"    ÉCHEC (Exception générale): {e}")
    else:
        print("  PAS DE SEED TITRE (seed_tracks) disponible pour ce test.")

    # Test 3: Seed avec un artiste (utilise le premier URI de seed_artists si disponible)
    print("\nDIAGNOSTIC TEST 3: Seed avec un artiste")
    if seed_artists: # seed_artists est un paramètre de get_recommendations_uris
        test_artist_seed_uri = seed_artists[0]
        print(f"  Utilisation du seed artiste: {test_artist_seed_uri} avec marché '{user_country}'")
        try:
            diag_recs_artist = sp.recommendations(seed_artists=[test_artist_seed_uri], limit=1, market=user_country)
            if diag_recs_artist and diag_recs_artist['tracks']:
                print(f"    RÉUSSI: Piste (seed artiste): {diag_recs_artist['tracks'][0]['name']}")
            elif diag_recs_artist:
                print("    RÉUSSI (appel OK) mais aucune piste retournée pour ce seed artiste.")
            else:
                print(f"    ÉCHEC: Aucune donnée retournée pour seed_artists=['{test_artist_seed_uri}'].")
        except spotipy.SpotifyException as e:
            print(f"    ÉCHEC (SpotifyException): {e.msg}")
        except Exception as e:
            print(f"    ÉCHEC (Exception générale): {e}")
    else:
        print("  PAS DE SEED ARTISTE (seed_artists) disponible pour ce test.")

    print("--- FIN DU BLOC DE DIAGNOSTIC DÉTAILLÉ ---\n")
    current_seed_tracks_for_api = list(set(seed_tracks))[:2] # URIs des titres
    current_seed_artists_for_api = list(set(seed_artists))[:2] # URIs des artistes
    
    new_recommendations_added_count = 0
    attempted_with_tracks_artists = False

    # Tentative 1: Basée sur les titres et artistes récents/tops
    if current_seed_tracks_for_api or current_seed_artists_for_api:
        attempted_with_tracks_artists = True
        print(f"Tentative de recommandations avec : Artistes = {current_seed_artists_for_api}, Titres = {current_seed_tracks_for_api}, Marché = {user_country}")
        try:
            recs = sp.recommendations(
                seed_tracks=current_seed_tracks_for_api if current_seed_tracks_for_api else None,
                seed_artists=current_seed_artists_for_api if current_seed_artists_for_api else None,
                limit=limit_new + 5, 
                market=user_country
            )
            if recs and recs['tracks']:
                for track in recs['tracks']:
                    if track and track['uri'] not in recommendation_uris and track['uri'] not in seed_tracks and track['uri'] not in user_library_track_uris: # Évite doublons avec biblio, seeds initiaux
                        print(f" - (Nouveau S/A) {track['name']} par {', '.join([artist['name'] for artist in track['artists']])}")
                        recommendation_uris.append(track['uri'])
                        new_recommendations_added_count += 1
                        if new_recommendations_added_count >= limit_new:
                            break
                if new_recommendations_added_count == 0:
                    print("Aucune nouvelle recommandation unique (non-biblio, non-seed) trouvée avec les seeds Artistes/Titres.")
            else:
                print("Aucune piste retournée par l'API de recommandations avec les seeds Artistes/Titres.")
        except spotipy.SpotifyException as e:
            print(f"Erreur Spotipy lors de la récupération des nouvelles recommandations (Artistes/Titres): {e.msg}") # Utiliser e.msg pour un message plus clair
            if e.http_status == 400:
                 print("   Cela peut être dû à des seeds Artistes/Titres invalides ou à une combinaison non supportée.")
            elif e.http_status == 404: # Ne devrait pas arriver si l'endpoint est bon, mais au cas où
                 print("   L'endpoint de recommandation (Artistes/Titres) n'a pas été trouvé.")
            # Pas d'autres messages spécifiques ici, l'erreur principale est déjà affichée.
        except Exception as e:
             print(f"Erreur générale non-Spotipy lors de la récupération des nouvelles recommandations (Artistes/Titres): {e}")

    # Tentative 2 (Fallback): Basée sur les genres, si la première tentative n'a pas fourni assez de recommandations
    if new_recommendations_added_count < limit_new:
        if attempted_with_tracks_artists: # Si on a déjà tenté avec tracks/artists
            print("\nFallback aux genres car la méthode Artistes/Titres n'a pas fourni assez de recommandations.")
        else: # Si on n'avait aucun seed track/artist au départ
            print("\nAucun seed Artiste/Titre disponible, tentative de recommandations basée sur les genres.")
        try:
            top_artists_genres = []
            top_artists_full = sp.current_user_top_artists(limit=5, time_range='medium_term') # Genres des artistes favoris
            if top_artists_full and top_artists_full['items']:
                for artist in top_artists_full['items']:
                    top_artists_genres.extend(artist['genres'])
                
                seed_genres_for_api = list(set(top_artists_genres))[:3] # Max 3 genres pour laisser de la place à d'autres types de seeds si besoin un jour

                if seed_genres_for_api:
                    print(f"Utilisation des genres seeds: {seed_genres_for_api}, Marché = {user_country}")
                    # On veut compléter jusqu'à `limit_new` recommandations
                    needed_recs_from_genres = limit_new - new_recommendations_added_count
                    if needed_recs_from_genres > 0:
                        recs_genre = sp.recommendations(seed_genres=seed_genres_for_api, limit=needed_recs_from_genres + 5, market=user_country)
                        if recs_genre and recs_genre['tracks']:
                            for track in recs_genre['tracks']:
                                if track and track['uri'] not in recommendation_uris and track['uri'] not in seed_tracks and track['uri'] not in user_library_track_uris:
                                    print(f" - (Nouveau/Genre) {track['name']} par {', '.join([artist['name'] for artist in track['artists']])}")
                                    recommendation_uris.append(track['uri'])
                                    new_recommendations_added_count += 1 # Compteur global de nouvelles recommandations
                                    if new_recommendations_added_count >= limit_new:
                                        break
                            if new_recommendations_added_count < limit_new and (needed_recs_from_genres > 0 and not any(t for t in recs_genre['tracks'] if t and t['uri'] not in recommendation_uris and t['uri'] not in seed_tracks and t['uri'] not in user_library_track_uris)): # Si on voulait des recos par genre mais on n'en a pas eu de nouvelles
                                print("Aucune nouvelle recommandation unique (non-biblio, non-seed) trouvée avec les genres.")
                        else:
                            print("Aucune piste retournée par l'API de recommandations avec les genres.")
                    else:
                        print("Nombre de nouvelles recommandations souhaitées déjà atteint avant le fallback par genres.")
                else:
                    print("Aucun genre trouvé à partir des artistes favoris pour les recommandations par genre.")
            else:
                print("Impossible de récupérer les top artistes pour obtenir des genres seeds.")
        except spotipy.SpotifyException as fallback_e:
            print(f"Erreur Spotipy lors de la tentative de recommandations par genre: {fallback_e.msg}")
        except Exception as fallback_e:
            print(f"Erreur générale lors de la tentative de recommandations par genre: {fallback_e}")
            
    if new_recommendations_added_count == 0 and not any(uri in user_library_track_uris for uri in recommendation_uris): # Si vraiment rien de neuf et rien de la biblio
        print("Aucune nouvelle recommandation n'a pu être ajoutée (ni par seeds Artistes/Titres, ni par Genres).")

    return recommendation_uris

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
    print(f"\n--- Mise à jour de la playlist '{PLAYLIST_NAME}' ---")
    try:
        # D'abord, vider la playlist
        sp.playlist_replace_items(playlist_id, []) # Envoie une liste vide pour tout supprimer
        print(f"Playlist '{PLAYLIST_NAME}' vidée.")
        
        # Ensuite, ajouter les nouveaux items par lots de 100 maximum
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i + 100]
            sp.playlist_add_items(playlist_id, batch)
        print(f"{len(track_uris)} éléments ajoutés à la playlist '{PLAYLIST_NAME}'.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la playlist '{PLAYLIST_NAME}': {e}")
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
        playlist_id = get_or_create_playlist(sp, PLAYLIST_NAME)

        # Collecte des contenus
        all_uris_to_add = []

        # 1. Podcasts (derniers épisodes)
        # Note: l'ordre d'ajout est important si tu veux les podcasts en premier
        podcast_episode_uris = get_saved_shows_latest_episodes_uris(sp, limit_shows=MAX_PODCAST_EPISODES, market=sp.current_user()['country'])
        all_uris_to_add.extend(podcast_episode_uris)

        # 2. Musiques basées sur les écoutes
        recent_tracks_uris = get_recent_tracks_uris(sp, limit=MAX_RECENT_TRACKS)
        all_uris_to_add.extend(recent_tracks_uris)

        top_tracks_uris = get_top_tracks_uris(sp, limit=MAX_TOP_TRACKS, time_range='short_term') # 'short_term', 'medium_term', 'long_term'
        all_uris_to_add.extend(top_tracks_uris)
        
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
                for uri in selected_library_tracks:
                    try:
                        track_info = sp.track(uri) # `sp.track` pour obtenir les infos
                        print(f" - (Biblio) {track_info['name']} par {', '.join([art['name'] for art in track_info['artists']])}")
                    except Exception as e_log_biblio:
                        print(f" - (Biblio) Erreur affichage URI {uri}: {e_log_biblio}")
                library_recommendation_uris.extend(selected_library_tracks)
        if not library_recommendation_uris: # Message si la liste est vide
             print("Aucun titre de la bibliothèque ajouté comme recommandation aléatoire.")

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
                        try: 
                            track_info = sp.track(uri)
                            print(f"  + (SoundStat Reco retenue) {track_info['name']} par {', '.join([art['name'] for art in track_info['artists']])}")
                        except:
                            print(f"  + (SoundStat Reco retenue) URI: {uri} (infos non récupérables sur Spotify)")
                else:
                    break # On a atteint le nombre max de recommandations SoundStat à ajouter
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
        
        print(f"\nTotal d'éléments après entrelacement (1 Podcast / 3 Musiques): {len(final_unique_uris)}")
        if final_unique_uris:
            print("Premiers éléments de la playlist entrelacée (vérification) :")
            # ... (Ta boucle de log pour les 10 premiers éléments, qui était correcte, vient ici) ...
            for i, uri in enumerate(final_unique_uris[:10]):
                try:
                    item_name = "Non trouvé"
                    item_type = "Inconnu"
                    if "spotify:episode:" in uri:
                        item = sp.episode(uri) 
                        item_type = "Épisode"
                        if item: item_name = item['name']
                    elif "spotify:track:" in uri:
                        item = sp.track(uri)
                        item_type = "Musique"
                        if item: item_name = item['name']
                    print(f"  {i+1}. ({item_type}) {item_name}")
                except Exception as e_log:
                    print(f"  {i+1}. URI: {uri} - Erreur récupération info pour log: {e_log}")
        
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
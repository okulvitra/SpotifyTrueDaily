import customtkinter as ctk
import tkinter as tk # Ajout de l'import pour tk.TclError
import threading
import sys
import os
import importlib
import time
import traceback

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILENAME = os.path.join(application_path, "config.py")

class ConfigError(Exception):
    """Exception personnalisée pour les erreurs de configuration."""
    pass

playlist_manager_module = None

try:
    from playlist_manager import ConfigError as PM_ConfigError
    import playlist_manager as pm
    playlist_manager_module = pm
except ConfigError as e:
    print(f"ERREUR (GUI): Problème de configuration détecté: {e}")
    print("L'application va démarrer. Veuillez vérifier/sauvegarder la configuration via l'onglet 'Settings'.")
except ImportError as e_imp:
    if "playlist_manager" in str(e_imp).lower():
        try:
            root_temp = ctk.CTk()
            root_temp.withdraw()
            # Remplacement de CTkMessagebox par une popup personnalisée
            dialog = ctk.CTkToplevel(root_temp)
            dialog.title("Erreur Critique")
            dialog.geometry("400x200")
            label = ctk.CTkLabel(dialog, text="Le fichier 'playlist_manager.py' est introuvable.\nAssurez-vous qu'il est dans le même dossier que app_gui.py.", wraplength=380)
            label.pack(padx=10, pady=10)
            button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
            button.pack(pady=10)
            dialog.grab_set()
            dialog.focus_set()
            root_temp.wait_window(dialog)
            root_temp.destroy()
        except Exception as e:
            print(f"ERREUR CRITIQUE: Le fichier 'playlist_manager.py' est introuvable. Détails: {e}")
        sys.exit(f"Dépendance 'playlist_manager.py' manquante: {e_imp}")
    else:
        print(f"Erreur d'importation inattendue: {e_imp}")
        sys.exit(1)

DEFAULT_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
DEFAULT_CONTENT_SETTINGS_GUI = {
    "MAX_RECENT_TRACKS": 5,
    "MAX_TOP_TRACKS": 5,
    "MAX_PODCAST_EPISODES": 3,
    "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": 2,
    "MAX_SOUNDSTAT_RECOMMENDATIONS": 3,
    "SOUNDSTAT_SEED_TRACK_COUNT": 2
}

def load_config_values_from_file():
    print("Chargement de la configuration depuis le fichier...")
    config_vals = {
        "SPOTIPY_CLIENT_ID": "",
        "SPOTIPY_CLIENT_SECRET": "",
        "SPOTIPY_REDIRECT_URI": DEFAULT_REDIRECT_URI,
        "SOUNDSTAT_API_KEY": "",
        **DEFAULT_CONTENT_SETTINGS_GUI
    }
    try:
        if os.path.exists(CONFIG_FILENAME):
            with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value_part = line.split('=', 1)
                        key = key.strip()
                        value_part = value_part.strip()
                        if (value_part.startswith("'") and value_part.endswith("'")) or \
                           (value_part.startswith('"') and value_part.endswith('"')):
                            value_part = value_part[1:-1]
                        if key in config_vals:
                            if key.startswith("MAX_") or key == "SOUNDSTAT_SEED_TRACK_COUNT":
                                try:
                                    config_vals[key] = int(value_part)
                                except ValueError:
                                    print(f"Avertissement: Valeur non numérique pour {key} dans {CONFIG_FILENAME}. Utilisation de la valeur par défaut {DEFAULT_CONTENT_SETTINGS_GUI.get(key)}.")
                                    config_vals[key] = DEFAULT_CONTENT_SETTINGS_GUI.get(key)
                            else:
                                config_vals[key] = value_part
        else:
            print(f"Note: Le fichier {CONFIG_FILENAME} n'existe pas. Les valeurs par défaut seront utilisées.")
            for key_default, val_default in DEFAULT_CONTENT_SETTINGS_GUI.items():
                if key_default not in config_vals:
                    config_vals[key_default] = val_default
    except Exception as e:
        print(f"Erreur en lisant {CONFIG_FILENAME}: {e}. Utilisation des valeurs par défaut.")
        config_vals.update(DEFAULT_CONTENT_SETTINGS_GUI)
    return config_vals

def save_config_values_to_file(config_data, app_instance=None):
    print("Sauvegarde de la configuration dans le fichier...")
    content = f"""# config.py - VOS INFORMATIONS CONFIDENTIELLES ET PRÉFÉRENCES
# Ce fichier est généré par l'application SpotifyTrueDaily.
# Configuration Spotify
SPOTIPY_CLIENT_ID = '{config_data.get("SPOTIPY_CLIENT_ID", "")}'
SPOTIPY_CLIENT_SECRET = '{config_data.get("SPOTIPY_CLIENT_SECRET", "")}'
SPOTIPY_REDIRECT_URI = '{config_data.get("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI)}'
# Configuration SoundStat
SOUNDSTAT_API_KEY = '{config_data.get("SOUNDSTAT_API_KEY", "")}'
# Paramètres de contenu de la Playlist Journalière
MAX_RECENT_TRACKS = {int(config_data.get("MAX_RECENT_TRACKS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_RECENT_TRACKS"]))}
MAX_TOP_TRACKS = {int(config_data.get("MAX_TOP_TRACKS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_TOP_TRACKS"]))}
MAX_PODCAST_EPISODES = {int(config_data.get("MAX_PODCAST_EPISODES", DEFAULT_CONTENT_SETTINGS_GUI["MAX_PODCAST_EPISODES"]))}
MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = {int(config_data.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY", DEFAULT_CONTENT_SETTINGS_GUI["MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"]))}
MAX_SOUNDSTAT_RECOMMENDATIONS = {int(config_data.get("MAX_SOUNDSTAT_RECOMMENDATIONS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_SOUNDSTAT_RECOMMENDATIONS"]))}
SOUNDSTAT_SEED_TRACK_COUNT = {int(config_data.get("SOUNDSTAT_SEED_TRACK_COUNT", DEFAULT_CONTENT_SETTINGS_GUI["SOUNDSTAT_SEED_TRACK_COUNT"]))}
"""
    try:
        # Vérifier les permissions d'écriture
        if not os.access(os.path.dirname(CONFIG_FILENAME), os.W_OK):
            raise PermissionError(f"Pas de permission d'écriture dans le répertoire {os.path.dirname(CONFIG_FILENAME)}")

        with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            f.write(content)
        if app_instance:
            app_instance.show_info("Settings", f"Configuration sauvegardée dans {CONFIG_FILENAME} !\n\n"
                                          "Les nouveaux paramètres seront utilisés au prochain lancement de la mise à jour.")
    except PermissionError as e:
        if app_instance:
            app_instance.show_error("Erreur de sauvegarde", f"Permission refusée pour écrire dans le fichier de configuration : {e}")
    except Exception as e:
        if app_instance:
            app_instance.show_error("Erreur de sauvegarde", f"Impossible de sauvegarder la configuration : {e}")

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_):
        if self.widget.winfo_exists():
            self.widget.configure(state='normal')
            self.widget.insert(ctk.END, str_)
            self.widget.see(ctk.END)
            self.widget.configure(state='disabled')

    def flush(self):
        pass

class SpotifyTrueDailyApp:
    def __init__(self, root_window):
        print("Initialisation de l'application...")
        self.root = root_window
        self.root.title("SpotifyTrueDaily v1.0 by okulvitra")
        self.root.geometry("800x650")
        self.root.minsize(700, 550)

        try:
            print("Création de l'interface graphique...")
            self.notebook = ctk.CTkTabview(self.root)
            self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

            # Ajout des onglets et récupération de leurs frames
            self.tab_application = self.notebook.add("  Application  ")
            self.tab_settings = self.notebook.add("  Settings  ")

            self.initial_config = load_config_values_from_file()
            self.setup_application_tab()
            self.setup_settings_tab()

            # Remplacement de bd et relief par fg_color et corner_radius
            self.footer = ctk.CTkLabel(self.root, text="Copyright @ okulvitra - 2025",
                                      fg_color="gray20", corner_radius=5)
            self.footer.pack(side=ctk.BOTTOM, fill=ctk.X, padx=5, pady=5)

            self.redirect_logging()

            print("Interface graphique initialisée.\n"
                  "Ajustez les quantités dans l'onglet 'Application' pour cette exécution.\n"
                  "Sauvegardez les clés API et les valeurs par défaut dans 'Settings'.\n"
                  "La première authentification Spotify ouvrira votre navigateur.\n")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de l'interface graphique: {e}")
            traceback.print_exc()

    def show_error(self, title, message):
        try:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(title)
            dialog.geometry("400x200")

            label = ctk.CTkLabel(dialog, text=message, wraplength=380)
            label.pack(padx=10, pady=10)

            button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
            button.pack(pady=10)

            dialog.grab_set()
            dialog.focus_set()
            self.root.wait_window(dialog)
        except Exception as e:
            print(f"Erreur lors de l'affichage de la boîte de dialogue d'erreur: {e}")
            traceback.print_exc()

    def show_info(self, title, message):
        try:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(title)
            dialog.geometry("400x200")

            label = ctk.CTkLabel(dialog, text=message, wraplength=380)
            label.pack(padx=10, pady=10)

            button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
            button.pack(pady=10)

            dialog.grab_set()
            dialog.focus_set()
            self.root.wait_window(dialog)
        except Exception as e:
            print(f"Erreur lors de l'affichage de la boîte de dialogue d'information: {e}")
            traceback.print_exc()

    def redirect_logging(self):
        try:
            sys.stdout = TextRedirector(self.log_area, "stdout")
            sys.stderr = TextRedirector(self.log_area, "stderr")
            # NOTE: CTkTextbox ne semble pas supporter tag_configure comme Tkinter Text.
            # La coloration différente de stderr ne sera donc pas appliquée.
            # self.log_area.tag_configure("stderr", foreground="red") # Ligne supprimée
        except Exception as e:
            print(f"Erreur lors de la redirection des logs: {e}")
            traceback.print_exc()

    def setup_application_tab(self):
        try:
            print("Configuration de l'onglet Application...")
            frame_app = self.tab_application
            content_params_frame = ctk.CTkFrame(frame_app)
            content_params_frame.pack(pady=(0, 10), fill=ctk.X, side=ctk.TOP)

            # Utiliser StringVar pour éviter les erreurs Tcl avec IntVar
            # S'assurer que les valeurs pour StringVar soient des chaînes
            self.max_recent_var = ctk.StringVar(value=str(self.initial_config.get("MAX_RECENT_TRACKS")))
            self.max_top_var = ctk.StringVar(value=str(self.initial_config.get("MAX_TOP_TRACKS")))
            self.max_podcasts_var = ctk.StringVar(value=str(self.initial_config.get("MAX_PODCAST_EPISODES")))
            self.max_library_var = ctk.StringVar(value=str(self.initial_config.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY")))
            self.max_soundstat_recos_var = ctk.StringVar(value=str(self.initial_config.get("MAX_SOUNDSTAT_RECOMMENDATIONS")))
            self.soundstat_seed_count_var = ctk.StringVar(value=str(self.initial_config.get("SOUNDSTAT_SEED_TRACK_COUNT")))

            fields_app_tab = [
                ("Titres Récents:", self.max_recent_var),
                ("Top Titres:", self.max_top_var),
                ("Épisodes de Podcast:", self.max_podcasts_var),
                ("Recos Bibliothèque:", self.max_library_var),
                ("Recos SoundStat:", self.max_soundstat_recos_var),
                ("Seeds pour SoundStat:", self.soundstat_seed_count_var)
            ]

            for i, (text, var) in enumerate(fields_app_tab):
                label = ctk.CTkLabel(content_params_frame, text=text)
                label.grid(row=i, column=0, sticky='w', padx=5, pady=3)
                entry = ctk.CTkEntry(content_params_frame, textvariable=var, width=50)
                entry.grid(row=i, column=1, sticky='w', padx=5, pady=3)

            disclaimer_label = ctk.CTkLabel(content_params_frame,
                                            text="Note: Des valeurs élevées (ex: >10 par catégorie) peuvent augmenter\n"
                                                 "le risque de dépasser les limites d'appels API de Spotify.",
                                            font=('TkDefaultFont', 8, 'italic'))
            disclaimer_label.grid(row=len(fields_app_tab), column=0, columnspan=2, pady=(8, 0), sticky='w')

            button_frame = ctk.CTkFrame(frame_app)
            button_frame.pack(pady=15, side=ctk.TOP)

            self.start_button = ctk.CTkButton(button_frame, text="Start Playlist Update", command=self.on_start_button_click)
            self.start_button.pack()

            log_frame = ctk.CTkFrame(frame_app)
            log_frame.pack(padx=5, pady=(5, 5), expand=True, fill='both', side=ctk.TOP)

            self.log_area = ctk.CTkTextbox(log_frame, wrap="word", state="disabled", height=100)
            self.log_area.pack(expand=True, fill='both')
        except Exception as e:
            print(f"Erreur lors de la configuration de l'onglet Application: {e}")
            traceback.print_exc()

    def _safe_get_int_var(self, var, default=0):
        """Récupère la valeur d'une StringVar (représentant un entier) en toute sécurité."""
        try:
            val_str = var.get()
            if val_str == "":
                return default
            return int(val_str)
        except (ValueError, tk.TclError): # ValueError pour int(), TclError pour var.get()
            print(f"Avertissement: Valeur invalide '{var.get()}' dans un champ, utilisation de {default}.")
            return default

    def on_start_button_click(self):
        try:
            # Utiliser _safe_get_int_var pour convertir les StringVar en int
            run_time_config = {
                "MAX_RECENT_TRACKS": self._safe_get_int_var(self.max_recent_var),
                "MAX_TOP_TRACKS": self._safe_get_int_var(self.max_top_var),
                "MAX_PODCAST_EPISODES": self._safe_get_int_var(self.max_podcasts_var),
                "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": self._safe_get_int_var(self.max_library_var),
                "MAX_SOUNDSTAT_RECOMMENDATIONS": self._safe_get_int_var(self.max_soundstat_recos_var),
                "SOUNDSTAT_SEED_TRACK_COUNT": self._safe_get_int_var(self.soundstat_seed_count_var)
            }
            self.run_playlist_update_thread(run_time_config)
        except Exception as e:
            print(f"Erreur lors du clic sur le bouton Start: {e}")
            traceback.print_exc()

    def run_playlist_update_thread(self, run_time_config):
        try:
            self.start_button.configure(state="disabled", text="Mise à jour en cours...")
            self.log_area.configure(state='normal')
            self.log_area.delete('1.0', ctk.END)
            self.log_area.configure(state='disabled')
            print(f"[{time.strftime('%H:%M:%S')}] Lancement de la mise à jour de la playlist avec les paramètres actuels...\n")
            thread = threading.Thread(target=self.execute_playlist_update, args=(run_time_config,), daemon=True)
            thread.start()
        except Exception as e:
            print(f"Erreur lors du lancement du thread de mise à jour: {e}")
            traceback.print_exc()

    def execute_playlist_update(self, run_config_for_this_execution):
        global playlist_manager_module
        try:
            if 'config' in sys.modules:
                importlib.reload(sys.modules['config'])
            if 'playlist_manager' in sys.modules and playlist_manager_module is not None:
                playlist_manager_module = importlib.reload(playlist_manager_module)
            elif playlist_manager_module is None:
                from playlist_manager import ConfigError as PM_ConfigError_reload
                import playlist_manager as pm_reloaded
                playlist_manager_module = pm_reloaded
            if playlist_manager_module is None:
                raise RuntimeError("Le module playlist_manager n'a pas pu être chargé.")

            print("Application des paramètres de contenu pour cette exécution :")
            for key, value in run_config_for_this_execution.items():
                if hasattr(playlist_manager_module, key):
                    setattr(playlist_manager_module, key, value)
                    print(f"  {key} = {value}")
                else:
                    print(f"  Avertissement (GUI): La constante {key} n'existe pas dans playlist_manager.py.")

            playlist_manager_module.refresh_daily_playlist()
            print(f"\n[{time.strftime('%H:%M:%S')}] --- Mise à jour terminée (depuis la GUI) ---")
        except PM_ConfigError as e_conf:
            error_title = "Erreur de Configuration"
            error_message = (f"La mise à jour n'a pas pu démarrer à cause d'une erreur de configuration:\n\n{e_conf}\n\n"
                             "Veuillez vérifier vos clés API dans l'onglet 'Settings' et sauvegarder.")
            self.show_error(error_title, error_message)
            print(f"ERREUR DE CONFIGURATION (GUI): {e_conf}")
        except AttributeError as e_attr:
            self.show_error("Erreur d'application", f"Fonctionnalité non trouvée ou erreur interne: {e_attr}")
            print(f"ERREUR D'ATTRIBUT (GUI): {e_attr}")
        except Exception as e_exec:
            self.show_error("Erreur d'exécution", f"Une erreur est survenue pendant la mise à jour : {e_exec}")
            print(f"ERREUR PENDANT L'EXÉCUTION (GUI): {e_exec}")
            traceback.print_exc()
        finally:
            if hasattr(self, 'start_button') and self.start_button.winfo_exists():
                self.start_button.configure(state="normal", text="Start Playlist Update")

    def setup_settings_tab(self):
        try:
            print("Configuration de l'onglet Settings...")
            frame_settings = self.tab_settings
            self.current_config_for_settings = load_config_values_from_file()

            spotify_frame = ctk.CTkFrame(frame_settings)
            spotify_frame.pack(fill=ctk.X, padx=5, pady=(5, 0))

            ctk.CTkLabel(spotify_frame, text="Client ID Spotify:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
            self.spotify_client_id_var = ctk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_CLIENT_ID", ""))
            self.spotify_client_id_entry = ctk.CTkEntry(spotify_frame, textvariable=self.spotify_client_id_var, width=200, show="*")
            self.spotify_client_id_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

            ctk.CTkLabel(spotify_frame, text="Client Secret Spotify:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
            self.spotify_client_secret_var = ctk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_CLIENT_SECRET", ""))
            self.spotify_client_secret_entry = ctk.CTkEntry(spotify_frame, textvariable=self.spotify_client_secret_var, width=200, show="*")
            self.spotify_client_secret_entry.grid(row=1, column=1, padx=5, pady=3, sticky='ew')

            ctk.CTkLabel(spotify_frame, text="Redirect URI Spotify:").grid(row=2, column=0, sticky='w', padx=5, pady=3)
            self.spotify_redirect_uri_var = ctk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI))
            self.spotify_redirect_uri_entry = ctk.CTkEntry(spotify_frame, textvariable=self.spotify_redirect_uri_var, width=200)
            self.spotify_redirect_uri_entry.grid(row=2, column=1, padx=5, pady=3, sticky='ew')
            spotify_frame.columnconfigure(1, weight=1)

            soundstat_frame = ctk.CTkFrame(frame_settings)
            soundstat_frame.pack(fill=ctk.X, padx=5, pady=5)

            ctk.CTkLabel(soundstat_frame, text="Clé API SoundStat:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
            self.soundstat_api_key_var = ctk.StringVar(value=self.current_config_for_settings.get("SOUNDSTAT_API_KEY", ""))
            self.soundstat_api_key_entry = ctk.CTkEntry(soundstat_frame, textvariable=self.soundstat_api_key_var, width=200, show="*")
            self.soundstat_api_key_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')
            soundstat_frame.columnconfigure(1, weight=1)

            content_settings_frame = ctk.CTkFrame(frame_settings)
            content_settings_frame.pack(fill=ctk.X, padx=5, pady=5)

            # S'assurer que les valeurs pour StringVar soient des chaînes d'entiers valides
            self.s_max_recent_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("MAX_RECENT_TRACKS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_RECENT_TRACKS"]))))
            self.s_max_top_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("MAX_TOP_TRACKS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_TOP_TRACKS"]))))
            self.s_max_podcasts_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("MAX_PODCAST_EPISODES", DEFAULT_CONTENT_SETTINGS_GUI["MAX_PODCAST_EPISODES"]))))
            self.s_max_library_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY", DEFAULT_CONTENT_SETTINGS_GUI["MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"]))))
            self.s_max_soundstat_recos_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("MAX_SOUNDSTAT_RECOMMENDATIONS", DEFAULT_CONTENT_SETTINGS_GUI["MAX_SOUNDSTAT_RECOMMENDATIONS"]))))
            self.s_soundstat_seed_count_var = ctk.StringVar(value=str(int(self.current_config_for_settings.get("SOUNDSTAT_SEED_TRACK_COUNT", DEFAULT_CONTENT_SETTINGS_GUI["SOUNDSTAT_SEED_TRACK_COUNT"]))))

            setting_fields_list = [
                ("Max Titres Récents:", self.s_max_recent_var, "MAX_RECENT_TRACKS"),
                ("Max Top Titres:", self.s_max_top_var, "MAX_TOP_TRACKS"),
                ("Max Épisodes Podcast:", self.s_max_podcasts_var, "MAX_PODCAST_EPISODES"),
                ("Max Recos Bibliothèque:", self.s_max_library_var, "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"),
                ("Max Recos SoundStat:", self.s_max_soundstat_recos_var, "MAX_SOUNDSTAT_RECOMMENDATIONS"),
                ("Nb Seeds SoundStat:", self.s_soundstat_seed_count_var, "SOUNDSTAT_SEED_TRACK_COUNT")
            ]

            for i, (text, var, _) in enumerate(setting_fields_list):
                ctk.CTkLabel(content_settings_frame, text=text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
                entry = ctk.CTkEntry(content_settings_frame, textvariable=var, width=50)
                entry.grid(row=i, column=1, sticky='w', padx=5, pady=2)

            content_settings_frame.columnconfigure(1, weight=0)

            save_button_frame = ctk.CTkFrame(frame_settings)
            save_button_frame.pack(pady=(15, 0))

            self.save_button = ctk.CTkButton(save_button_frame, text="Sauvegarder Toute la Configuration", command=self.on_save_all_settings)
            self.save_button.pack()
        except Exception as e:
            print(f"Erreur lors de la configuration de l'onglet Settings: {e}")
            traceback.print_exc()

    def validate_positive_integer(self, value):
        try:
            num = int(value)
            if num < 0:
                return False
            return True
        except ValueError:
            return False

    def on_save_all_settings(self):
        try:
            config_to_save = {
                "SPOTIPY_CLIENT_ID": self.spotify_client_id_var.get().strip(),
                "SPOTIPY_CLIENT_SECRET": self.spotify_client_secret_var.get().strip(),
                "SPOTIPY_REDIRECT_URI": self.spotify_redirect_uri_var.get().strip(),
                "SOUNDSTAT_API_KEY": self.soundstat_api_key_var.get().strip(),
            }

            content_settings_vars_map = {
                "MAX_RECENT_TRACKS": self.s_max_recent_var,
                "MAX_TOP_TRACKS": self.s_max_top_var,
                "MAX_PODCAST_EPISODES": self.s_max_podcasts_var,
                "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": self.s_max_library_var,
                "MAX_SOUNDSTAT_RECOMMENDATIONS": self.s_max_soundstat_recos_var,
                "SOUNDSTAT_SEED_TRACK_COUNT": self.s_soundstat_seed_count_var
            }

            for key, str_var in content_settings_vars_map.items():
                if not self.validate_positive_integer(str_var.get()):
                    self.show_error("Valeur Invalide", f"La valeur pour '{key}' doit être un nombre entier positif.")
                    return
                config_to_save[key] = int(str_var.get())

            if not all([config_to_save["SPOTIPY_CLIENT_ID"],
                        config_to_save["SPOTIPY_CLIENT_SECRET"],
                        config_to_save["SPOTIPY_REDIRECT_URI"]]):
                self.show_error("Champs Spotify manquants",
                               "Veuillez remplir tous les champs Spotify (Client ID, Client Secret, Redirect URI).")
                return

            save_config_values_to_file(config_to_save, self)
            self.initial_config = load_config_values_from_file()

            self.max_recent_var.set(str(self.initial_config.get("MAX_RECENT_TRACKS")))
            self.max_top_var.set(str(self.initial_config.get("MAX_TOP_TRACKS")))
            self.max_podcasts_var.set(str(self.initial_config.get("MAX_PODCAST_EPISODES")))
            self.max_library_var.set(str(self.initial_config.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY")))
            self.max_soundstat_recos_var.set(str(self.initial_config.get("MAX_SOUNDSTAT_RECOMMENDATIONS")))
            self.soundstat_seed_count_var.set(str(self.initial_config.get("SOUNDSTAT_SEED_TRACK_COUNT")))

            print("Configuration sauvegardée. Les paramètres de l'onglet 'Application' ont été mis à jour avec ces nouvelles valeurs par défaut.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    try:
        print("Démarrage de l'application...")
        ctk.set_appearance_mode("Dark")  # Mode sombre par défaut
        ctk.set_default_color_theme("blue")  # Couleur par défaut
        main_window = ctk.CTk()
        main_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))  # Gérer la fermeture de la fenêtre
        app = SpotifyTrueDailyApp(main_window)
        print("Démarrage de la boucle principale de l'interface graphique...")
        main_window.mainloop()
    except Exception as e:
        print(f"Erreur lors de l'exécution de l'application: {e}")
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")  # Garder la console ouverte pour voir les erreurs

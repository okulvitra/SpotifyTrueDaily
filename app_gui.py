import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import importlib  # Pour recharger les modules si config change
import time  # Pour le strftime dans les logs

if getattr(sys, 'frozen', False):
    # Si l'application est "gelée" (exécutable PyInstaller)
    application_path = os.path.dirname(sys.executable)
else:
    # Si c'est un script Python normal
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILENAME = os.path.join(application_path, "config.py")

# --- Définition de ConfigError pour la GUI ---
class ConfigError(Exception):
    """Exception personnalisée pour les erreurs de configuration."""
    pass

# --- Tentative d'import de playlist_manager ---
# Il est crucial que playlist_manager.py soit dans le même dossier.
# Il doit aussi définir sa propre `ConfigError` et la lever au lieu de `exit()`.

playlist_manager_module = None  # Variable pour stocker le module importé
try:
    # Tenter d'importer l'exception personnalisée de playlist_manager
    # pour la gérer spécifiquement si elle est levée lors de l'import du module.
    from playlist_manager import ConfigError as PM_ConfigError
    import playlist_manager as pm
    playlist_manager_module = pm  # Stocker la référence au module
except ConfigError as e:
    # Attrape notre ConfigError locale si playlist_manager.py a un problème avant de définir la sienne
    # ou si l'import de playlist_manager lui-même échoue pour une raison autre que sa propre ConfigError.
    print(f"ERREUR (GUI): Problème de configuration détecté: {e}")
    print("L'application va démarrer. Veuillez vérifier/sauvegarder la configuration via l'onglet 'Settings'.")
except ImportError as e_imp:
    if "playlist_manager" in str(e_imp).lower():
        # Afficher une messagebox si Tkinter peut être initialisé, sinon print et exit.
        try:
            root_temp = tk.Tk()
            root_temp.withdraw()  # Cacher la fenêtre principale temporaire
            messagebox.showerror("Erreur Critique",
                                 "Le fichier 'playlist_manager.py' est introuvable.\n"
                                 "Assurez-vous qu'il est dans le même dossier que app_gui.py.",
                                 parent=None)  # Pas de parent car root_temp est cachée
            root_temp.destroy()
        except tk.TclError:  # Si Tk n'a pas pu être initialisé (ex: pas d'affichage)
            print("ERREUR CRITIQUE: Le fichier 'playlist_manager.py' est introuvable.")
        sys.exit(f"Dépendance 'playlist_manager.py' manquante: {e_imp}")
    else:  # Autre erreur d'import
        print(f"Erreur d'importation inattendue: {e_imp}")
        sys.exit(1)

# --- Gestion de la Configuration (config.py) ---

CONFIG_FILENAME = "config.py"
DEFAULT_REDIRECT_URI = 'http://127.0.0.1:8888/callback' # Correction de l'URL google

DEFAULT_CONTENT_SETTINGS_GUI = {
    "MAX_RECENT_TRACKS": 5,
    "MAX_TOP_TRACKS": 5,
    "MAX_PODCAST_EPISODES": 3,
    "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": 2,
    "MAX_SOUNDSTAT_RECOMMENDATIONS": 3,
    "SOUNDSTAT_SEED_TRACK_COUNT": 2
}

def load_config_values_from_file():
    """Charge les valeurs depuis config.py."""
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
            # S'assurer que toutes les clés de contenu ont leurs valeurs par défaut si le fichier n'existe pas
            for key_default, val_default in DEFAULT_CONTENT_SETTINGS_GUI.items():
                if key_default not in config_vals:  # Devrait déjà y être, mais par sécurité
                    config_vals[key_default] = val_default
    except Exception as e:
        print(f"Erreur en lisant {CONFIG_FILENAME}: {e}. Utilisation des valeurs par défaut.")
        config_vals.update(DEFAULT_CONTENT_SETTINGS_GUI)  # S'assurer que les valeurs par défaut sont là
    return config_vals


def save_config_values_to_file(config_data):
    """Écrit toutes les valeurs de config_data dans config.py."""
    # S'assurer que les valeurs numériques sont bien des nombres pour l'écriture
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
        with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("Settings", f"Configuration sauvegardée dans {CONFIG_FILENAME} !\n\n"
                                       "Les nouveaux paramètres seront utilisés au prochain lancement de la mise à jour.")
    except Exception as e:
        messagebox.showerror("Erreur de sauvegarde", f"Impossible de sauvegarder la configuration : {e}")


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_):
        if self.widget.winfo_exists():
            self.widget.configure(state='normal')
            self.widget.insert(tk.END, str_, (self.tag,))
            self.widget.see(tk.END)
            self.widget.configure(state='disabled')

    def flush(self):
        pass


class SpotifyTrueDailyApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("SpotifyTrueDaily v1.0 by okulvitra")  # Ajout du nom
        self.root.geometry("800x650")
        self.root.minsize(700, 550)

        style = ttk.Style()
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')

        self.notebook = ttk.Notebook(self.root)
        self.tab_application = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.tab_settings = ttk.Frame(self.notebook, padding="10 10 10 10")

        self.notebook.add(self.tab_application, text='  Application  ')
        self.notebook.add(self.tab_settings, text='  Settings  ')
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.initial_config = load_config_values_from_file()

        self.setup_application_tab()
        self.setup_settings_tab()

        self.footer = tk.Label(self.root, text="Copyright @ okulvitra - 2025", bd=1, relief=tk.SUNKEN, anchor=tk.CENTER)  # Centré
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.redirect_logging()
        print("Interface graphique initialisée.\n"
              "Ajustez les quantités dans l'onglet 'Application' pour cette exécution.\n"
              "Sauvegardez les clés API et les valeurs par défaut dans 'Settings'.\n"
              "La première authentification Spotify ouvrira votre navigateur.\n")

    def redirect_logging(self):
        sys.stdout = TextRedirector(self.log_area, "stdout")
        sys.stderr = TextRedirector(self.log_area, "stderr")
        self.log_area.tag_configure("stderr", foreground="red")

    def setup_application_tab(self):
        frame_app = self.tab_application

        content_params_frame = ttk.LabelFrame(frame_app, text=" Paramètres de la Playlist pour cette exécution ", padding="10 10 10 10")
        content_params_frame.pack(pady=(0, 10), fill=tk.X, side=tk.TOP)

        # Variables Tkinter pour les Spinbox, initialisées avec les valeurs de config.py
        self.max_recent_var = tk.IntVar(value=self.initial_config.get("MAX_RECENT_TRACKS"))
        self.max_top_var = tk.IntVar(value=self.initial_config.get("MAX_TOP_TRACKS"))
        self.max_podcasts_var = tk.IntVar(value=self.initial_config.get("MAX_PODCAST_EPISODES"))
        self.max_library_var = tk.IntVar(value=self.initial_config.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"))  # Ajout pour la bibliothèque
        self.max_soundstat_recos_var = tk.IntVar(value=self.initial_config.get("MAX_SOUNDSTAT_RECOMMENDATIONS"))
        self.soundstat_seed_count_var = tk.IntVar(value=self.initial_config.get("SOUNDSTAT_SEED_TRACK_COUNT"))

        fields_app_tab = [
            ("Titres Récents:", self.max_recent_var),
            ("Top Titres:", self.max_top_var),
            ("Épisodes de Podcast:", self.max_podcasts_var),
            ("Recos Bibliothèque:", self.max_library_var),  # Ajouté
            ("Recos SoundStat:", self.max_soundstat_recos_var),
            ("Seeds pour SoundStat:", self.soundstat_seed_count_var)
        ]

        for i, (text, var) in enumerate(fields_app_tab):
            ttk.Label(content_params_frame, text=text).grid(row=i, column=0, sticky='w', padx=5, pady=3)
            spinbox = ttk.Spinbox(content_params_frame, from_=0, to=50, textvariable=var, width=5)
            spinbox.grid(row=i, column=1, sticky='w', padx=5, pady=3)

        content_params_frame.columnconfigure(1, weight=0)

        disclaimer_label = ttk.Label(content_params_frame,
                                    text="Note: Des valeurs élevées (ex: >10 par catégorie) peuvent augmenter\n"
                                         "le risque de dépasser les limites d'appels API de Spotify.",
                                    font=('TkDefaultFont', 8, 'italic'))  # Utiliser TkDefaultFont pour la portabilité
        disclaimer_label.grid(row=len(fields_app_tab), column=0, columnspan=2, pady=(8, 0), sticky='w')

        button_frame = ttk.Frame(frame_app)
        button_frame.pack(pady=15, side=tk.TOP)  # Ajusté pady
        s_button = ttk.Style()
        s_button.configure('Accent.TButton', font=('TkDefaultFont', 10, 'bold'), padding=6)
        self.start_button = ttk.Button(button_frame, text="Start Playlist Update", command=self.on_start_button_click, style="Accent.TButton")
        self.start_button.pack()

        log_frame = ttk.LabelFrame(frame_app, text="Logs de l'application", padding="5 5 5 5")
        log_frame.pack(padx=5, pady=(5, 5), expand=True, fill='both', side=tk.TOP)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=10, font=("Consolas", 9))
        self.log_area.pack(expand=True, fill='both')

    def on_start_button_click(self):
        """Récupère les valeurs de l'onglet App, les passe au thread d'exécution."""
        run_time_config = {
            "MAX_RECENT_TRACKS": self.max_recent_var.get(),
            "MAX_TOP_TRACKS": self.max_top_var.get(),
            "MAX_PODCAST_EPISODES": self.max_podcasts_var.get(),
            "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": self.max_library_var.get(),  # Ajouté
            "MAX_SOUNDSTAT_RECOMMENDATIONS": self.max_soundstat_recos_var.get(),
            "SOUNDSTAT_SEED_TRACK_COUNT": self.soundstat_seed_count_var.get()
        }
        self.run_playlist_update_thread(run_time_config)

    def run_playlist_update_thread(self, run_time_config):  # Accepte la config pour ce run
        self.start_button.config(state=tk.DISABLED, text="Mise à jour en cours...")
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')
        print(f"[{time.strftime('%H:%M:%S')}] Lancement de la mise à jour de la playlist avec les paramètres actuels...\n")

        # Passer run_time_config au thread
        thread = threading.Thread(target=self.execute_playlist_update, args=(run_time_config,), daemon=True)
        thread.start()

    def execute_playlist_update(self, run_config_for_this_execution):
        global playlist_manager_module  # Utiliser la référence globale
        try:
            # Recharger les modules pour s'assurer que config.py (pour les clés API) est à jour
            # si l'utilisateur a sauvegardé dans l'onglet Settings depuis le dernier run.
            if 'config' in sys.modules:
                importlib.reload(sys.modules['config'])

            if 'playlist_manager' in sys.modules and playlist_manager_module is not None:
                playlist_manager_module = importlib.reload(playlist_manager_module)  # Recharger et réassigner
            elif playlist_manager_module is None:
                from playlist_manager import ConfigError as PM_ConfigError_reload  # Importer localement
                import playlist_manager as pm_reloaded
                playlist_manager_module = pm_reloaded

            if playlist_manager_module is None:
                raise RuntimeError("Le module playlist_manager n'a pas pu être chargé.")

            # Modifier dynamiquement les constantes globales DANS le module playlist_manager
            # avant d'appeler sa fonction.
            # Ces constantes doivent être définies au niveau du module dans playlist_manager.py
            # et être chargées depuis config.py par défaut dans ce module.
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
            messagebox.showerror(error_title, error_message, parent=self.root)
            print(f"ERREUR DE CONFIGURATION (GUI): {e_conf}")
        except AttributeError as e_attr:
            messagebox.showerror("Erreur d'application", f"Fonctionnalité non trouvée ou erreur interne: {e_attr}", parent=self.root)
            print(f"ERREUR D'ATTRIBUT (GUI): {e_attr}")
        except Exception as e_exec:
            messagebox.showerror("Erreur d'exécution", f"Une erreur est survenue pendant la mise à jour : {e_exec}", parent=self.root)
            print(f"ERREUR PENDANT L'EXÉCUTION (GUI): {e_exec}")
            import traceback
            print(traceback.format_exc())
        finally:
            if hasattr(self, 'start_button') and self.start_button.winfo_exists():
                self.start_button.config(state=tk.NORMAL, text="Start Playlist Update")

    def setup_settings_tab(self):
        frame_settings = self.tab_settings
        self.current_config_for_settings = load_config_values_from_file()

        spotify_frame = ttk.LabelFrame(frame_settings, text=" Configuration API Spotify ", padding="10 10 10 10")
        spotify_frame.pack(fill=tk.X, padx=5, pady=(5, 0))  # Moins de marge en bas

        ttk.Label(spotify_frame, text="Client ID Spotify:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.spotify_client_id_var = tk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_CLIENT_ID", ""))
        self.spotify_client_id_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_client_id_var, width=60, show="*")
        self.spotify_client_id_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(spotify_frame, text="Client Secret Spotify:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.spotify_client_secret_var = tk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_CLIENT_SECRET", ""))
        self.spotify_client_secret_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_client_secret_var, width=60, show="*")
        self.spotify_client_secret_entry.grid(row=1, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(spotify_frame, text="Redirect URI Spotify:").grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.spotify_redirect_uri_var = tk.StringVar(value=self.current_config_for_settings.get("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI))
        self.spotify_redirect_uri_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_redirect_uri_var, width=60)
        self.spotify_redirect_uri_entry.grid(row=2, column=1, padx=5, pady=3, sticky='ew')
        spotify_frame.columnconfigure(1, weight=1)

        soundstat_frame = ttk.LabelFrame(frame_settings, text=" Configuration API SoundStat ", padding="10 10 10 10")
        soundstat_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(soundstat_frame, text="Clé API SoundStat:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.soundstat_api_key_var = tk.StringVar(value=self.current_config_for_settings.get("SOUNDSTAT_API_KEY", ""))
        self.soundstat_api_key_entry = ttk.Entry(soundstat_frame, textvariable=self.soundstat_api_key_var, width=60, show="*")
        self.soundstat_api_key_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')
        soundstat_frame.columnconfigure(1, weight=1)

        content_settings_frame = ttk.LabelFrame(frame_settings, text=" Paramètres par Défaut du Contenu (sauvegardés dans config.py) ", padding="10 10 10 10")
        content_settings_frame.pack(fill=tk.X, padx=5, pady=5)

        self.s_max_recent_var = tk.StringVar(value=str(self.current_config_for_settings.get("MAX_RECENT_TRACKS")))
        self.s_max_top_var = tk.StringVar(value=str(self.current_config_for_settings.get("MAX_TOP_TRACKS")))
        self.s_max_podcasts_var = tk.StringVar(value=str(self.current_config_for_settings.get("MAX_PODCAST_EPISODES")))
        self.s_max_library_var = tk.StringVar(value=str(self.current_config_for_settings.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY")))
        self.s_max_soundstat_recos_var = tk.StringVar(value=str(self.current_config_for_settings.get("MAX_SOUNDSTAT_RECOMMENDATIONS")))
        self.s_soundstat_seed_count_var = tk.StringVar(value=str(self.current_config_for_settings.get("SOUNDSTAT_SEED_TRACK_COUNT")))

        setting_fields_list = [
            ("Max Titres Récents:", self.s_max_recent_var, "MAX_RECENT_TRACKS"),
            ("Max Top Titres:", self.s_max_top_var, "MAX_TOP_TRACKS"),
            ("Max Épisodes Podcast:", self.s_max_podcasts_var, "MAX_PODCAST_EPISODES"),
            ("Max Recos Bibliothèque:", self.s_max_library_var, "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"),
            ("Max Recos SoundStat:", self.s_max_soundstat_recos_var, "MAX_SOUNDSTAT_RECOMMENDATIONS"),
            ("Nb Seeds SoundStat:", self.s_soundstat_seed_count_var, "SOUNDSTAT_SEED_TRACK_COUNT")
        ]
        for i, (text, var, _) in enumerate(setting_fields_list):  # Le _ est pour la clé qu'on n'utilise pas ici
            ttk.Label(content_settings_frame, text=text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(content_settings_frame, textvariable=var, width=7)
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=2)
        content_settings_frame.columnconfigure(1, weight=0)

        save_button_frame = ttk.Frame(frame_settings)
        save_button_frame.pack(pady=(15, 0))
        self.save_button = ttk.Button(save_button_frame, text="Sauvegarder Toute la Configuration", command=self.on_save_all_settings, style="Accent.TButton")
        self.save_button.pack()

    def on_save_all_settings(self):
        config_to_save = {
            "SPOTIPY_CLIENT_ID": self.spotify_client_id_var.get().strip(),
            "SPOTIPY_CLIENT_SECRET": self.spotify_client_secret_var.get().strip(),
            "SPOTIPY_REDIRECT_URI": self.spotify_redirect_uri_var.get().strip(),
            "SOUNDSTAT_API_KEY": self.soundstat_api_key_var.get().strip(),
        }

        content_settings_vars_map = {  # Map pour faire correspondre la clé à la variable Stringvar
            "MAX_RECENT_TRACKS": self.s_max_recent_var,
            "MAX_TOP_TRACKS": self.s_max_top_var,
            "MAX_PODCAST_EPISODES": self.s_max_podcasts_var,
            "MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY": self.s_max_library_var,
            "MAX_SOUNDSTAT_RECOMMENDATIONS": self.s_max_soundstat_recos_var,
            "SOUNDSTAT_SEED_TRACK_COUNT": self.s_soundstat_seed_count_var
        }

        for key, str_var in content_settings_vars_map.items():
            try:
                config_to_save[key] = int(str_var.get())
            except ValueError:
                messagebox.showwarning("Valeur Invalide", f"La valeur pour '{key}' doit être un nombre entier.", parent=self.root)
                return

        if not all([config_to_save["SPOTIPY_CLIENT_ID"],
                    config_to_save["SPOTIPY_CLIENT_SECRET"],
                    config_to_save["SPOTIPY_REDIRECT_URI"]]):
            messagebox.showwarning("Champs Spotify manquants",
                                   "Veuillez remplir tous les champs Spotify (Client ID, Client Secret, Redirect URI).", parent=self.root)
            return

        save_config_values_to_file(config_to_save)

        # Mettre à jour les valeurs utilisées par l'onglet Application pour la prochaine exécution
        self.initial_config = load_config_values_from_file()  # Recharger la config globale de la GUI
        self.max_recent_var.set(self.initial_config.get("MAX_RECENT_TRACKS"))
        self.max_top_var.set(self.initial_config.get("MAX_TOP_TRACKS"))
        self.max_podcasts_var.set(self.initial_config.get("MAX_PODCAST_EPISODES"))
        self.max_library_var.set(self.initial_config.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY"))
        self.max_soundstat_recos_var.set(self.initial_config.get("MAX_SOUNDSTAT_RECOMMENDATIONS"))
        self.soundstat_seed_count_var.set(self.initial_config.get("SOUNDSTAT_SEED_TRACK_COUNT"))

        print("Configuration sauvegardée. Les paramètres de l'onglet 'Application' ont été mis à jour avec ces nouvelles valeurs par défaut.")

# --- Lancement de l'application ---

if __name__ == '__main__':
    main_window = tk.Tk()
    app = SpotifyTrueDailyApp(main_window)
    main_window.mainloop()

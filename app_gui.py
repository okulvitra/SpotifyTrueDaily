import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import importlib  # Pour recharger les modules si config change
import time  # Ajout de l'import manquant

# Essayer d'importer playlist_manager et gérer l'erreur de configuration initiale
# que nous avons définie dans playlist_manager.py
try:
    import playlist_manager
except playlist_manager.ConfigError as e:
    # Afficher l'erreur de config initiale et suggérer d'utiliser l'onglet Settings
    # On ne peut pas faire grand-chose de plus ici car la GUI n'est pas encore lancée.
    # L'utilisateur devra configurer via l'onglet Settings de la GUI une fois lancée.
    # Ou créer un config.py manuellement au préalable.
    print(f"Erreur de configuration initiale de playlist_manager: {e}")
    print("Veuillez configurer les clés API via l'onglet 'Settings' de l'application après son lancement, ou créer/corriger config.py.")
    # On pourrait choisir de ne pas importer playlist_manager ici et de le faire
    # uniquement lorsque l'utilisateur clique sur "Start", après avoir potentiellement
    # sauvegardé une configuration. Pour l'instant, on le laisse comme ça.
    # Si l'import échoue ici, les appels à playlist_manager.refresh_daily_playlist échoueront.
    pass  # Laisser la GUI se lancer pour permettre la configuration
except ImportError:
    # Cas où playlist_manager.py n'est pas trouvé du tout.
    print("ERREUR CRITIQUE: Le fichier 'playlist_manager.py' est introuvable. L'application ne peut pas fonctionner.")
    # Dans une vraie application, on pourrait afficher une messagebox ici si Tkinter est déjà initialisé.
    # Pour l'instant, on quitte si le fichier principal est manquant.
    # messagebox.showerror("Erreur Critique", "Le fichier 'playlist_manager.py' est introuvable.") # Ne fonctionnera pas avant tk.Tk()
    exit()

# --- Gestion de la Configuration (config.py) ---

CONFIG_FILENAME = "config.py"
DEFAULT_REDIRECT_URI = 'http://127.0.0.1:8888/callback'  # Valeur par défaut commune

def load_config_values_from_file():
    """Charge les valeurs depuis config.py en le lisant comme un fichier texte."""
    config_vals = {
        "SPOTIPY_CLIENT_ID": "",
        "SPOTIPY_CLIENT_SECRET": "",
        "SPOTIPY_REDIRECT_URI": DEFAULT_REDIRECT_URI,
        "SOUNDSTAT_API_KEY": ""
    }
    try:
        if os.path.exists(CONFIG_FILENAME):
            with open(CONFIG_FILENAME, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue  # Ignorer les lignes vides ou les commentaires
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        # Enlever les guillemets simples ou doubles autour de la valeur
                        value = value.strip()
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        elif value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]

                        if key in config_vals:
                            config_vals[key] = value
        else:
            print(f"Note: Le fichier {CONFIG_FILENAME} n'existe pas. Des valeurs par défaut ou vides seront utilisées dans les paramètres.")
    except Exception as e:
        print(f"Erreur en lisant {CONFIG_FILENAME} pour les valeurs initiales: {e}")
    return config_vals


def save_config_values_to_file(spotify_client_id, spotify_client_secret, spotify_redirect_uri, soundstat_api_key):
    """Écrit les valeurs dans config.py."""
    content = f"""# config.py - VOS INFORMATIONS CONFIDENTIELLES
# Ce fichier est généré par l'application SpotifyTrueDaily.
# Remplissez avec vos informations. NE PARTAGEZ PAS CE FICHIER REMPLI !

# Configuration Spotify
SPOTIPY_CLIENT_ID = '{spotify_client_id}'
SPOTIPY_CLIENT_SECRET = '{spotify_client_secret}'
SPOTIPY_REDIRECT_URI = '{spotify_redirect_uri}'

# Configuration SoundStat
SOUNDSTAT_API_KEY = '{soundstat_api_key}'
"""
    try:
        with open(CONFIG_FILENAME, 'w') as f:
            f.write(content)
        messagebox.showinfo("Settings", f"Configuration sauvegardée dans {CONFIG_FILENAME} !\n\n"
                                       "La mise à jour de la playlist utilisera ces nouveaux paramètres.")
    except Exception as e:
        messagebox.showerror("Erreur de sauvegarde", f"Impossible de sauvegarder la configuration : {e}")

# --- Redirection des logs vers le widget Text ---

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_):
        self.widget.configure(state='normal')
        # Utiliser des tags pour potentiellement colorer stdout vs stderr différemment
        self.widget.insert(tk.END, str_, (self.tag,))
        self.widget.see(tk.END)  # Auto-scroll
        self.widget.configure(state='disabled')

    def flush(self):
        pass


# --- Classe principale de l'application GUI ---

class SpotifyTrueDailyApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("SpotifyTrueDaily v1.0")
        # Augmenter la taille pour un meilleur affichage des logs et des paramètres
        self.root.geometry("800x600")
        self.root.minsize(600, 400)  # Taille minimale

        # Style
        style = ttk.Style()
        try:
            # Essayer d'utiliser un thème plus moderne si disponible
            # 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
            if 'clam' in style.theme_names():
                style.theme_use('clam')
            elif 'vista' in style.theme_names():  # Bon pour Windows
                style.theme_use('vista')
        except tk.TclError:
            print("Thème Tkinter par défaut utilisé.")

        # --- Création des onglets ---
        self.notebook = ttk.Notebook(self.root)

        self.tab_application = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.tab_settings = ttk.Frame(self.notebook, padding="10 10 10 10")

        self.notebook.add(self.tab_application, text='  Application  ')  # Ajout d'espaces pour un meilleur look
        self.notebook.add(self.tab_settings, text='  Settings  ')
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # --- Contenu de l'onglet "Application" ---
        self.setup_application_tab()

        # --- Contenu de l'onglet "Settings" ---
        self.setup_settings_tab()

        # --- Pied de page ---
        self.footer = tk.Label(self.root, text="Copyright @ okulvitra - 2025", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)

        # Rediriger stdout et stderr vers le widget de log
        self.redirect_logging()
        print("Interface graphique initialisée. Configurez vos clés API dans l'onglet 'Settings' si ce n'est pas déjà fait.\n")

    def redirect_logging(self):
        sys.stdout = TextRedirector(self.log_area, "stdout")
        sys.stderr = TextRedirector(self.log_area, "stderr")
        # Configurer un tag pour stderr pour le colorer en rouge (optionnel)
        self.log_area.tag_configure("stderr", foreground="red")

    def setup_application_tab(self):
        frame_app = self.tab_application

        # Frame pour le bouton, pour le centrer
        button_frame = ttk.Frame(frame_app)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Playlist Update", command=self.run_playlist_update_thread, style="Accent.TButton")
        self.start_button.pack()

        # Style pour le bouton (optionnel, dépend du thème)
        s = ttk.Style()
        s.configure('Accent.TButton', font=('Arial', 10, 'bold'), padding=5)

        # Zone de texte pour les logs
        log_frame = ttk.LabelFrame(frame_app, text="Logs de l'application", padding="5 5 5 5")
        log_frame.pack(padx=5, pady=(0, 5), expand=True, fill='both')

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=15, font=("Consolas", 9))
        self.log_area.pack(expand=True, fill='both')

    def run_playlist_update_thread(self):
        self.start_button.config(state=tk.DISABLED, text="Mise à jour en cours...")

        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')

        print(f"[{time.strftime('%H:%M:%S')}] Lancement de la mise à jour de la playlist...\n")

        thread = threading.Thread(target=self.execute_playlist_update, daemon=True)
        thread.start()

    def execute_playlist_update(self):
        try:
            # Avant d'appeler playlist_manager, nous devons nous assurer qu'il utilisera
            # le fichier config.py potentiellement mis à jour par la GUI.
            # Python met en cache les modules importés.
            # Si config.py a été modifié par la GUI, nous devons recharger config et playlist_manager.
            if 'config' in sys.modules:
                importlib.reload(sys.modules['config'])
                print("Module 'config' rechargé.")
            if 'playlist_manager' in sys.modules:
                # Recharger playlist_manager pour qu'il réimporte le config.py mis à jour.
                # Cela suppose que les constantes globales dans playlist_manager sont redéfinies
                # lors du rechargement à partir du nouveau config.
                importlib.reload(sys.modules['playlist_manager'])
                print("Module 'playlist_manager' rechargé pour prendre en compte la nouvelle configuration.")

            # Maintenant, appelez la fonction principale de playlist_manager
            # Elle devrait lever ConfigError si la configuration est toujours invalide.
            playlist_manager.refresh_daily_playlist()
            print(f"\n[{time.strftime('%H:%M:%S')}] --- Mise à jour terminée (depuis la GUI) ---")

        except playlist_manager.ConfigError as e_conf:  # Attraper l'exception personnalisée
            error_title = "Erreur de Configuration"
            error_message = (f"La mise à jour n'a pas pu démarrer à cause d'une erreur de configuration:\n\n{e_conf}\n\n"
                             "Veuillez vérifier vos clés API dans l'onglet 'Settings' et sauvegarder.")
            messagebox.showerror(error_title, error_message)
            print(f"ERREUR DE CONFIGURATION (GUI): {e_conf}")
        except AttributeError as e_attr:
            messagebox.showerror("Erreur d'application", f"Fonctionnalité non trouvée ou erreur interne: {e_attr}")
            print(f"ERREUR D'ATTRIBUT (GUI): {e_attr}")
        except Exception as e_exec:
            messagebox.showerror("Erreur d'exécution", f"Une erreur est survenue pendant la mise à jour : {e_exec}")
            print(f"ERREUR PENDANT L'EXÉCUTION (GUI): {e_exec}")
            import traceback
            print(traceback.format_exc())  # Pour plus de détails dans les logs
        finally:
            if hasattr(self, 'start_button') and self.start_button.winfo_exists():
                self.start_button.config(state=tk.NORMAL, text="Start Playlist Update")

    def setup_settings_tab(self):
        frame_settings = self.tab_settings
        current_config = load_config_values_from_file()

        # Utiliser des LabelFrames pour mieux organiser
        spotify_frame = ttk.LabelFrame(frame_settings, text=" Configuration API Spotify ", padding="10 10 10 10")
        spotify_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(spotify_frame, text="Client ID Spotify:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.spotify_client_id_var = tk.StringVar(value=current_config.get("SPOTIPY_CLIENT_ID", ""))
        self.spotify_client_id_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_client_id_var, width=60, show="*")
        self.spotify_client_id_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(spotify_frame, text="Client Secret Spotify:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.spotify_client_secret_var = tk.StringVar(value=current_config.get("SPOTIPY_CLIENT_SECRET", ""))
        self.spotify_client_secret_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_client_secret_var, width=60, show="*")
        self.spotify_client_secret_entry.grid(row=1, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(spotify_frame, text="Redirect URI Spotify:").grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.spotify_redirect_uri_var = tk.StringVar(value=current_config.get("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI))
        self.spotify_redirect_uri_entry = ttk.Entry(spotify_frame, textvariable=self.spotify_redirect_uri_var, width=60)
        self.spotify_redirect_uri_entry.grid(row=2, column=1, padx=5, pady=3, sticky='ew')

        spotify_frame.columnconfigure(1, weight=1)  # Permet au champ Entry de s'étendre

        soundstat_frame = ttk.LabelFrame(frame_settings, text=" Configuration API SoundStat ", padding="10 10 10 10")
        soundstat_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(soundstat_frame, text="Clé API SoundStat:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.soundstat_api_key_var = tk.StringVar(value=current_config.get("SOUNDSTAT_API_KEY", ""))
        self.soundstat_api_key_entry = ttk.Entry(soundstat_frame, textvariable=self.soundstat_api_key_var, width=60, show="*")
        self.soundstat_api_key_entry.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

        soundstat_frame.columnconfigure(1, weight=1)

        # Frame pour le bouton de sauvegarde pour le centrer
        save_button_frame = ttk.Frame(frame_settings)
        save_button_frame.pack(pady=20)
        self.save_button = ttk.Button(save_button_frame, text="Sauvegarder la Configuration", command=self.on_save_settings, style="Accent.TButton")
        self.save_button.pack()

    def on_save_settings(self):
        spotify_id = self.spotify_client_id_var.get()
        spotify_secret = self.spotify_client_secret_var.get()
        spotify_redirect = self.spotify_redirect_uri_var.get()
        soundstat_key = self.soundstat_api_key_var.get()

        if not all([spotify_id.strip(), spotify_secret.strip(), spotify_redirect.strip()]):
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs Spotify (Client ID, Client Secret, Redirect URI).")
            return
        # La clé SoundStat peut être vide si l'utilisateur ne veut pas l'utiliser.

        save_config_values_to_file(spotify_id, spotify_secret, spotify_redirect, soundstat_key)


# --- Lancement de l'application ---

if __name__ == '__main__':
    main_window = tk.Tk()
    app = SpotifyTrueDailyApp(main_window)
    main_window.mainloop()

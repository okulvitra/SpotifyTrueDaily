# Guide d'utilisation des icônes Lucide dans SpotifyTrueDaily

## 🎨 Présentation

Ce projet utilise des icônes basées sur la bibliothèque [Lucide Icons](https://lucide.dev/), une collection open-source de plus de 1000 icônes vectorielles SVG conçues pour les projets numériques modernes.

## 📁 Fichiers d'icônes disponibles

Le projet inclut déjà le fichier d'icône principal :
- `truedaily.ico` - Icône de l'application utilisée pour la fenêtre Windows

## 🔧 Intégration dans l'application

### 1. Icône de fenêtre principale

L'icône est automatiquement appliquée dans `app_modern.py` :

```python
# Set window icon if available
try:
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "truedaily.ico")
    if os.path.exists(icon_path):
        self.iconbitmap(icon_path)
        print(f"Window icon set successfully: {icon_path}")
    else:
        print(f"Icon file not found: {icon_path}")
except Exception as e:
    print(f"Could not set window icon: {e}")
```

### 2. Icônes dans la sidebar

Les icônes de navigation sont définies dans `modern_ui.py` :

```python
def get_nav_icon(self, item_id):
    """Get Lucide icon for navigation item"""
    icons = {
        "dashboard": "🏠",      # Home icon
        "playlist_config": "🎵", # Music icon
        "settings": "⚙️",       # Settings icon
        "about": "ℹ️"           # Info icon
    }
    return icons.get(item_id, "📄")
```

### 3. Icônes dans le panneau de logs

```python
# Title with Lucide icon
title_label = ctk.CTkLabel(
    header_frame,
    text="📝 Logs",  # Document with pencil icon
    font=("Segoe UI", 14, "bold"),
    text_color=ModernTheme.COLORS['text_primary']
)
```

## 🎯 Bonnes pratiques

### 1. Consistance visuelle
- Utilisez des icônes cohérentes avec le thème musical de l'application
- Maintenez une taille et un style uniformes
- Choisissez des icônes qui représentent clairement leur fonction

### 2. Accessibilité
- Toujours accompagner les icônes de texte descriptif
- Utiliser des couleurs contrastées pour une bonne lisibilité
- S'assurer que les icônes restent compréhensibles à différentes tailles

## 📚 Références des icônes courantes

Voici les icônes recommandées pour différents contextes :

### Navigation
- **Dashboard/Home**: 🏠
- **Music/Playlist**: 🎵
- **Settings**: ⚙️
- **Info/About**: ℹ️

### Actions
- **Add/Create**: ➕
- **Refresh**: 🔄
- **Delete/Trash**: 🗑️
- **Search**: 🔍

### Statuts
- **Success**: ✅
- **Error**: ❌
- **Warning**: ⚠️
- **Info**: ℹ️

### Médias
- **Music**: 🎵
- **Podcast**: 🎙️
- **Library**: 📚
- **Target/AI**: 🎯

## 🛠 Maintenance

### Mise à jour des icônes
1. Téléchargez les icônes souhaitées depuis [lucide.dev](https://lucide.dev/)
2. Convertissez-les au format ICO si nécessaire
3. Placez-les dans le répertoire racine du projet
4. Mettez à jour les références dans le code

### Format recommandé
- **Fichier**: ICO (pour Windows)
- **Tailles**: 16x16, 32x32, 48x48 pixels
- **Couleurs**: 32 bits avec alpha channel

## ⚠️ Problèmes connus

### Affichage des emojis
Sur certains systèmes, les emojis peuvent ne pas s'afficher correctement. Dans ce cas :
1. Utiliser des caractères Unicode standards
2. S'assurer que les polices système supportent les emojis
3. Considérer l'utilisation d'icônes SVG pour une meilleure compatibilité

## 🤝 Contribuer

Pour ajouter de nouvelles icônes :
1. Consultez la documentation Lucide
2. Choisissez des icônes qui s'intègrent bien avec le design existant
3. Testez l'affichage sur différentes plateformes
4. Documentez les nouvelles icônes dans ce guide

## 📞 Support

Pour toute question sur l'intégration des icônes :
- Vérifiez d'abord la documentation Lucide officielle
- Testez les icônes sur différents systèmes
- Documentez les problèmes spécifiques rencontrés
# Kivy-based Modern UI for SpotifyTrueDaily

This branch explores a modern UI refactoring using Kivy instead of CustomTkinter.

## Project Structure

- `kivy_ui/`: Main directory for Kivy UI components
  - `main_app.py`: Main Kivy application class
  - `screens/`: Directory for different app screens (dashboard, settings, etc.)
  - `components/`: Reusable UI components
  - `themes/`: Theme definitions and styling
  - `utils/`: Utility functions and helpers
- `kivy_requirements.txt`: Dependencies specific to Kivy implementation

## Getting Started

1. Create a virtual environment: `python -m venv kivy_env`
2. Activate it: `source kivy_env/bin/activate` (Linux/macOS) or `kivy_env\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r kivy_requirements.txt`
4. Run the application: `python kivy_ui/main_app.py`

## Development Notes

- This is a complete rewrite of the UI layer
- Core logic in `playlist_manager.py` remains unchanged
- Configuration handling will be adapted for Kivy
- Focus on modern design principles and cross-platform compatibility
- Follows Kivy best practices for 2025
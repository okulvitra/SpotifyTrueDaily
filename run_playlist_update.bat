@echo off
echo Starting Spotify Playlist Updater script...

REM Change directory to the script's location
cd /D "C:\Users\M\Desktop\spotiapp"

REM Activate virtual environment
echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

REM Check if activation was successful (optional, python path should now point to venv)
REM where python

REM Run the Python script
echo Running Python script...
python "playlist_manager.py"

REM Optional: Deactivate virtual environment (the script ending usually handles this)
REM call ".venv\Scripts\deactivate.bat"

echo Script finished.
REM Optional: Pause to see output if running manually, remove for scheduled task
REM pause
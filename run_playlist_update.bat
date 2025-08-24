@echo off
echo Starting Spotify Playlist Updater script...

REM This script assumes it is being run with the project's root directory
REM as the current working directory.
REM For Windows Task Scheduler, ensure the "Start in" directory is set
REM to the full path of your project folder (e.g., C:\Users\YourName\Desktop\spotiapp).

REM Activate virtual environment (relative path from project root)
echo Activating virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment activate.bat not found in .venv\Scripts.
    echo Please ensure this batch file is in the project root,
    echo and the Task Scheduler's "Start in" directory is set correctly.
    pause
    exit /b 1
)
call ".venv\Scripts\activate.bat"

REM Run the Python script (relative path from project root)
echo Running Python script...
if not exist "playlist_manager.py" (
    echo ERROR: playlist_manager.py not found.
    echo Please ensure this batch file is in the project root.
    pause
    exit /b 1
)
python "playlist_manager.py"

echo Script finished.
REM Optional: To see output when run manually, uncomment the next line.
REM For scheduled tasks, keep it commented or remove it.
REM pause
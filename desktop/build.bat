@echo off
REM ─────────────────────────────────────────────────
REM  Build script — Education Space Junior (Windows)
REM  Requires: pip install pyinstaller PyQt6 PyQt6-WebEngine
REM ─────────────────────────────────────────────────

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo [2/3] Running PyInstaller...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "EducationSpaceJunior" ^
  --icon "assets\icon.ico" ^
  --add-data "assets;assets" ^
  --hidden-import "PyQt6.QtWebEngineWidgets" ^
  --hidden-import "PyQt6.QtWebEngineCore" ^
  main.py

echo [3/3] Done!
echo Executable is at: dist\EducationSpaceJunior.exe
pause

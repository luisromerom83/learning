@echo off
REM ─────────────────────────────────────────────────
REM  Build script — Education Space Junior (Windows)
REM  Requires: pip install pyinstaller pywebview
REM ─────────────────────────────────────────────────

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo [2/3] Running PyInstaller...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "EducationSpaceJunior" ^
  --add-data "index.html;." ^
  main.py

echo [3/3] Done!
echo Executable is at: dist\EducationSpaceJunior.exe
pause

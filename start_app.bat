@echo off
echo [Health Monitor] Fixing path compatibility...

rem 1. Check if we are in a path with special characters (like masaustu)
rem Tech: Map current folder to virtual drive Z: to fool MediaPipe
subst Z: /D >nul 2>&1
subst Z: "%~dp0."

if not exist Z:\main.py (
    echo [Error] Could not mount virtual drive.
    echo Please move this folder to C:\MediaPipe and try again.
    pause
    exit
)

echo [Health Monitor] Launching from Virtual Drive Z:...
Z:
venv\Scripts\python main.py

echo.
echo [System] Application closed.
rem Cleanup
subst Z: /D
pause

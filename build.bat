@echo off

:: =========================================================
::  E.V.O Build Script
:: =========================================================

echo ========================================
echo   E.V.O Build Script
echo ========================================

:: ----------------------------------------------------
:: Step 1: Verify Python is available
:: ----------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.12+ first.
    pause
    exit /b 1
)
echo [OK] Python found.

:: ----------------------------------------------------
:: Step 2: Install/upgrade build dependencies
:: ----------------------------------------------------
echo [INFO] Installing build dependencies...

pip install --upgrade pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install/upgrade PyInstaller.
    pause
    exit /b 1
)

pip install "rapidfuzz==3.6.1" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install rapidfuzz 3.6.1.
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install project requirements.
    pause
    exit /b 1
)

echo [OK] Dependencies ready.

:: ----------------------------------------------------
:: Step 3: Install Playwright browsers (Chromium only)
:: ----------------------------------------------------
echo [INFO] Installing Playwright browsers (Chromium only)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Playwright browser install failed.
    pause
    exit /b 1
)

echo [OK] Playwright ready.

:: ----------------------------------------------------
:: Step 4: Create runtime hook for Playwright (playwright_hook.py)
:: ----------------------------------------------------
rem Create a clean file
if exist playwright_hook.py del /f /q playwright_hook.py

rem Write the hook contents
>>playwright_hook.py echo import os, sys
>>playwright_hook.py echo if getattr(sys, 'frozen', False):
>>playwright_hook.py echo     os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(sys._MEIPASS, 'ms-playwright')

:: ----------------------------------------------------
:: Step 5: Build with PyInstaller
:: ----------------------------------------------------
echo [INFO] Building EVO.exe with PyInstaller...

pyinstaller --noconfirm --windowed --onedir ^
    --name EVO ^
    --icon evo_icon.ico ^
    --runtime-hook playwright_hook.py ^
    --add-data "actions;actions" ^
    --add-data "agent;agent" ^
    --add-data "config;config" ^
    --add-data "core;core" ^
    --add-data "memory;memory" ^
    --hidden-import "playwright.sync_api" ^
    --hidden-import "sklearn.utils._cython_blas" ^
    --collect-all "google.generativeai" ^
    --collect-all "sounddevice" ^
    main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   [SUCCESS] Build complete!
echo   Output: dist\EVO\EVO.exe
echo ========================================
pause

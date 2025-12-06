@echo off
REM PhishGuard API Key Setup Script (Windows)
REM This script launches the Python API key configuration tool

echo ========================================
echo PhishGuard API Key Setup
echo ========================================
echo.

cd /d "%~dp0.."

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Run the setup script
python scripts\setup_api_keys.py

echo.
pause

@echo off
echo ==========================================
echo Lindy Automation - Quick Start Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Install dependencies
echo [*] Installing dependencies...
pip install playwright pyperclip

echo.
echo [*] Installing Playwright browsers...
python -m playwright install chromium

echo.
echo [*] Setting up config file...
if not exist config.py (
    copy config_template.py config.py
    echo [!] Please edit config.py with your credentials before running!
    echo     Open config.py in a text editor and fill in your details.
) else (
    echo [OK] config.py already exists
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit config.py with your credentials
echo 2. Run: python main_playwright.py
echo.
echo The browser will open and you can watch the automation!
echo.
pause

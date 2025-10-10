#!/bin/bash

echo "=========================================="
echo "Lindy Automation - Quick Start Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install playwright pyperclip

echo ""
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

echo ""
echo "📝 Setting up config file..."
if [ ! -f config.py ]; then
    cp config_template.py config.py
    echo "⚠️  Please edit config.py with your credentials before running!"
    echo "   Open config.py in a text editor and fill in your details."
else
    echo "✅ config.py already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.py with your credentials"
echo "2. Run: python3 main_playwright.py"
echo ""
echo "The browser will open and you can watch the automation!"

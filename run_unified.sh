#!/bin/bash

# Lindy Automation - Unified Runner Script

echo "========================================"
echo "Lindy Automation - Unified Version"
echo "========================================"
echo ""
echo "Choose mode:"
echo "1) Headed (Visible Browser) - Default"
echo "2) Headless (Background)"
echo ""
read -p "Enter choice (1 or 2, default=1): " choice

case $choice in
    2)
        echo ""
        echo "Running in HEADLESS mode..."
        python run_automation_unified.py --headless
        ;;
    *)
        echo ""
        echo "Running in HEADED mode..."
        python run_automation_unified.py --headed
        ;;
esac

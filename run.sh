#!/bin/bash

echo "Starting Lindy Automation with Playwright..."
echo "Browser will be visible so you can see exactly what's happening"
echo ""

cd /home/code/lindy-automation-selenium
source venv/bin/activate
export DISPLAY=:1
python3 run_automation.py

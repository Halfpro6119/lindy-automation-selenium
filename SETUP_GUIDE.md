# How to Run the Lindy Automation on Your Computer (Visible Browser Mode)

This guide will help you run the automation on your own computer so you can see exactly what it's doing in real-time.

## Prerequisites

1. **Python 3.8 or higher** installed on your computer
   - Check by running: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Git** installed (to clone the repository)
   - Check by running: `git --version`
   - Download from: https://git-scm.com/downloads

## Step-by-Step Setup

### 1. Clone the Repository

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
```

### 2. Install Python Dependencies

#### Option A: Using Playwright (Recommended - Better Visibility)

```bash
# Install Playwright
pip install playwright pyperclip

# Install Playwright browsers (this downloads Chromium)
playwright install chromium
```

#### Option B: Using Selenium (Original Version)

```bash
# Install Selenium and dependencies
pip install -r requirements.txt
```

### 3. Configure Your Credentials

Create a `config.py` file from the template:

```bash
cp config_template.py config.py
```

Then edit `config.py` with your actual credentials:

```python
# Google Account Credentials
GOOGLE_EMAIL = "your-email@gmail.com"
GOOGLE_PASSWORD = "your-password"

# Card Details for Free Trial
CARD_NUMBER = "5196120393968168"
CARD_EXPIRY = "02/30"
CARD_CVC = "315"
CARDHOLDER_NAME = "Mr Big G"
CARD_COUNTRY = "United Kingdom"
POSTAL_CODE = "SW1A 1AA"

# ... rest of the config
```

### 4. Run the Automation

#### Option A: Run with Playwright (Visible Browser)

```bash
python main_playwright.py
```

This will open a **visible Chrome browser** where you can watch every step of the automation in real-time!

#### Option B: Run with Selenium (Original)

To run Selenium with a visible browser, you need to modify `main.py`:

1. Open `main.py` in a text editor
2. Find this line in the `__init__` method:
   ```python
   options = webdriver.ChromeOptions()
   ```
3. Comment out or remove these lines:
   ```python
   # options.add_argument('--headless')  # Remove this if present
   ```
4. Run:
   ```bash
   python main.py
   ```

## What You'll See

When running in visible mode, you'll see the browser:

1. ✅ Navigate to Lindy.ai
2. ✅ Click "Sign in with Google"
3. ✅ Enter your Google credentials
4. ✅ Fill out any signup forms
5. ✅ Handle free trial and payment details
6. ✅ Navigate to the template
7. ✅ Create webhook and copy URL
8. ✅ Generate authorization token
9. ✅ Deploy the Lindy automation
10. ✅ Configure N8N with the webhook details
11. ✅ Start processing
12. ✅ Wait 10 minutes
13. ✅ Delete the account

## Troubleshooting

### "playwright: command not found" after installation

Try:
```bash
python -m playwright install chromium
```

### "Module not found" errors

Make sure you're in the correct directory and have installed dependencies:
```bash
cd lindy-automation-selenium
pip install playwright pyperclip
```

### Browser doesn't open (headless mode)

Make sure you're using `main_playwright.py` which has `headless=False` set, or modify `main.py` to remove headless mode.

### Permission errors on Linux/Mac

Use `pip3` instead of `pip`:
```bash
pip3 install playwright pyperclip
python3 -m playwright install chromium
```

### Google blocks automated sign-in

- Use an app-specific password instead of your regular password
- Disable 2-factor authentication temporarily (not recommended for production)
- Google may require manual verification the first time

## Customization

### Adjust Wait Times

Edit `config.py` to change timing:

```python
SHORT_WAIT = 5      # seconds
MEDIUM_WAIT = 10    # seconds
LONG_WAIT = 20      # seconds
WAIT_TIME = 600     # 10 minutes (change to 60 for 1 minute testing)
```

### Skip Account Deletion

Comment out this line in the `run()` method:

```python
# await self.delete_lindy_account()  # Comment this out
```

### Run in Slow Motion (Playwright Only)

Modify `main_playwright.py` to add slow motion:

```python
self.browser = await playwright.chromium.launch(
    headless=False,
    slow_mo=1000  # Add this line (1000ms = 1 second delay between actions)
)
```

## Comparison: Playwright vs Selenium

| Feature | Playwright | Selenium |
|---------|-----------|----------|
| **Visibility** | Excellent (native headed mode) | Good (requires configuration) |
| **Speed** | Faster | Slower |
| **Reliability** | More reliable | Can be flaky |
| **Setup** | Easier (auto-installs browsers) | Requires ChromeDriver |
| **Debugging** | Better dev tools | Standard |

**Recommendation:** Use Playwright (`main_playwright.py`) for the best experience!

## Security Warning

⚠️ **Never commit your `config.py` file with real credentials to a public repository!**

The `.gitignore` file is already configured to exclude `config.py`, but always double-check before pushing to GitHub.

## Need Help?

If you encounter issues:

1. Check the console output for error messages
2. Make sure all dependencies are installed
3. Verify your credentials in `config.py`
4. Try running with increased wait times
5. Open an issue on GitHub with the error details

## Advanced: Recording the Automation

### Using Playwright's Built-in Recorder

```bash
playwright codegen https://chat.lindy.ai
```

This opens a browser and records your actions, which can help you understand the automation flow.

### Screen Recording (Mac)

Use QuickTime Player or:
```bash
# Record the screen while running
screencapture -v output.mov &
python main_playwright.py
```

### Screen Recording (Windows)

Use Windows Game Bar (Win + G) or OBS Studio.

### Screen Recording (Linux)

```bash
# Install recordmydesktop
sudo apt-get install recordmydesktop

# Record
recordmydesktop &
python3 main_playwright.py
```

## Summary

**Quick Start (Recommended):**

```bash
# 1. Clone
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium

# 2. Install
pip install playwright pyperclip
playwright install chromium

# 3. Configure
cp config_template.py config.py
# Edit config.py with your credentials

# 4. Run with visible browser
python main_playwright.py
```

Now sit back and watch the automation work! 🎬

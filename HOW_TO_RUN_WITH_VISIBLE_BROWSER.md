# 🎬 How to Run the Automation with a Visible Browser

This guide shows you how to run the Lindy automation on your own computer so you can **watch everything happen in real-time**.

## 🚀 Quick Start (3 Steps)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
```

### Step 2: Run the Setup Script

**On Mac/Linux:**
```bash
./quick_start.sh
```

**On Windows:**
```bash
quick_start.bat
```

**Or manually:**
```bash
pip install playwright pyperclip
python -m playwright install chromium
cp config_template.py config.py
```

### Step 3: Configure and Run

1. **Edit `config.py`** with your credentials (use any text editor)
2. **Run the automation:**
   ```bash
   python main_playwright.py
   ```

That's it! A Chrome browser will open and you'll see every action happening live! 🎉

---

## 📋 Detailed Instructions

### What You Need

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads/)
- **Internet connection**
- **Your credentials** (Google account, card details)

### Installation Steps

1. **Open Terminal/Command Prompt**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Mac: Press `Cmd + Space`, type "Terminal", press Enter
   - Linux: Press `Ctrl + Alt + T`

2. **Navigate to where you want the project**
   ```bash
   cd Desktop  # or wherever you want it
   ```

3. **Clone the repository**
   ```bash
   git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
   cd lindy-automation-selenium
   ```

4. **Install Playwright**
   ```bash
   pip install playwright pyperclip
   ```
   
   If you get permission errors, try:
   ```bash
   pip install --user playwright pyperclip
   ```

5. **Install Chromium browser**
   ```bash
   python -m playwright install chromium
   ```

6. **Create your config file**
   ```bash
   cp config_template.py config.py
   ```
   
   On Windows:
   ```bash
   copy config_template.py config.py
   ```

7. **Edit config.py**
   
   Open `config.py` in any text editor (Notepad, VS Code, etc.) and fill in:
   
   ```python
   GOOGLE_EMAIL = "your-email@gmail.com"
   GOOGLE_PASSWORD = "your-password"
   # ... etc
   ```

8. **Run the automation!**
   ```bash
   python main_playwright.py
   ```

---

## 🎥 What You'll See

When you run `python main_playwright.py`, a Chrome browser window will open and you'll see:

1. **Browser opens** - Chromium launches in full screen
2. **Navigate to Lindy** - Goes to chat.lindy.ai
3. **Click "Sign in with Google"** - Finds and clicks the button
4. **Enter email** - Types your Google email
5. **Enter password** - Types your Google password
6. **Fill signup form** - Completes any required fields
7. **Handle free trial** - Enters card details if needed
8. **Navigate to template** - Goes to the specific template URL
9. **Add template** - Clicks to add template to account
10. **Create webhook** - Creates webhook and copies URL
11. **Generate token** - Creates authorization token
12. **Deploy** - Deploys the Lindy automation
13. **Configure N8N** - Enters webhook details in N8N
14. **Start processing** - Clicks start button
15. **Wait 10 minutes** - Countdown timer
16. **Delete account** - Cleans up

**Every step is visible!** You can watch the mouse move, see text being typed, and observe all clicks.

---

## ⚙️ Customization Options

### Make it Run Slower (Easier to Watch)

Edit `main_playwright.py` and change this line:

```python
self.browser = await playwright.chromium.launch(
    headless=False,
    slow_mo=1000  # Add this line - 1000ms = 1 second between actions
)
```

### Change Wait Times

Edit `config.py`:

```python
SHORT_WAIT = 5      # Change to 10 for slower
MEDIUM_WAIT = 10    # Change to 20 for slower
WAIT_TIME = 600     # Change to 60 for 1 minute instead of 10
```

### Skip Account Deletion

In `main_playwright.py`, comment out this line in the `run()` method:

```python
# await self.delete_lindy_account()  # Add # at the start
```

### Pause at Specific Steps

Add this line anywhere in `main_playwright.py` to pause:

```python
await self.page.pause()  # Browser will pause and wait for you to click "Resume"
```

---

## 🐛 Troubleshooting

### "python: command not found"

Try `python3` instead:
```bash
python3 main_playwright.py
```

### "playwright: command not found"

Install it:
```bash
pip install playwright
python -m playwright install chromium
```

### "Module not found: playwright"

Make sure you're in the right directory:
```bash
cd lindy-automation-selenium
pip install playwright pyperclip
```

### Browser doesn't open (runs in background)

Make sure you're using `main_playwright.py` (not `main.py`). The Playwright version has `headless=False` which makes the browser visible.

### Google blocks sign-in

- Try using an app-specific password
- Disable 2FA temporarily
- Google may require manual verification first time

### "Permission denied" on Mac/Linux

Use `pip3` and `python3`:
```bash
pip3 install playwright pyperclip
python3 -m playwright install chromium
python3 main_playwright.py
```

---

## 📊 Comparison: Playwright vs Selenium

| Feature | Playwright (main_playwright.py) | Selenium (main.py) |
|---------|--------------------------------|-------------------|
| **Visibility** | ✅ Excellent | ⚠️ Requires config |
| **Setup** | ✅ Easy (auto-installs) | ⚠️ Need ChromeDriver |
| **Speed** | ✅ Faster | ⚠️ Slower |
| **Reliability** | ✅ More stable | ⚠️ Can be flaky |
| **Debugging** | ✅ Better tools | ⚠️ Standard |

**Recommendation:** Use `main_playwright.py` for the best experience! ⭐

---

## 🎬 Recording the Automation

### Built-in Playwright Inspector

```bash
PWDEBUG=1 python main_playwright.py
```

This opens a debugger where you can step through each action!

### Screen Recording

**Mac:**
- Use QuickTime Player → File → New Screen Recording

**Windows:**
- Press `Win + G` to open Game Bar
- Click record button

**Linux:**
```bash
sudo apt-get install recordmydesktop
recordmydesktop &
python3 main_playwright.py
```

---

## 🔒 Security Tips

⚠️ **Important:**

1. **Never commit `config.py`** to GitHub (it's already in `.gitignore`)
2. **Use app-specific passwords** instead of your main Google password
3. **Don't share your config file** with anyone
4. **Delete test accounts** after use
5. **Use test credit cards** when possible

---

## 📝 Summary

**To run with visible browser:**

```bash
# 1. Clone
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium

# 2. Install
pip install playwright pyperclip
python -m playwright install chromium

# 3. Configure
cp config_template.py config.py
# Edit config.py with your credentials

# 4. Run and watch!
python main_playwright.py
```

**That's it!** The browser will open and you can watch every step happen in real-time! 🎉

---

## 💡 Pro Tips

1. **Run in slow motion** for easier viewing (add `slow_mo=1000`)
2. **Use dual monitors** - code on one, browser on the other
3. **Record the session** for later review
4. **Pause at key steps** using `await self.page.pause()`
5. **Check console output** for detailed logs

---

## 🆘 Need Help?

If you run into issues:

1. Check the console output for error messages
2. Make sure all dependencies are installed
3. Verify credentials in `config.py`
4. Try increasing wait times
5. Open an issue on GitHub with error details

---

## 🎓 Learning Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Playwright Inspector](https://playwright.dev/python/docs/debug)
- [Selenium vs Playwright](https://playwright.dev/python/docs/selenium)

---

**Enjoy watching your automation in action!** 🚀

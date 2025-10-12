# Lindy Automation with Selenium/Playwright

This automation script handles the complete workflow for Lindy account setup, webhook configuration, and N8N integration.

## Features

- **Visible Browser Mode**: Browser stays open throughout the entire process so you can see exactly what's happening
- **Session Management**: Saves login session to avoid repeated logins
- **Automatic Template Addition**: Adds the specified Lindy template to your account
- **Webhook Configuration**: Creates and configures webhooks with authorization tokens
- **N8N Integration**: Automatically configures N8N with Lindy webhook details
- **Account Cleanup**: Deletes the Lindy account after processing
- **Detailed Logging**: Console output shows every step with clear status indicators
- **Screenshot Capture**: Takes screenshots at each major step for debugging

## What You'll See

The browser will:
1. **Stay open during login** - You can watch the entire login process
2. **Remain visible during automation** - See every click, form fill, and navigation
3. **Show all steps clearly** - Console output explains what's happening
4. **Keep open after completion** - Review results before closing

## Prerequisites

- Python 3.7+
- Playwright (installed via requirements.txt)
- Valid Lindy account credentials
- N8N instance URL

## Installation

### Quick Start (Recommended)

**Windows:**
```bash
quick_start.bat
```

**Linux/Mac:**
```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Configure credentials:
```bash
cp config_template.py config.py
# Edit config.py with your credentials
```

## Configuration

Edit `config.py` with your details:

```python
# Google Account (for Lindy login)
GOOGLE_EMAIL = "your-email@gmail.com"
GOOGLE_PASSWORD = "your-password"

# Lindy Template URL
LINDY_TEMPLATE_URL = "https://chat.lindy.ai/home/?templateId=YOUR_TEMPLATE_ID"

# N8N Configuration
N8N_URL = "https://your-n8n-instance.com"

# Wait time (in seconds) - default 10 minutes
WAIT_TIME = 600
```

## Usage

### Run with Visible Browser (Recommended)

This mode keeps the browser open so you can see everything:

```bash
python main_playwright_headed.py
```

**What happens:**
1. Browser opens and stays visible
2. You'll see the login page (manual login required on first run)
3. Watch as the automation navigates through each step
4. Console shows detailed progress with ✓ checkmarks
5. Browser remains open after completion for review

### Run with Headless Browser

For automated/background execution:

```bash
python main_playwright.py
```

### Using the Run Script

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

## First Run - Manual Login

On the first run, you'll need to log in manually:

1. The browser will open to the Lindy login page
2. Log in with your Google account
3. Wait until you reach the Lindy workspace/home page
4. The automation will detect the login and continue automatically
5. Your session will be saved for future runs

**Console output will show:**
```
======================================================================
MANUAL LOGIN REQUIRED
======================================================================

→ The browser window is now open and visible
→ Please log in manually in the browser window

Steps:
1. Log in to Lindy with your Google account
2. Wait until you see the Lindy workspace/home page
3. The automation will detect the login and continue automatically

→ Waiting for you to log in...
→ Browser will stay open throughout the entire process
```

## Automation Steps

The script performs these steps automatically:

1. **Login Check**: Verifies if already logged in (uses saved session)
2. **Template Addition**: Navigates to template URL and adds it to account
3. **Webhook Configuration**: 
   - Finds the webhook trigger
   - Creates a new webhook
   - Retrieves the webhook URL and authorization token
4. **Agent Deployment**: Deploys the Lindy agent
5. **N8N Configuration**:
   - Navigates to N8N instance
   - Enters webhook URL and authorization token
   - Saves configuration and starts processing
6. **Wait Period**: Waits for specified time (default 10 minutes)
7. **Account Deletion**: Removes the Lindy account

## Console Output

The script provides detailed console output with visual indicators:

- `→` - Action in progress
- `✓` - Success
- `✗` - Failure
- `!!!` - Critical error
- `WARNING:` - Non-critical issue

Example:
```
======================================================================
STEP 1: ADDING TEMPLATE TO ACCOUNT
======================================================================

→ Navigating to template: https://chat.lindy.ai/home/?templateId=...
✓ Template page loaded
✓ Screenshot saved: screenshot_1_template_page.png

→ Looking for 'Add' button...
✓ Found Add button with selector: button:has-text('Add')

→ Clicking 'Add' button...
✓ Template added to account!
```

## Screenshots

The automation captures screenshots at each major step:

- `screenshot_1_template_page.png` - Template page
- `screenshot_2_after_add.png` - After adding template
- `screenshot_3_before_webhook.png` - Before webhook configuration
- `screenshot_4_webhook_opened.png` - Webhook dialog opened
- `screenshot_5_webhook_created.png` - Webhook created
- `screenshot_6_secret.png` - Authorization token
- `screenshot_7_deployed.png` - Agent deployed
- `screenshot_8_n8n.png` - N8N page
- `screenshot_9_n8n_filled.png` - N8N form filled
- `screenshot_10_n8n_saved.png` - N8N configuration saved
- `screenshot_11_n8n_started.png` - Processing started
- `screenshot_12_before_delete.png` - Before account deletion
- `screenshot_13_menu.png` - Menu opened
- `screenshot_14_settings.png` - Settings page
- `screenshot_15_delete_confirm.png` - Delete confirmation
- `screenshot_16_deleted.png` - Account deleted

## Troubleshooting

### Browser Closes Too Quickly

**Solution**: Use `main_playwright_headed.py` - this version keeps the browser open throughout the entire process.

### Can't See What's Happening

**Solution**: The headed mode (`main_playwright_headed.py`) shows the browser window at all times. Watch the console output for detailed progress.

### Login Not Detected

- Make sure you complete the login fully
- Wait until you see the Lindy workspace/home page
- The script checks every 5 seconds for up to 5 minutes

### Webhook Not Found

- Check that the template URL is correct
- Verify the template has a webhook trigger
- Review `screenshot_3_before_webhook.png` to see the page state

### N8N Configuration Failed

- Verify N8N URL is accessible
- Check that input field selectors match your N8N instance
- Review `screenshot_8_n8n.png` for the page layout

### Session File Issues

If you have login problems, delete the saved session:
```bash
rm lindy_session.json
```

## Files

- `main_playwright_headed.py` - Main script with visible browser (RECOMMENDED)
- `main_playwright.py` - Headless version for automation
- `config.py` - Configuration file (create from template)
- `config_template.py` - Configuration template
- `requirements.txt` - Python dependencies
- `quick_start.bat` / `quick_start.sh` - Quick setup scripts
- `run.sh` / `run.bat` - Run scripts
- `lindy_session.json` - Saved login session (auto-generated)

## Security Notes

- Never commit `config.py` with real credentials
- The `.gitignore` file excludes sensitive files
- Session files contain authentication tokens - keep them secure
- Delete session files when done: `rm lindy_session.json`

## Browser Visibility

### Headed Mode (Visible Browser)
- Browser window opens and stays visible
- You can watch every action in real-time
- Great for debugging and understanding the process
- Browser remains open after completion
- Press Ctrl+C to close when done

### Headless Mode (Background)
- Browser runs in background
- Faster execution
- Better for automated/scheduled runs
- No visual feedback except console output

## Requirements

```
playwright>=1.40.0
asyncio
```

## License

This project is for educational and automation purposes.

## Support

For issues or questions:
1. Check the console output for error messages
2. Review the screenshots to see where the automation stopped
3. Verify your configuration in `config.py`
4. Make sure you're using the headed mode to see what's happening

## Updates

To update the script:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
playwright install chromium
```

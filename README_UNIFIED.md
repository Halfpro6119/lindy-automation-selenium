# Lindy Automation - Unified Version with Google OAuth

This is the **unified version** of the Lindy automation script that works seamlessly in both **headed (visible)** and **headless (background)** modes with automatic Google OAuth login.

## 🎯 Key Features

- **✅ Automatic Google OAuth Login**: No manual login required - fully automated
- **✅ Dual Mode Support**: Works in both headed and headless modes
- **✅ Complete Automation**: From login to account deletion
- **✅ Detailed Logging**: See every step with clear status indicators
- **✅ Screenshot Capture**: Debug-friendly with screenshots at each step
- **✅ Error Handling**: Robust error handling with fallback selectors

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone git@github.com:rileyrmarketingai/lindy-automation-selenium.git
cd lindy-automation-selenium
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Configure credentials:**
```bash
cp config_template.py config.py
# Edit config.py with your Google credentials
```

### Configuration

Edit `config.py` with your details:

```python
# Google Account (for Lindy login via OAuth)
GOOGLE_EMAIL = "your-email@gmail.com"
GOOGLE_PASSWORD = "your-password"

# Card Details for Free Trial
CARD_NUMBER = "1234567890123456"
CARD_EXPIRY = "MM/YY"
CARD_CVC = "123"
CARDHOLDER_NAME = "Your Name"
CARD_COUNTRY = "Your Country"
POSTAL_CODE = "Your Postal Code"

# Lindy Template URL
LINDY_TEMPLATE_URL = "https://chat.lindy.ai/home/?templateId=YOUR_TEMPLATE_ID"

# N8N Configuration
N8N_URL = "https://your-n8n-instance.com"

# Wait time (in seconds) - default 10 minutes
WAIT_TIME = 600
```

## 📖 Usage

### Run in Headed Mode (Visible Browser - Default)

See everything happening in real-time:

```bash
python run_automation_unified.py --headed
```

or simply:

```bash
python run_automation_unified.py
```

**What you'll see:**
- Browser window opens and stays visible
- Watch the Google OAuth login process
- See every click, form fill, and navigation
- Console shows detailed progress with ✓ checkmarks
- Browser remains open after completion for review

### Run in Headless Mode (Background)

For automated/scheduled execution:

```bash
python run_automation_unified.py --headless
```

**Benefits:**
- Runs in background without GUI
- Faster execution
- Perfect for CI/CD pipelines
- Lower resource usage
- Same functionality as headed mode

## 🔄 Automation Workflow

The script performs these steps automatically:

1. **🔐 Google OAuth Login**
   - Navigates to Lindy
   - Clicks "Sign in with Google"
   - Automatically enters email and password
   - Handles OAuth redirect back to Lindy
   - Fills signup form if needed

2. **💳 Free Trial Setup** (if available)
   - Clicks "Start Free Trial"
   - Enters card details
   - Saves payment information

3. **📋 Template Addition**
   - Navigates to template URL
   - Adds template to account
   - Switches to editor view

4. **🔗 Webhook Configuration**
   - Finds webhook trigger
   - Creates new webhook
   - Retrieves webhook URL
   - Gets authorization token

5. **🚀 Agent Deployment**
   - Deploys the Lindy agent

6. **⚙️ N8N Configuration**
   - Navigates to N8N instance
   - Enters webhook URL and token
   - Saves configuration
   - Starts processing

7. **⏱️ Wait Period**
   - Waits for specified time (default 10 minutes)

8. **🗑️ Account Cleanup**
   - Deletes the Lindy account

## 📊 Console Output

The script provides detailed console output with visual indicators:

```
======================================================================
Lindy Automation - Unified Version (HEADED MODE)
Works with Google OAuth in both headed and headless modes
======================================================================

Initializing Playwright automation in HEADED (VISIBLE) mode...
Setting up browser in headed (visible) mode...
✓ Browser setup complete in headed (visible) mode!

======================================================================
LOGGING INTO GOOGLE WITH OAUTH
======================================================================

Navigating to Lindy...
Looking for Google sign-in button...
✓ Found Google button: button:has-text('Continue with Google')
✓ Clicked Google sign in
Entering email...
✓ Entered email: your-email@gmail.com
Entering password...
✓ Entered password
Waiting for redirect to Lindy...
✓ Login successful!

======================================================================
ADDING TEMPLATE TO ACCOUNT
======================================================================

Navigating to template: https://chat.lindy.ai/home/?templateId=...
Screenshot saved: screenshot_1_template_page.png
✓ Found Add button with selector: button:has-text('Add')
✓ Clicked 'Add' button to add template
Current URL after adding template: https://chat.lindy.ai/...
✓ Successfully navigated to editor view

... and so on
```

## 📸 Screenshots

The automation captures screenshots at each major step:

| Screenshot | Description |
|------------|-------------|
| `screenshot_1_template_page.png` | Template page loaded |
| `screenshot_2_after_add.png` | After adding template |
| `screenshot_2b_editor_view.png` | Editor view |
| `screenshot_3_before_webhook.png` | Before webhook configuration |
| `screenshot_4_webhook_opened.png` | Webhook dialog opened |
| `screenshot_4b_after_select_option.png` | After selecting webhook option |
| `screenshot_5_webhook_created.png` | Webhook created |
| `screenshot_6_secret.png` | Authorization token revealed |
| `screenshot_7_deployed.png` | Agent deployed |
| `screenshot_8_n8n.png` | N8N page loaded |
| `screenshot_9_n8n_filled.png` | N8N form filled |
| `screenshot_10_n8n_saved.png` | N8N configuration saved |
| `screenshot_11_n8n_started.png` | Processing started |
| `screenshot_12_before_delete.png` | Before account deletion |
| `screenshot_13_menu.png` | Menu opened |
| `screenshot_14_settings.png` | Settings page |
| `screenshot_15_delete_confirm.png` | Delete confirmation |
| `screenshot_16_deleted.png` | Account deleted |

## 🔧 Troubleshooting

### Google Login Fails

**Symptoms:** Script can't find email or password input

**Solutions:**
1. Check that `GOOGLE_EMAIL` and `GOOGLE_PASSWORD` are correct in `config.py`
2. Run in headed mode to see what's happening: `python run_automation_unified.py --headed`
3. Check `screenshot_error_login.png` for visual debugging
4. Google may require additional verification (2FA) - disable for automation account

### Webhook Not Found

**Symptoms:** Script can't find webhook element

**Solutions:**
1. Verify the template URL is correct
2. Check that the template has a webhook trigger
3. Review `screenshot_3_before_webhook.png` to see the page state
4. Run in headed mode to watch the process

### N8N Configuration Failed

**Symptoms:** Can't enter webhook URL or token

**Solutions:**
1. Verify N8N URL is accessible
2. Check that N8N instance is running
3. Review `screenshot_8_n8n.png` for the page layout
4. Ensure input field selectors match your N8N instance

### Script Hangs or Times Out

**Symptoms:** Script stops responding

**Solutions:**
1. Increase timeout values in `config.py`
2. Check your internet connection
3. Run in headed mode to see where it's stuck
4. Review the last screenshot taken

## 🔒 Security Notes

- **Never commit `config.py`** with real credentials
- The `.gitignore` file excludes sensitive files
- Use a dedicated Google account for automation
- Consider using environment variables for credentials
- Delete screenshots after debugging (they may contain sensitive info)

## 📁 Files

| File | Description |
|------|-------------|
| `run_automation_unified.py` | **Main unified script** (headed/headless) |
| `config.py` | Configuration file (create from template) |
| `config_template.py` | Configuration template |
| `requirements.txt` | Python dependencies |
| `README_UNIFIED.md` | This file |

## 🆚 Comparison: Headed vs Headless

| Feature | Headed Mode | Headless Mode |
|---------|-------------|---------------|
| **Visibility** | Browser window visible | Runs in background |
| **Speed** | Slightly slower | Faster |
| **Debugging** | Easy to see what's happening | Relies on logs/screenshots |
| **Resource Usage** | Higher (GUI rendering) | Lower |
| **Use Case** | Development, debugging | Production, CI/CD |
| **User Interaction** | Can watch in real-time | No visual feedback |

## 🎓 Advanced Usage

### Running with Custom Wait Time

Modify `config.py`:
```python
WAIT_TIME = 300  # 5 minutes instead of 10
```

### Running in CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Run Lindy Automation

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  automate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run automation
        env:
          GOOGLE_EMAIL: ${{ secrets.GOOGLE_EMAIL }}
          GOOGLE_PASSWORD: ${{ secrets.GOOGLE_PASSWORD }}
        run: python run_automation_unified.py --headless
      
      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: screenshot_*.png
```

### Environment Variables

Instead of hardcoding credentials in `config.py`, use environment variables:

```python
import os

GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL', 'default@example.com')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD', 'default-password')
```

Then run:
```bash
export GOOGLE_EMAIL="your-email@gmail.com"
export GOOGLE_PASSWORD="your-password"
python run_automation_unified.py --headless
```

## 🐛 Debug Mode

For maximum debugging information, run in headed mode and watch the console:

```bash
python run_automation_unified.py --headed 2>&1 | tee automation.log
```

This will:
- Show the browser window
- Print all console output
- Save output to `automation.log` file

## 📝 Requirements

```
playwright>=1.40.0
```

Python 3.7+ required.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test in both headed and headless modes
5. Submit a pull request

## 📄 License

This project is for educational and automation purposes.

## 🆘 Support

For issues or questions:
1. Check the console output for error messages
2. Review the screenshots to see where the automation stopped
3. Verify your configuration in `config.py`
4. Run in headed mode to see what's happening: `python run_automation_unified.py --headed`
5. Check the troubleshooting section above

## 🔄 Updates

To update the script:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
playwright install chromium
```

---

**Made with ❤️ for automation enthusiasts**

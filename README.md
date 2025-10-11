# Lindy Automation - Full Playwright Version

This automation script uses **Playwright** to automate the entire Lindy workflow with a **visible browser** so you can see exactly what's happening in real-time.

## Features

- ✅ **100% Playwright** - No Selenium, pure Playwright automation
- ✅ **Visible Browser** - Watch the automation happen in real-time
- ✅ **Complete Workflow** - From login to account deletion
- ✅ **Screenshot Capture** - Saves screenshots at each major step
- ✅ **Error Handling** - Robust error handling with detailed logging

## What It Does

1. **Login to Google** - Authenticates with your Google account
2. **Start Free Trial** - Enters card details and starts the free trial (if needed)
3. **Add Template** - Navigates to the specified template and adds it to your workspace
4. **Configure Webhook** - Creates a webhook and retrieves the URL and authorization token
5. **Deploy Agent** - Deploys the Lindy agent
6. **Configure N8N** - Enters the webhook URL and token into the N8N interface
7. **Wait Period** - Waits for 10 minutes (configurable)
8. **Delete Account** - Removes the Lindy account

## Prerequisites

- Python 3.10+
- Virtual environment (included)
- Playwright (installed in venv)

## Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
   cd lindy-automation-selenium
   ```

2. **Configuration is already set up** in `config.py` with your credentials

3. **Virtual environment and Playwright are already installed**

## Running the Automation

### Quick Start

Simply run:
```bash
./run.sh
```

### Manual Start

If you prefer to run manually:
```bash
source venv/bin/activate
export DISPLAY=:1
python3 run_automation.py
```

## What You'll See

When you run the automation:

1. **A browser window will open** - You'll see Chromium launch
2. **Real-time automation** - Watch as the script navigates through each step
3. **Console output** - Detailed progress messages in your terminal
4. **Screenshots** - Saved to the project directory at each major step

## Screenshots

The automation saves screenshots at key points:

- `screenshot_1_template_page.png` - Template page before adding
- `screenshot_2_after_add.png` - After clicking Add button
- `screenshot_2b_editor_view.png` - Editor view
- `screenshot_3_before_webhook.png` - Before webhook configuration
- `screenshot_4_webhook_opened.png` - Webhook panel opened
- `screenshot_5_webhook_created.png` - After creating webhook
- `screenshot_6_secret.png` - Authorization token view
- `screenshot_7_deployed.png` - After deployment
- `screenshot_8_n8n.png` - N8N configuration page
- `screenshot_9_n8n_filled.png` - N8N form filled
- `screenshot_10_n8n_saved.png` - N8N configuration saved
- `screenshot_11_n8n_started.png` - Processing started
- `screenshot_12_before_delete.png` - Before account deletion
- `screenshot_13_menu.png` - Menu opened
- `screenshot_14_settings.png` - Settings page
- `screenshot_15_delete_confirm.png` - Delete confirmation
- `screenshot_16_deleted.png` - Account deleted

## Configuration

Edit `config.py` to change:

- Google credentials
- Card details
- Template URL
- N8N URL
- Wait time (default: 600 seconds / 10 minutes)

## Troubleshooting

### Browser doesn't open
Make sure DISPLAY is set:
```bash
export DISPLAY=:1
```

### Playwright not found
Reinstall in the virtual environment:
```bash
source venv/bin/activate
pip install playwright
playwright install chromium
```

### Login fails
The script will wait for manual intervention if Google blocks automated login. Simply log in manually in the browser window and the script will continue.

## Technical Details

- **Browser**: Chromium (via Playwright)
- **Mode**: Headed (visible browser)
- **Language**: Python 3.10+
- **Framework**: Playwright async API
- **Error Handling**: Try-catch blocks with detailed logging
- **Screenshots**: Automatic capture at each step

## Repository

GitHub: https://github.com/Halfpro6119/lindy-automation-selenium

## Support

For issues or questions, please open an issue on GitHub.

## License

MIT License - Feel free to use and modify as needed.

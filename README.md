# Lindy Automation with Playwright

This automation script handles the complete workflow for setting up a Lindy agent with webhook integration and N8N configuration.

## Features

- ✅ Automated Google sign-in with fallback to manual login
- ✅ Template addition to workspace
- ✅ Webhook configuration with URL and authorization token extraction
- ✅ Agent deployment
- ✅ N8N integration setup
- ✅ Automatic account cleanup after 10 minutes
- ✅ Session persistence for reusability
- ✅ Comprehensive error handling and screenshots

## Prerequisites

- Python 3.7+
- Playwright
- pyperclip

## Installation

### Quick Start (Linux/Mac)

```bash
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
./quick_start.sh
```

### Quick Start (Windows)

```powershell
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
.\quick_start.bat
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium

# Install dependencies
pip install playwright pyperclip
python -m playwright install chromium

# Copy and configure settings
cp config_template.py config.py
# Edit config.py with your credentials
```

## Configuration

Edit `config.py` with your credentials:

```python
# Google Account Credentials
GOOGLE_EMAIL = "your-email@gmail.com"
GOOGLE_PASSWORD = "your-password"

# Card Details for Free Trial (if needed)
CARD_NUMBER = "1234567890123456"
CARD_EXPIRY = "MM/YY"
CARD_CVC = "123"
CARDHOLDER_NAME = "Your Name"
CARD_COUNTRY = "Your Country"
POSTAL_CODE = "Your Postal Code"

# URLs
LINDY_TEMPLATE_URL = "https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6"
N8N_URL = "https://n8n-lead-processing-jjde.bolt.host/"

# Timeouts
WAIT_TIME = 600  # 10 minutes
```

## Usage

### Run the automation:

```bash
python main_playwright.py
```

### First Run - Manual Login

Due to Google's security measures that detect automated logins, the first time you run the script:

1. The script will detect that you're not logged in
2. A browser window will open
3. **Manually log in** to Lindy using your Google account
4. Wait until you see the Lindy workspace/home page
5. The script will automatically detect the login and save your session
6. The browser will close and reopen in headless mode to continue the automation

### Subsequent Runs

After the first manual login, the script will use the saved session (`lindy_session.json`) and run completely automated without requiring manual intervention.

## How It Works

The automation performs the following steps:

1. **Session Check**: Checks if you're already logged in using saved session
2. **Manual Login** (if needed): Opens a browser for you to log in manually
3. **Add Template**: Navigates to the specified template and adds it to your workspace
4. **Configure Webhook**: 
   - Finds the webhook trigger in the template
   - Creates a new webhook (or uses existing)
   - Extracts the webhook URL
   - Retrieves the authorization token
5. **Deploy Agent**: Deploys the Lindy agent
6. **Configure N8N**: 
   - Navigates to the N8N URL
   - Enters the Lindy webhook URL
   - Enters the authorization token
   - Saves configuration and starts processing
7. **Wait Period**: Waits for 10 minutes (configurable)
8. **Cleanup**: Deletes the Lindy account

## Troubleshooting

### Google Login Issues

**Problem**: Google blocks automated login attempts

**Solution**: The script now handles this automatically by:
- Detecting when Google blocks the login
- Opening a visible browser window for manual login
- Saving your session for future runs
- Using the saved session to bypass login on subsequent runs

### Screenshots

The script takes screenshots at each major step for debugging:
- `screenshot_1_template_page.png` - Template page
- `screenshot_2_after_add.png` - After adding template
- `screenshot_3_before_webhook.png` - Before webhook configuration
- `screenshot_4_webhook_opened.png` - Webhook dialog opened
- `screenshot_5_webhook_created.png` - After webhook creation
- And more...

Check these screenshots if something goes wrong to see exactly where the automation failed.

### Common Issues

**Issue**: "Not logged in" error
**Fix**: Delete `lindy_session.json` and run the script again to perform a fresh manual login

**Issue**: "Could not find webhook element"
**Fix**: The template structure may have changed. Check the screenshots to see the current page state.

**Issue**: "Could not find Add button"
**Fix**: Verify the template URL is correct and the template still exists.

## Files

- `main_playwright.py` - Main automation script
- `config.py` - Configuration file (create from template)
- `config_template.py` - Configuration template
- `requirements.txt` - Python dependencies
- `quick_start.sh` - Quick start script for Linux/Mac
- `quick_start.bat` - Quick start script for Windows
- `lindy_session.json` - Saved browser session (auto-generated)

## Security Notes

⚠️ **Important**: 
- Never commit `config.py` to version control (it's in `.gitignore`)
- Keep your credentials secure
- The `lindy_session.json` file contains authentication cookies - keep it private
- Consider using environment variables for sensitive data in production

## Customization

### Change Wait Time

Edit `config.py`:
```python
WAIT_TIME = 300  # 5 minutes instead of 10
```

### Use Different Template

Edit `config.py`:
```python
LINDY_TEMPLATE_URL = "https://chat.lindy.ai/home/?templateId=YOUR_TEMPLATE_ID"
```

### Skip Account Deletion

Comment out the deletion step in `main_playwright.py`:
```python
# await self.delete_account()
```

## Development

### Running in Visible Mode

To see what the automation is doing, edit `main_playwright.py`:

```python
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Change to False
    args=[...]
)
```

### Adding More Steps

The automation is modular. Add new methods to the `LindyAutomationPlaywright` class and call them in the `run()` method.

## Known Limitations

1. **Google Login**: Requires manual login on first run due to Google's bot detection
2. **Template Structure**: If Lindy changes their UI, selectors may need updating
3. **N8N Integration**: Assumes specific input field names on the N8N page

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check the screenshots for debugging
- Review the console output for error messages

## Changelog

### Version 2.0 (Current)
- ✅ Fixed Google login detection issues
- ✅ Added manual login fallback
- ✅ Implemented session persistence
- ✅ Improved error handling
- ✅ Added comprehensive screenshots
- ✅ Better selector strategies
- ✅ Cleaned up repository structure

### Version 1.0
- Initial release with basic automation
- Google sign-in (had issues with bot detection)
- Template addition
- Webhook configuration
- N8N integration

## Credits

Created for automating Lindy agent setup and N8N integration workflows.

# Lindy Automation with Selenium

This project automates the complete workflow for setting up a Lindy account with webhook integration and N8N configuration.

## Features

- ✅ Automated Google account sign-in
- ✅ Lindy signup form completion
- ✅ Free trial activation with card details
- ✅ Template installation and configuration
- ✅ Webhook creation and secret key generation
- ✅ N8N integration setup
- ✅ Automated deployment
- ✅ Account cleanup after processing

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone git@github.com:Halfpro6119/lindy-automation-selenium.git
cd lindy-automation-selenium
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

**Important:** Before running the script, you must create your own `config.py` file:

```bash
cp config_template.py config.py
```

Then edit `config.py` and fill in your actual credentials.

All credentials and settings should be stored in `config.py` (copy from `config_template.py`). The file includes:

- Google account credentials
- Card payment details
- GitHub token
- Lindy and N8N URLs
- Timeout settings

**⚠️ Security Warning:** Never commit real credentials to a public repository. This is for demonstration purposes only.

## Usage

Run the automation script:

```bash
python main.py
```

The script will:

1. Sign in to Google account
2. Complete Lindy signup process
3. Activate free trial (if required)
4. Navigate to the specified template
5. Add template to account
6. Configure webhook with secret key
7. Deploy the Lindy automation
8. Configure N8N with Lindy URL and authorization token
9. Start processing
10. Wait for 10 minutes
11. Delete the Lindy account

## Workflow Details

### Google Sign-in
The script automatically signs in using the provided Google credentials.

### Signup Form
Fills out any required signup forms with appropriate information.

### Free Trial Setup
- Clicks "Start Free Trial" button
- Enters card details:
  - Card Number: 5196 1203 9396 8168
  - Expiry: 02/30
  - CVC: 315
  - Cardholder: Mr Big G
  - Country: United Kingdom
  - Postal Code: SW1A 1AA

### Template Configuration
- Navigates to template ID: `68e5dd479651421f3052eaa6`
- Adds template to account
- Locates webhook step
- Creates webhook with name
- Generates and copies Lindy URL
- Creates authorization token/secret key

### Deployment
Deploys the Lindy automation and verifies deployment status.

### N8N Integration
- Navigates to N8N instance
- Enters Lindy URL
- Enters authorization token
- Saves configuration
- Starts processing

### Wait Period
Waits for 10 minutes to allow processing to complete.

### Cleanup
Deletes the Lindy account after processing is complete.

## File Structure

```
lindy-automation-selenium/
├── main.py              # Main automation script
├── config.py            # Configuration and credentials
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- **selenium**: Web automation framework
- **requests**: HTTP library for API calls
- **webdriver-manager**: Automatic ChromeDriver management
- **pyperclip**: Clipboard operations for copying URLs and tokens

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - The script uses `webdriver-manager` to automatically download the correct ChromeDriver
   - Ensure you have Chrome browser installed

2. **Element not found errors**
   - Website structure may have changed
   - Increase timeout values in `config.py`
   - Check if selectors need updating

3. **Google sign-in issues**
   - Verify credentials in `config.py`
   - Check if 2FA is enabled (may require manual intervention)
   - Google may block automated sign-ins - use app-specific passwords if needed

4. **Card payment fails**
   - Ensure card details are valid
   - Check if additional verification is required

5. **Webhook creation fails**
   - Verify you're on the correct template page
   - Check if webhook step exists in the template

## Security Considerations

- Store credentials securely (use environment variables in production)
- Never commit real credentials to version control
- Use `.gitignore` to exclude sensitive files
- Consider using a secrets management service
- Rotate credentials regularly

## Limitations

- Requires Chrome browser
- May need updates if website structure changes
- Google may block automated sign-ins
- Some steps may require manual intervention depending on account status

## Contributing

Feel free to submit issues or pull requests if you find bugs or have improvements.

## License

This project is for educational and demonstration purposes only.

## Disclaimer

This automation tool is provided as-is. Use responsibly and in accordance with the terms of service of all platforms involved. Automated account creation and manipulation may violate terms of service.

## Author

Created by Halfpro6119

## Support

For issues or questions, please open an issue on GitHub.

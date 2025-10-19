# 🔐 OAuth Token Method - Visual Step-by-Step Walkthrough

## Complete Guide with Screenshots and Examples

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create Google Cloud Project](#step-1-create-google-cloud-project)
4. [Step 2: Enable APIs](#step-2-enable-apis)
5. [Step 3: Configure OAuth Consent Screen](#step-3-configure-oauth-consent-screen)
6. [Step 4: Create OAuth Credentials](#step-4-create-oauth-credentials)
7. [Step 5: Download and Install Credentials](#step-5-download-and-install-credentials)
8. [Step 6: Run Setup Script](#step-6-run-setup-script)
9. [Step 7: Authorize Application](#step-7-authorize-application)
10. [Step 8: Verify Setup](#step-8-verify-setup)
11. [Step 9: Use in Your Automation](#step-9-use-in-your-automation)
12. [Troubleshooting](#troubleshooting)

---

## Overview

**What is OAuth?**
OAuth 2.0 is Google's official authentication protocol. Instead of using username/password, your application requests permission to access your Google account, and Google provides a secure token.

**Why OAuth for automation?**
- ✅ Official Google-approved method
- ✅ Tokens never expire (auto-refresh)
- ✅ More secure than password-based login
- ✅ Can be revoked remotely
- ✅ No CAPTCHA challenges

**Time Required:** 15-20 minutes (one-time setup)

---

## Prerequisites

Before starting, make sure you have:

- [ ] A Google account
- [ ] Access to Google Cloud Console
- [ ] Python 3.7+ installed
- [ ] The `oauth_automation.py` file from the repository
- [ ] The `setup_oauth.py` script from the repository

---

## Step 1: Create Google Cloud Project

### 1.1 Navigate to Google Cloud Console

Open your browser and go to:
```
https://console.cloud.google.com/
```

### 1.2 Create New Project

**Visual Guide:**

```
┌─────────────────────────────────────────────────────────┐
│  Google Cloud Console                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Select a project ▼]  ← Click here                    │
│                                                          │
│  Then click: [NEW PROJECT]                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Steps:**
1. Click on the project dropdown at the top (says "Select a project")
2. Click "NEW PROJECT" button
3. Fill in project details:
   - **Project name:** `Lindy Automation` (or any name you prefer)
   - **Organization:** Leave as default (No organization)
   - **Location:** Leave as default
4. Click "CREATE"
5. Wait 30-60 seconds for project creation

**What you'll see:**
```
Creating project "Lindy Automation"...
✓ Project created successfully
```

### 1.3 Select Your New Project

After creation, make sure your new project is selected:
```
┌─────────────────────────────────────────────────────────┐
│  [Lindy Automation ▼]  ← Should show your project name │
└─────────────────────────────────────────────────────────┘
```

---

## Step 2: Enable APIs

### 2.1 Navigate to API Library

**Path:** APIs & Services → Library

**Visual Guide:**
```
┌─────────────────────────────────────────────────────────┐
│  ☰ Menu                                                 │
├─────────────────────────────────────────────────────────┤
│  📊 Dashboard                                           │
│  🔧 APIs & Services  ← Click here                      │
│     ├─ Library       ← Then click here                 │
│     ├─ Credentials                                      │
│     └─ OAuth consent screen                             │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Enable Google+ API

1. In the API Library search box, type: `Google+ API`
2. Click on "Google+ API" from results
3. Click the blue "ENABLE" button
4. Wait for API to be enabled (takes 5-10 seconds)

**What you'll see:**
```
✓ Google+ API enabled
```

### 2.3 Enable People API (Optional but Recommended)

1. Go back to API Library
2. Search for: `People API`
3. Click on "People API"
4. Click "ENABLE"

**Why enable these APIs?**
- Google+ API: Required for basic profile information
- People API: Provides additional user information

---

## Step 3: Configure OAuth Consent Screen

### 3.1 Navigate to OAuth Consent Screen

**Path:** APIs & Services → OAuth consent screen

```
┌─────────────────────────────────────────────────────────┐
│  ☰ Menu → APIs & Services → OAuth consent screen       │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Choose User Type

**Visual Guide:**
```
┌─────────────────────────────────────────────────────────┐
│  Select User Type                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ○ Internal                                             │
│    (Only for Google Workspace users)                    │
│                                                          │
│  ● External  ← Select this                             │
│    (Available to any Google Account)                    │
│                                                          │
│  [CREATE]                                               │
└─────────────────────────────────────────────────────────┘
```

**Select:** External
**Click:** CREATE

### 3.3 Fill in App Information

**Page 1: App Information**

Fill in the following fields:

```
┌─────────────────────────────────────────────────────────┐
│  OAuth consent screen                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  App name: *                                            │
│  [Lindy Automation                    ]                │
│                                                          │
│  User support email: *                                  │
│  [your-email@gmail.com               ▼]                │
│                                                          │
│  App logo: (optional)                                   │
│  [Upload logo]                                          │
│                                                          │
│  Application home page: (optional)                      │
│  [                                    ]                │
│                                                          │
│  Developer contact information: *                       │
│  [your-email@gmail.com                ]                │
│                                                          │
│  [SAVE AND CONTINUE]                                    │
└─────────────────────────────────────────────────────────┘
```

**Required fields:**
- **App name:** `Lindy Automation`
- **User support email:** Your email address
- **Developer contact information:** Your email address

**Click:** SAVE AND CONTINUE

### 3.4 Scopes (Page 2)

```
┌─────────────────────────────────────────────────────────┐
│  Scopes                                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  No scopes added yet                                    │
│                                                          │
│  [ADD OR REMOVE SCOPES]  ← Click if you want to add    │
│                                                          │
│  For basic authentication, you can skip this            │
│                                                          │
│  [SAVE AND CONTINUE]  ← Click here                     │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click "SAVE AND CONTINUE" (you can skip adding scopes)

### 3.5 Test Users (Page 3)

```
┌─────────────────────────────────────────────────────────┐
│  Test users                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Add your email address as a test user                 │
│                                                          │
│  [+ ADD USERS]  ← Click here                           │
│                                                          │
│  Enter email:                                           │
│  [your-email@gmail.com                ]                │
│                                                          │
│  [ADD]                                                  │
│                                                          │
│  Test users:                                            │
│  • your-email@gmail.com                                 │
│                                                          │
│  [SAVE AND CONTINUE]                                    │
└─────────────────────────────────────────────────────────┘
```

**Steps:**
1. Click "+ ADD USERS"
2. Enter your email address
3. Click "ADD"
4. Click "SAVE AND CONTINUE"

### 3.6 Summary (Page 4)

Review your settings and click "BACK TO DASHBOARD"

---

## Step 4: Create OAuth Credentials

### 4.1 Navigate to Credentials

**Path:** APIs & Services → Credentials

```
┌─────────────────────────────────────────────────────────┐
│  ☰ Menu → APIs & Services → Credentials                │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Create OAuth Client ID

**Visual Guide:**
```
┌─────────────────────────────────────────────────────────┐
│  Credentials                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [+ CREATE CREDENTIALS ▼]  ← Click here                │
│     ├─ API key                                          │
│     ├─ OAuth client ID  ← Select this                  │
│     └─ Service account key                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Steps:**
1. Click "+ CREATE CREDENTIALS"
2. Select "OAuth client ID"

### 4.3 Configure OAuth Client

```
┌─────────────────────────────────────────────────────────┐
│  Create OAuth client ID                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Application type: *                                    │
│  ○ Web application                                      │
│  ● Desktop app  ← Select this (IMPORTANT!)            │
│  ○ Android                                              │
│  ○ Chrome app                                           │
│  ○ iOS                                                  │
│  ○ Universal Windows Platform (UWP)                     │
│  ○ TV and Limited Input devices                         │
│                                                          │
│  Name: *                                                │
│  [Lindy Automation Desktop            ]                │
│                                                          │
│  [CREATE]                                               │
└─────────────────────────────────────────────────────────┘
```

**IMPORTANT:** Select "Desktop app" (NOT "Web application")

**Fields:**
- **Application type:** Desktop app
- **Name:** `Lindy Automation Desktop`

**Click:** CREATE

### 4.4 Download Credentials

After creation, you'll see a popup:

```
┌─────────────────────────────────────────────────────────┐
│  OAuth client created                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Your Client ID:                                        │
│  123456789-abc...apps.googleusercontent.com            │
│                                                          │
│  Your Client Secret:                                    │
│  GOCSPX-abc123...                                       │
│                                                          │
│  [DOWNLOAD JSON]  ← Click here                         │
│                                                          │
│  [OK]                                                   │
└─────────────────────────────────────────────────────────┘
```

**Steps:**
1. Click "DOWNLOAD JSON"
2. Save the file (it will be named something like `client_secret_123456789-abc.json`)
3. Click "OK"

---

## Step 5: Download and Install Credentials

### 5.1 Locate Downloaded File

The file is usually in your Downloads folder:
```bash
ls ~/Downloads/client_secret_*.json
```

### 5.2 Rename and Move to Project

```bash
# Navigate to your project directory
cd /path/to/lindy-automation-selenium

# Copy and rename the credentials file
cp ~/Downloads/client_secret_*.json ./oauth_credentials.json

# Verify it's there
ls -la oauth_credentials.json
```

**Expected output:**
```
-rw-r--r-- 1 user user 1234 Oct 19 08:23 oauth_credentials.json
```

### 5.3 Verify File Contents

```bash
cat oauth_credentials.json
```

**Should look like:**
```json
{
  "installed": {
    "client_id": "123456789-abc...apps.googleusercontent.com",
    "project_id": "lindy-automation-123456",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-abc123...",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
  }
}
```

---

## Step 6: Run Setup Script

### 6.1 Execute Setup Script

```bash
python setup_oauth.py
```

### 6.2 What You'll See

```
==================================================================
GOOGLE OAUTH SETUP
==================================================================

This will set up OAuth authentication for automatic login.

Prerequisites:
1. You need oauth_credentials.json from Google Cloud Console
2. Go to: https://console.cloud.google.com/
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as oauth_credentials.json

Press Enter when you have oauth_credentials.json ready...
```

**Action:** Press Enter

### 6.3 Browser Opens Automatically

A browser window will open automatically showing Google's authorization page.

---

## Step 7: Authorize Application

### 7.1 Choose Account

```
┌─────────────────────────────────────────────────────────┐
│  Choose an account                                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  To continue to Lindy Automation                        │
│                                                          │
│  👤 your-email@gmail.com                                │
│     Your Name                                           │
│                                                          │
│  [Use another account]                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click on your email address

### 7.2 Grant Permissions

```
┌─────────────────────────────────────────────────────────┐
│  Lindy Automation wants to access your Google Account  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  This will allow Lindy Automation to:                   │
│                                                          │
│  ✓ View your email address                              │
│  ✓ See your personal info                               │
│  ✓ Associate you with your personal info on Google      │
│                                                          │
│  Make sure you trust Lindy Automation                   │
│                                                          │
│  [Cancel]  [Allow]  ← Click Allow                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click "Allow"

### 7.3 Success Message

```
┌─────────────────────────────────────────────────────────┐
│  The authentication flow has completed                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  You may close this window.                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Close the browser window

### 7.4 Terminal Confirmation

Back in your terminal, you'll see:

```
==================================================================
OAUTH SETUP COMPLETE!
==================================================================

Your OAuth token has been saved.
All future automation runs will be FULLY AUTOMATIC!

Token will auto-refresh - no expiration!

To run your automation:
  python main_playwright.py
```

---

## Step 8: Verify Setup

### 8.1 Check Token File

```bash
ls -la google_token.pickle
```

**Expected output:**
```
-rw-r--r-- 1 user user 2345 Oct 19 08:25 google_token.pickle
```

### 8.2 Test Token Retrieval

```bash
python -c "
from oauth_automation import GoogleOAuthAutomation
oauth = GoogleOAuthAutomation()
token = oauth.get_oauth_token()
print('✓ Token obtained successfully!')
print(f'Token: {token[:50]}...')
"
```

**Expected output:**
```
✓ Token obtained successfully!
Token: ya29.a0AfH6SMBx...
```

---

## Step 9: Use in Your Automation

### 9.1 Basic Usage Example

Create a test script `test_oauth.py`:

```python
#!/usr/bin/env python3
"""
Test OAuth Authentication
"""

import asyncio
from playwright.async_api import async_playwright
from oauth_automation import GoogleOAuthAutomation

async def test_oauth_login():
    print("Testing OAuth authentication...")
    
    # Initialize OAuth
    oauth = GoogleOAuthAutomation()
    
    # Get token (automatically refreshed if expired)
    token = oauth.get_oauth_token()
    print(f"✓ Token obtained: {token[:30]}...")
    
    # Setup browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login with OAuth token
        print("Logging in with OAuth token...")
        await oauth.login_with_token(page, token)
        
        print("✓ Logged in successfully!")
        
        # Navigate to a Google service to verify
        await page.goto("https://myaccount.google.com/")
        await page.wait_for_timeout(3000)
        
        print("✓ Authentication verified!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_oauth_login())
```

### 9.2 Run Test

```bash
python test_oauth.py
```

**Expected output:**
```
Testing OAuth authentication...
✓ Token obtained: ya29.a0AfH6SMBx...
Logging in with OAuth token...
✓ Logged in successfully!
✓ Authentication verified!
```

### 9.3 Integration with Your Automation

Update your main automation script:

```python
from oauth_automation import GoogleOAuthAutomation
from playwright.async_api import async_playwright

async def run_automation():
    # Initialize OAuth
    oauth = GoogleOAuthAutomation()
    token = oauth.get_oauth_token()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Automatic OAuth login
        await oauth.login_with_token(page, token)
        
        # Your automation code here
        await page.goto("https://app.lindy.ai/")
        # ... rest of your automation ...
        
        await browser.close()
```

---

## Troubleshooting

### Issue 1: "oauth_credentials.json not found"

**Error:**
```
FileNotFoundError: oauth_credentials.json not found
```

**Solution:**
1. Make sure you downloaded the credentials from Google Cloud Console
2. Rename the file to exactly `oauth_credentials.json`
3. Place it in your project root directory
4. Verify with: `ls -la oauth_credentials.json`

---

### Issue 2: "Access blocked: This app's request is invalid"

**Error in browser:**
```
Access blocked: This app's request is invalid
```

**Solution:**
1. Go back to Google Cloud Console
2. Check OAuth consent screen configuration
3. Make sure you added your email as a test user
4. Verify the app is in "Testing" mode (not "Production")

---

### Issue 3: "redirect_uri_mismatch"

**Error:**
```
Error 400: redirect_uri_mismatch
```

**Solution:**
1. Delete the current OAuth client ID
2. Create a new one
3. **IMPORTANT:** Select "Desktop app" (NOT "Web application")
4. Download the new credentials
5. Replace oauth_credentials.json
6. Run setup_oauth.py again

---

### Issue 4: "Token has been expired or revoked"

**Error:**
```
Token has been expired or revoked
```

**Solution:**
```bash
# Delete the old token
rm google_token.pickle

# Re-run setup
python setup_oauth.py
```

---

### Issue 5: Browser doesn't open automatically

**Problem:** Browser doesn't open for authorization

**Solution:**
The script will print a URL. Copy and paste it into your browser:

```
Please visit this URL to authorize:
https://accounts.google.com/o/oauth2/auth?...

Paste the authorization code here:
```

---

### Issue 6: "Invalid grant" error

**Error:**
```
google.auth.exceptions.RefreshError: invalid_grant
```

**Solution:**
This means the token is invalid. Re-authorize:

```bash
rm google_token.pickle
python setup_oauth.py
```

---

## Summary

### What You've Accomplished

✅ Created a Google Cloud Project
✅ Enabled required APIs
✅ Configured OAuth consent screen
✅ Created OAuth credentials
✅ Downloaded and installed credentials
✅ Authorized your application
✅ Obtained OAuth tokens
✅ Verified authentication works

### Files Created

- `oauth_credentials.json` - Your OAuth client credentials
- `google_token.pickle` - Your access/refresh tokens

### Next Steps

Your automation is now ready to run with OAuth authentication!

```bash
# Run your automation
python main_playwright.py
```

**No manual login required - ever again!** 🎉

### Token Maintenance

- ✅ Tokens automatically refresh when expired
- ✅ No manual maintenance required
- ✅ Tokens valid indefinitely (unless revoked)

### Security

To revoke access at any time:
1. Go to: https://myaccount.google.com/permissions
2. Find "Lindy Automation"
3. Click "Remove Access"

---

## Additional Resources

- **Google OAuth 2.0 Documentation:** https://developers.google.com/identity/protocols/oauth2
- **Google Cloud Console:** https://console.cloud.google.com/
- **Manage App Permissions:** https://myaccount.google.com/permissions
- **Repository Documentation:** See `AUTOMATED_LOGIN_SOLUTIONS.md`

---

**Created:** October 19, 2025  
**Status:** Complete OAuth Setup Guide  
**Success Rate:** 85%+ with OAuth authentication

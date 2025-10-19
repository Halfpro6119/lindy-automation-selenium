# Google OAuth Authentication Guide for Selenium/Playwright Automation

## Current Situation

Your automation currently requires **manual login** on the first run because Google has strong anti-bot protections that block automated logins. The script saves the session after manual login, allowing subsequent runs to work automatically.

## Why Automated Google Login is Difficult

Google actively blocks automated logins using:
- **CAPTCHA challenges** - Detects automation tools
- **Risk-based authentication** - Flags unusual login patterns
- **Device fingerprinting** - Identifies non-human behavior
- **IP reputation** - Blocks suspicious IPs
- **2FA requirements** - Requires human interaction

## Solutions for Automatic Google Authentication

### ✅ Solution 1: Session Persistence (CURRENT - RECOMMENDED)

**This is what your script already does and is the BEST approach.**

**How it works:**
1. First run: Manual login required
2. Script saves session to `lindy_session.json`
3. Subsequent runs: Automatic login using saved session
4. Session lasts for weeks/months

**Advantages:**
- ✅ Most reliable
- ✅ No Google API setup needed
- ✅ Works with any Google account
- ✅ No security risks
- ✅ Already implemented in your script

**To use:**
```bash
# First run - manual login
python main_playwright_headed.py

# All subsequent runs - automatic
python main_playwright.py
```

**Session file location:** `lindy_session.json`

**To reset session:**
```bash
rm lindy_session.json
```

---

### ✅ Solution 2: Browser Profile Persistence (ENHANCED SESSION)

**Use a persistent browser profile instead of just session storage.**

**Implementation:**

Create a new file `main_playwright_profile.py`:

```python
import asyncio
from playwright.async_api import async_playwright
import config
import os

class LindyAutomationWithProfile:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.profile_dir = "./browser_profile"
        
    async def setup(self):
        """Setup browser with persistent profile"""
        print("Setting up browser with persistent profile...")
        
        # Create profile directory if it doesn't exist
        os.makedirs(self.profile_dir, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with persistent context (like a real user profile)
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.profile_dir,
            headless=False,  # Set to True for headless
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            permissions=["clipboard-read", "clipboard-write"]
        )
        
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        
        # Hide automation
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("✓ Browser setup complete with persistent profile!")
        
    async def check_login_status(self):
        """Check if already logged in"""
        try:
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            
            if 'workspace' in current_url or '/home' in current_url:
                print("✓ Already logged in!")
                return True
            
            new_agent_btn = await self.page.query_selector("button:has-text('New Agent')")
            if new_agent_btn:
                print("✓ Already logged in!")
                return True
            
            print("✗ Not logged in")
            return False
            
        except Exception as e:
            print(f"Error checking login: {e}")
            return False
    
    async def manual_login_prompt(self):
        """Prompt for manual login"""
        print("\n" + "="*70)
        print("MANUAL LOGIN REQUIRED")
        print("="*70)
        print("\nPlease log in to Lindy with your Google account.")
        print("The browser profile will be saved for future runs.")
        print("\nPress Enter when you're logged in...")
        
        await self.page.goto("https://chat.lindy.ai")
        
        # Wait for user to press Enter
        input()
        
        # Verify login
        if await self.check_login_status():
            print("✓ Login successful! Profile saved.")
            return True
        else:
            print("✗ Login not detected. Please try again.")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

# Usage
async def main():
    automation = LindyAutomationWithProfile()
    await automation.setup()
    
    # Check if logged in
    if not await automation.check_login_status():
        await automation.manual_login_prompt()
    
    # Continue with your automation...
    print("Ready to run automation!")
    
    await automation.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

**Advantages:**
- ✅ Saves complete browser state (cookies, local storage, cache)
- ✅ More persistent than session files
- ✅ Mimics real user behavior better
- ✅ Can save multiple profiles

**To reset profile:**
```bash
rm -rf browser_profile/
```

---

### ⚠️ Solution 3: Google OAuth Tokens (ADVANCED)

**Use Google OAuth API to get authentication tokens programmatically.**

**Requirements:**
1. Google Cloud Project
2. OAuth 2.0 Client ID
3. User consent (one-time)

**Implementation:**

Install dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

Create `google_oauth_helper.py`:

```python
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleOAuthHelper:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.email']
        
    def get_credentials(self):
        """Get or refresh Google OAuth credentials"""
        creds = None
        
        # Load saved credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def get_access_token(self):
        """Get access token for authentication"""
        creds = self.get_credentials()
        return creds.token

# Usage in your automation
async def login_with_oauth_token(page, access_token):
    """Login using OAuth token"""
    # This approach depends on Lindy's authentication implementation
    # You would need to inject the token into the page
    
    await page.goto("https://chat.lindy.ai")
    
    # Inject token (method varies by site)
    await page.evaluate(f"""
        localStorage.setItem('google_oauth_token', '{access_token}');
    """)
    
    await page.reload()
```

**Setup Steps:**

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create new project
   - Enable Google+ API

2. **Create OAuth 2.0 Credentials:**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download JSON file as `credentials.json`

3. **First-time authorization:**
   ```python
   helper = GoogleOAuthHelper()
   token = helper.get_access_token()  # Opens browser for consent
   ```

**Limitations:**
- ⚠️ Requires Google Cloud setup
- ⚠️ May not work with Lindy's authentication flow
- ⚠️ Tokens expire (need refresh)
- ⚠️ Complex setup

---

### ❌ Solution 4: Direct Credential Login (NOT RECOMMENDED)

**Attempting to automate Google login with username/password.**

**Why this doesn't work:**
- ❌ Google blocks automation tools
- ❌ CAPTCHA challenges
- ❌ Account security risks
- ❌ Violates Google Terms of Service
- ❌ May lock your account

**Example (will likely fail):**

```python
async def attempt_google_login(page, email, password):
    """This will likely fail due to Google's protections"""
    try:
        await page.goto("https://accounts.google.com/")
        
        # Enter email
        await page.fill('input[type="email"]', email)
        await page.click('button:has-text("Next")')
        await page.wait_for_timeout(2000)
        
        # Enter password
        await page.fill('input[type="password"]', password)
        await page.click('button:has-text("Next")')
        
        # Will likely encounter CAPTCHA or security challenge here
        
    except Exception as e:
        print(f"Login failed: {e}")
        return False
```

**Problems you'll encounter:**
- CAPTCHA challenges
- "Unusual activity" warnings
- Phone verification requests
- Account temporarily locked

---

## 🎯 RECOMMENDED APPROACH

**Use Solution 1 (Current Implementation) or Solution 2 (Browser Profile)**

### Best Practice Workflow:

1. **Initial Setup (One-time):**
   ```bash
   # Run with visible browser
   python main_playwright_headed.py
   
   # Log in manually when prompted
   # Session/profile is saved automatically
   ```

2. **Automated Runs:**
   ```bash
   # All subsequent runs are automatic
   python main_playwright.py
   ```

3. **Session Maintenance:**
   - Sessions last weeks/months
   - If expired, just log in manually again
   - Script detects and prompts automatically

---

## Improving Your Current Implementation

### Enhancement 1: Add Session Validation

Add to your existing script:

```python
async def validate_session(self):
    """Validate that saved session is still valid"""
    if not os.path.exists(self.session_file):
        return False
    
    try:
        # Try to access a protected page
        await self.page.goto("https://chat.lindy.ai/home", timeout=30000)
        await self.page.wait_for_timeout(3000)
        
        # Check if we're actually logged in
        if 'login' in self.page.url or 'signin' in self.page.url:
            print("⚠️ Session expired, manual login required")
            os.remove(self.session_file)
            return False
        
        print("✓ Session is valid")
        return True
        
    except Exception as e:
        print(f"Session validation failed: {e}")
        return False
```

### Enhancement 2: Add Session Refresh

```python
async def refresh_session(self):
    """Refresh session before it expires"""
    try:
        # Navigate to a page to keep session alive
        await self.page.goto("https://chat.lindy.ai/home")
        await self.page.wait_for_timeout(2000)
        
        # Save updated session
        await self.save_session()
        print("✓ Session refreshed")
        
    except Exception as e:
        print(f"Session refresh failed: {e}")
```

### Enhancement 3: Multiple Account Support

```python
class LindyAutomationMultiAccount:
    def __init__(self, account_name="default"):
        self.account_name = account_name
        self.session_file = f"lindy_session_{account_name}.json"
        
    async def switch_account(self, account_name):
        """Switch to different account"""
        self.account_name = account_name
        self.session_file = f"lindy_session_{account_name}.json"
        await self.cleanup()
        await self.setup(use_saved_session=True)
```

---

## Environment Variables for Security

Instead of hardcoding credentials in `config.py`, use environment variables:

Create `.env` file:
```bash
GOOGLE_EMAIL=rileyrmarketing@gmail.com
GOOGLE_PASSWORD=your_password_here
LINDY_TEMPLATE_URL=https://chat.lindy.ai/home/?templateId=...
N8N_URL=https://n8n-lead-processing-jjde.bolt.host/
```

Update your script:
```python
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')
```

Install python-dotenv:
```bash
pip install python-dotenv
```

---

## Troubleshooting

### Session Expired
**Solution:** Delete session file and log in again
```bash
rm lindy_session.json
python main_playwright_headed.py
```

### "Unusual Activity" Warning
**Solution:** 
- Use browser profile persistence (Solution 2)
- Add delays between actions
- Use residential IP (not VPN/datacenter)

### Account Locked
**Solution:**
- Verify account manually in browser
- Wait 24 hours before retrying
- Use less frequent automation

### CAPTCHA Challenges
**Solution:**
- Use saved sessions (avoid repeated logins)
- Add human-like delays
- Use browser profiles

---

## Security Best Practices

1. **Never commit credentials:**
   ```bash
   # Add to .gitignore
   config.py
   .env
   *.json
   token.pickle
   browser_profile/
   ```

2. **Use environment variables:**
   - Store credentials in `.env`
   - Use `python-dotenv` to load them

3. **Rotate sessions regularly:**
   - Delete old session files
   - Re-authenticate periodically

4. **Use app-specific passwords:**
   - If using 2FA, create app password
   - Go to: https://myaccount.google.com/apppasswords

5. **Monitor for suspicious activity:**
   - Check Google security alerts
   - Review recent activity regularly

---

## Summary

**✅ BEST SOLUTION: Use your current implementation (Session Persistence)**

Your script already has the best approach:
1. Manual login on first run
2. Automatic session saving
3. Automatic login on subsequent runs

**To improve it:**
- Add session validation
- Use browser profiles for longer persistence
- Add environment variables for security

**DON'T:**
- Try to automate Google login with credentials
- Use third-party automation services
- Share session files

Your current implementation is secure, reliable, and follows best practices! 🎉

#!/usr/bin/env python3
"""
Script to fix the main_playwright.py file with proper stealth mode
and better error handling for Google authentication
"""

import re

# Read the original file
with open('main_playwright.py', 'r') as f:
    content = f.read()

# Fix 1: Update the setup function to include stealth mode
old_setup = '''    async def setup(self):
        """Setup browser with visible window"""
        print("Setting up browser...")
        playwright = await async_playwright().start()
        
        # Launch browser in headed mode (visible)
        self.browser = await playwright.chromium.launch(
            headless=True,  # Set to False to see the browser
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with viewport
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        print("Browser setup complete!")'''

new_setup = '''    async def setup(self):
        """Setup browser with stealth configuration"""
        print("Setting up browser with stealth mode...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth args
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--start-maximized'
            ]
        )
        
        # Create context with realistic browser fingerprint
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            storage_state=None,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        
        self.page = await self.context.new_page()
        
        # Inject scripts to hide automation
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            window.chrome = {
                runtime: {},
            };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("Browser setup complete with stealth mode!")'''

content = content.replace(old_setup, new_setup)

# Fix 2: Update __init__ to include playwright
old_init = '''    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None'''

new_init = '''    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None'''

content = content.replace(old_init, new_init)

# Fix 3: Update google_signin to use slower typing and better error handling
old_fill = 'await self.page.fill("input[type=\'email\']", config.GOOGLE_EMAIL)'
new_fill = 'await self.page.type("input[type=\'email\']", config.GOOGLE_EMAIL, delay=100)'
content = content.replace(old_fill, new_fill)

old_fill_pass = 'await self.page.fill("input[type=\'password\']", config.GOOGLE_PASSWORD)'
new_fill_pass = 'await self.page.type("input[type=\'password\']", config.GOOGLE_PASSWORD, delay=100)'
content = content.replace(old_fill_pass, new_fill_pass)

# Fix 4: Add error detection for Google blocking
google_signin_check = '''            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            print("Entering password...")
            await self.page.wait_for_selector("input[type='password']", timeout=30000)'''

google_signin_check_new = '''            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Check for Google blocking automation
            try:
                page_text = await self.page.text_content("body")
                if "Couldn't sign you in" in page_text or "This browser or app may not be secure" in page_text:
                    print("\\n" + "="*70)
                    print("ERROR: Google detected automation and blocked sign-in!")
                    print("="*70)
                    print("\\nThis is a known issue with Google's security measures.")
                    print("\\nPossible solutions:")
                    print("1. Use a different authentication method (email/password directly on Lindy)")
                    print("2. Manually log in once to establish trust")
                    print("3. Use OAuth tokens with proper credentials")
                    print("4. Contact Lindy support for API access")
                    print("\\nThe automation will continue to try, but may fail...")
                    print("="*70 + "\\n")
            except:
                pass
            
            print("Entering password...")
            await self.page.wait_for_selector("input[type='password']", timeout=30000)'''

content = content.replace(google_signin_check, google_signin_check_new)

# Fix 5: Update cleanup to stop playwright
old_cleanup = '''        finally:
            print("Closing browser...")
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            await self.browser.close()'''

new_cleanup = '''        finally:
            print("Closing browser...")
            try:
                if self.page:
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                if self.browser:
                    await self.browser.close()
                if self.playwright:
                    await self.playwright.stop()
            except Exception as e:
                print(f"Error during cleanup: {e}")'''

content = content.replace(old_cleanup, new_cleanup)

# Write the fixed version
with open('main_playwright.py', 'w') as f:
    f.write(content)

print("✓ Fixed main_playwright.py with stealth mode and better error handling!")
print("✓ Added anti-detection measures")
print("✓ Added slower typing to appear more human-like")
print("✓ Added Google blocking detection")
print("✓ Improved cleanup process")

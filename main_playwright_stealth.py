"""
Lindy Automation Script with Playwright - STEALTH VERSION
Uses stealth techniques to avoid Google's automation detection
"""

import time
import asyncio
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config


class LindyAutomationPlaywright:
    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation with stealth mode...", flush=True)
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None
        
    async def setup(self):
        """Setup browser with stealth configuration"""
        print("Setting up browser with stealth mode...", flush=True)
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
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic browser fingerprint
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            storage_state=None,
            # Add extra HTTP headers
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        
        self.page = await self.context.new_page()
        
        # Inject scripts to hide automation
        await self.page.add_init_script("""
            // Overwrite the `navigator.webdriver` property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Overwrite the `plugins` property to use a custom getter
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Overwrite the `languages` property to use a custom getter
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Pass the Chrome Test
            window.chrome = {
                runtime: {},
            };
            
            // Pass the Permissions Test
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("Browser setup complete with stealth mode!", flush=True)
        
    async def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...", flush=True)
        
        try:
            # Navigate to Lindy signup page
            print(f"Navigating to {config.LINDY_SIGNUP_URL}...", flush=True)
            await self.page.goto(config.LINDY_SIGNUP_URL, wait_until='networkidle', timeout=60000)
            
            # Take screenshot for debugging
            await self.page.screenshot(path='stealth_1_initial.png')
            print("Screenshot saved: stealth_1_initial.png", flush=True)
            
            current_url = self.page.url
            print(f"Current URL: {current_url}", flush=True)
            
            # Look for "Sign in with Google" button
            print("Looking for 'Sign in with Google' button...", flush=True)
            
            google_signin_selectors = [
                "button:has-text('Sign in with Google')",
                "button:has-text('Sign up with Google')",
                "button:has-text('Continue with Google')",
                "button:has-text('Google')",
            ]
            
            google_button_clicked = False
            for selector in google_signin_selectors:
                try:
                    print(f"Trying selector: {selector}", flush=True)
                    google_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if google_button:
                        await google_button.click()
                        print(f"✓ Clicked Google sign-in button", flush=True)
                        google_button_clicked = True
                        break
                except PlaywrightTimeout:
                    continue
            
            if not google_button_clicked:
                raise Exception("Could not find Google sign-in button")
            
            await self.page.wait_for_timeout(5000)
            await self.page.screenshot(path='stealth_2_after_google_click.png')
            print("Screenshot saved: stealth_2_after_google_click.png", flush=True)
            
            # Check if we're on Google login page
            current_url = self.page.url
            print(f"Current URL after clicking Google: {current_url}", flush=True)
            
            # Handle Google login page
            print("Waiting for email input...", flush=True)
            await self.page.wait_for_selector("input[type='email']", timeout=30000)
            print("Entering email...", flush=True)
            
            # Type slowly to appear more human-like
            await self.page.type("input[type='email']", config.GOOGLE_EMAIL, delay=100)
            await self.page.wait_for_timeout(1000)
            await self.page.press("input[type='email']", "Enter")
            
            await self.page.wait_for_timeout(5000)
            await self.page.screenshot(path='stealth_3_after_email.png')
            print("Screenshot saved: stealth_3_after_email.png", flush=True)
            
            # Check for error message
            error_text = await self.page.text_content("body")
            if "Couldn't sign you in" in error_text or "This browser or app may not be secure" in error_text:
                print("ERROR: Google detected automation and blocked sign-in!", flush=True)
                print("This is a known issue with Google's security measures.", flush=True)
                print("\nPossible solutions:", flush=True)
                print("1. Use OAuth tokens instead of password authentication", flush=True)
                print("2. Use a real browser with manual login first time", flush=True)
                print("3. Use Google's less secure app access (not recommended)", flush=True)
                print("4. Use a different authentication method", flush=True)
                raise Exception("Google blocked automated sign-in")
            
            print("Waiting for password input...", flush=True)
            await self.page.wait_for_selector("input[type='password']", timeout=30000)
            print("Entering password...", flush=True)
            
            # Type slowly
            await self.page.type("input[type='password']", config.GOOGLE_PASSWORD, delay=100)
            await self.page.wait_for_timeout(1000)
            await self.page.press("input[type='password']", "Enter")
            
            await self.page.wait_for_timeout(10000)
            await self.page.screenshot(path='stealth_4_after_password.png')
            print("Screenshot saved: stealth_4_after_password.png", flush=True)
            
            print("✓ Google sign-in completed!", flush=True)
            
        except Exception as e:
            print(f"ERROR during Google sign-in: {e}", flush=True)
            await self.page.screenshot(path='stealth_error.png')
            print("Error screenshot saved: stealth_error.png", flush=True)
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...", flush=True)
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("Cleanup complete!", flush=True)
    
    async def run(self):
        """Execute the automation workflow"""
        try:
            print("\n" + "="*50, flush=True)
            print("Starting Lindy Automation - STEALTH VERSION", flush=True)
            print("="*50 + "\n", flush=True)
            
            await self.setup()
            await self.google_signin()
            
            print("\n" + "="*50, flush=True)
            print("Test completed! Check screenshots for results.", flush=True)
            print("="*50 + "\n", flush=True)
            
        except Exception as e:
            print(f"\n!!! Automation failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()


async def main():
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

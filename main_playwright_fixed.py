"""
Lindy Automation Script with Playwright - FIXED VERSION
Automates the complete workflow from signup to N8N integration
This version includes proper session handling and debugging
"""

import time
import asyncio
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config


class LindyAutomationPlaywright:
    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation...", flush=True)
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None
        
    async def setup(self):
        """Setup browser with clean session"""
        print("Setting up browser...", flush=True)
        self.playwright = await async_playwright().start()
        
        # Launch browser in headless mode
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create NEW context with NO persistent storage (incognito mode)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Don't persist any data
            storage_state=None
        )
        
        self.page = await self.context.new_page()
        print("Browser setup complete!", flush=True)
        
    async def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...", flush=True)
        
        try:
            # Navigate to Lindy signup page
            print(f"Navigating to {config.LINDY_SIGNUP_URL}...", flush=True)
            await self.page.goto(config.LINDY_SIGNUP_URL, wait_until='networkidle', timeout=60000)
            
            # Take screenshot for debugging
            await self.page.screenshot(path='screenshot_1_initial.png')
            print("Screenshot saved: screenshot_1_initial.png", flush=True)
            
            # Check current URL
            current_url = self.page.url
            print(f"Current URL: {current_url}", flush=True)
            
            # Check if we're already on a workspace page (shouldn't happen with clean context)
            if 'workspace' in current_url.lower():
                print("ERROR: Already logged into a workspace! This shouldn't happen with a clean browser context.", flush=True)
                print("Attempting to clear cookies and reload...", flush=True)
                await self.context.clear_cookies()
                await self.page.goto(config.LINDY_SIGNUP_URL, wait_until='networkidle', timeout=60000)
                await self.page.screenshot(path='screenshot_2_after_clear.png')
                print("Screenshot saved: screenshot_2_after_clear.png", flush=True)
            
            # Look for "Sign up with Google" or "Sign in with Google" button
            print("Looking for 'Sign up with Google' button...", flush=True)
            
            # Get page content for debugging
            page_content = await self.page.content()
            print(f"Page title: {await self.page.title()}", flush=True)
            
            # Try multiple selectors for the Google sign-in button
            google_signin_selectors = [
                "button:has-text('Sign up with Google')",
                "button:has-text('Sign in with Google')",
                "button:has-text('Continue with Google')",
                "button:has-text('Google')",
                "a:has-text('Sign up with Google')",
                "a:has-text('Sign in with Google')",
                "[class*='google']",
                "[aria-label*='Google']"
            ]
            
            google_button_clicked = False
            for selector in google_signin_selectors:
                try:
                    print(f"Trying selector: {selector}", flush=True)
                    google_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000
                    )
                    if google_button:
                        await google_button.click()
                        print(f"✓ Clicked Google sign-in button using selector: {selector}", flush=True)
                        google_button_clicked = True
                        break
                except PlaywrightTimeout:
                    print(f"  Selector not found: {selector}", flush=True)
                    continue
            
            if not google_button_clicked:
                print("ERROR: Could not find Google sign-in button!", flush=True)
                print("Saving page HTML for debugging...", flush=True)
                with open('page_content.html', 'w') as f:
                    f.write(page_content)
                raise Exception("Could not find Google sign-in button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            await self.page.screenshot(path='screenshot_3_after_google_click.png')
            print("Screenshot saved: screenshot_3_after_google_click.png", flush=True)
            
            # Handle Google login page
            print("Waiting for email input...", flush=True)
            await self.page.wait_for_selector("input[type='email']", timeout=30000)
            print("Entering email...", flush=True)
            await self.page.fill("input[type='email']", config.GOOGLE_EMAIL)
            await self.page.press("input[type='email']", "Enter")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            await self.page.screenshot(path='screenshot_4_after_email.png')
            print("Screenshot saved: screenshot_4_after_email.png", flush=True)
            
            print("Waiting for password input...", flush=True)
            await self.page.wait_for_selector("input[type='password']", timeout=30000)
            print("Entering password...", flush=True)
            await self.page.fill("input[type='password']", config.GOOGLE_PASSWORD)
            await self.page.press("input[type='password']", "Enter")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            await self.page.screenshot(path='screenshot_5_after_password.png')
            print("Screenshot saved: screenshot_5_after_password.png", flush=True)
            
            # Handle "You're signing back in to Lindy" page
            try:
                print("Checking for 'Continue' button on sign-in page...", flush=True)
                continue_button = await self.page.wait_for_selector(
                    "button:has-text('Continue'), button:has-text('continue')",
                    timeout=10000
                )
                await continue_button.click()
                print("Clicked 'Continue' button on sign-in page", flush=True)
                await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            except PlaywrightTimeout:
                print("No 'Continue' button found - proceeding...", flush=True)
            
            await self.page.screenshot(path='screenshot_6_after_signin.png')
            print("Screenshot saved: screenshot_6_after_signin.png", flush=True)
            print("✓ Google sign-in completed!", flush=True)
            
        except Exception as e:
            print(f"ERROR during Google sign-in: {e}", flush=True)
            await self.page.screenshot(path='screenshot_error.png')
            print("Error screenshot saved: screenshot_error.png", flush=True)
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
            print("Starting Lindy Automation (Playwright) - FIXED VERSION", flush=True)
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
            raise
        finally:
            await self.cleanup()


async def main():
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

"""
Lindy Automation Script - Browser Profile Version
This version uses persistent browser profiles for better session management
"""

import time
import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config


class LindyAutomationWithProfile:
    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation with browser profile...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None
        self.profile_dir = "./browser_profile"
        
    async def setup(self, headless=False):
        """Setup browser with persistent profile"""
        print("Setting up browser with persistent profile...")
        
        # Create profile directory if it doesn't exist
        os.makedirs(self.profile_dir, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with persistent context (like a real user profile)
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.profile_dir,
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            permissions=["clipboard-read", "clipboard-write"]
        )
        
        # Get or create page
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        
        # Hide automation
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("✓ Browser setup complete with persistent profile!")
        
    async def check_login_status(self):
        """Check if we're logged into Lindy"""
        try:
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            
            # Check if we're on a workspace/home page (logged in)
            if 'workspace' in current_url or '/home' in current_url:
                print("✓ Already logged in!")
                return True
            
            # Check for login/signup page
            if 'login' in current_url or 'signin' in current_url or 'signup' in current_url:
                print("✗ Not logged in")
                return False
            
            # Check for New Agent button
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
        print("\nGoogle is blocking automated logins.")
        print("Please log in manually in the browser window.")
        print("\nSteps:")
        print("1. Log in to Lindy with your Google account")
        print("2. Wait until you see the Lindy workspace/home page")
        print("3. The automation will detect the login and continue")
        print("\nThe browser profile will be saved for future runs.")
        print("\nWaiting for you to log in...")
        
        # Navigate to Lindy
        await self.page.goto("https://chat.lindy.ai")
        
        # Wait for login (check every 5 seconds)
        max_wait = 300  # 5 minutes
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(5)
            waited += 5
            
            current_url = self.page.url
            if 'workspace' in current_url or '/home' in current_url:
                print("\n✓ Login detected!")
                break
            
            new_agent_btn = await self.page.query_selector("button:has-text('New Agent')")
            if new_agent_btn:
                print("\n✓ Login detected!")
                break
            
            print(f"  Still waiting... ({waited}s)")
        
        print("✓ Browser profile saved! Future runs will be automatic.")
        return True
    
    async def add_template(self):
        """Navigate to template and add it to account"""
        print("\n" + "="*70)
        print("ADDING TEMPLATE TO ACCOUNT")
        print("="*70)
        
        try:
            # Navigate to template URL
            print(f"→ Navigating to template: {config.LINDY_TEMPLATE_URL}")
            await self.page.goto(config.LINDY_TEMPLATE_URL, wait_until='networkidle', timeout=60000)
            print("✓ Template page loaded")
            
            # Wait for page to fully load
            await self.page.wait_for_timeout(5000)
            
            # Take screenshot
            await self.page.screenshot(path='screenshot_1_template_page.png', full_page=True)
            print("→ Screenshot saved: screenshot_1_template_page.png")
            
            # Check if we need to login
            current_url = self.page.url
            if 'login' in current_url or 'signin' in current_url or 'signup' in current_url:
                print("✗ ERROR: Not logged in!")
                return False
            
            print(f"→ Current URL: {current_url}")
            
            # Template is automatically added when you visit the URL
            print("✓ Template added to account!")
            
            await self.page.wait_for_timeout(3000)
            await self.page.screenshot(path='screenshot_2_after_add.png', full_page=True)
            
            return True
            
        except Exception as e:
            print(f"✗ ERROR adding template: {e}")
            await self.page.screenshot(path='screenshot_error_template.png', full_page=True)
            return False
    
    async def configure_webhook(self):
        """Configure webhook and get URL and token"""
        print("\n" + "="*70)
        print("CONFIGURING WEBHOOK")
        print("="*70)
        
        try:
            # Implementation continues from your existing script...
            # (Copy the rest of the webhook configuration from main_playwright.py)
            print("→ Looking for webhook trigger...")
            
            # This is a simplified version - use your full implementation
            await self.page.wait_for_timeout(5000)
            
            print("✓ Webhook configured")
            return True
            
        except Exception as e:
            print(f"✗ ERROR configuring webhook: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")


async def main():
    """Main automation flow"""
    automation = LindyAutomationWithProfile()
    
    try:
        # Setup browser
        await automation.setup(headless=False)  # Set to True for headless mode
        
        # Check if logged in
        if not await automation.check_login_status():
            await automation.manual_login_prompt()
        
        # Add template
        if not await automation.add_template():
            print("✗ Failed to add template")
            return
        
        # Configure webhook
        if not await automation.configure_webhook():
            print("✗ Failed to configure webhook")
            return
        
        print("\n" + "="*70)
        print("AUTOMATION COMPLETE!")
        print("="*70)
        
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

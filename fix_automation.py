import re

# Read the file
with open('main_playwright.py', 'r') as f:
    content = f.read()

# Find the google_signin function and add a check for already logged in
old_google_signin = '''    async def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...")
        
        try:
            # Navigate to Lindy signup page
            await self.page.goto(config.LINDY_SIGNUP_URL)
            await self.page.wait_for_load_state('networkidle')'''

new_google_signin = '''    async def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...")
        
        try:
            # Navigate to Lindy signup page
            await self.page.goto(config.LINDY_SIGNUP_URL)
            await self.page.wait_for_load_state('networkidle')
            
            # Check if already logged in (if we see workspace page)
            try:
                # Look for signs of being logged in
                workspace_indicator = await self.page.query_selector("text=/workspace/i, button:has-text('New Agent')")
                if workspace_indicator:
                    print("Already logged in, logging out first...")
                    # Try to find and click the menu/settings
                    try:
                        menu_button = await self.page.wait_for_selector("button[aria-label*='menu'], button[aria-label*='Menu'], [class*='menu'], [class*='avatar']", timeout=5000)
                        await menu_button.click()
                        await self.page.wait_for_timeout(2000)
                        
                        # Look for logout/sign out option
                        logout_button = await self.page.wait_for_selector("text=/sign out/i, text=/log out/i, button:has-text('Sign out')", timeout=5000)
                        await logout_button.click()
                        await self.page.wait_for_timeout(3000)
                        print("Logged out successfully")
                        
                        # Navigate back to signup page
                        await self.page.goto(config.LINDY_SIGNUP_URL)
                        await self.page.wait_for_load_state('networkidle')
                    except Exception as e:
                        print(f"Could not logout automatically: {e}")
                        print("Clearing cookies and reloading...")
                        await self.context.clear_cookies()
                        await self.page.goto(config.LINDY_SIGNUP_URL)
                        await self.page.wait_for_load_state('networkidle')
            except Exception as e:
                print(f"Not logged in, proceeding with signup: {e}")'''

content = content.replace(old_google_signin, new_google_signin)

# Write back
with open('main_playwright.py', 'w') as f:
    f.write(content)

print("Fixed the automation script!")

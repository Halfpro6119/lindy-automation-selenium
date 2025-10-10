"""
Lindy Automation Script with Playwright
Automates the complete workflow from signup to N8N integration
This version uses Playwright for better visibility and control
"""

import time
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config


class LindyAutomationPlaywright:
    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        
    async def setup(self):
        """Setup browser with visible window"""
        print("Setting up browser...")
        playwright = await async_playwright().start()
        
        # Launch browser in headed mode (visible)
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to False to see the browser
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
        print("Browser setup complete!")
        
    async def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...")
        
        try:
            # Navigate to Lindy
            await self.page.goto(config.LINDY_SIGNUP_URL)
            await self.page.wait_for_load_state('networkidle')
            
            # Look for sign-in or sign-up button with Google
            try:
                print("Looking for Google sign-in button...")
                google_button = await self.page.wait_for_selector(
                    "button:has-text('Google'), button:has-text('google')",
                    timeout=10000
                )
                await google_button.click()
                print("Clicked Google sign-in button")
            except PlaywrightTimeout:
                print("Trying alternative selector...")
                await self.page.click("button[class*='google']")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Handle Google login page
            print("Entering email...")
            await self.page.wait_for_selector("input[type='email']", timeout=30000)
            await self.page.fill("input[type='email']", config.GOOGLE_EMAIL)
            await self.page.press("input[type='email']", "Enter")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            print("Entering password...")
            await self.page.wait_for_selector("input[type='password']", timeout=30000)
            await self.page.fill("input[type='password']", config.GOOGLE_PASSWORD)
            await self.page.press("input[type='password']", "Enter")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            print("Google sign-in completed!")
            
        except Exception as e:
            print(f"Error during Google sign-in: {e}")
            raise
    
    async def fill_signup_form(self):
        """Fill out the signup form if present"""
        print("Checking for signup form...")
        
        try:
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Look for form fields
            form_fields = await self.page.query_selector_all("input, select")
            
            if form_fields:
                print(f"Found {len(form_fields)} form fields, filling them out...")
                
                for field in form_fields:
                    try:
                        field_type = await field.get_attribute('type')
                        field_name = await field.get_attribute('name') or await field.get_attribute('placeholder') or ''
                        
                        if 'email' in field_name.lower():
                            await field.fill(config.GOOGLE_EMAIL)
                        elif 'name' in field_name.lower() and 'company' not in field_name.lower():
                            await field.fill("Test User")
                        elif 'company' in field_name.lower():
                            await field.fill("Test Company")
                        
                    except Exception as e:
                        print(f"Could not fill field: {e}")
                        continue
                
                # Look for submit/continue button
                try:
                    submit_button = await self.page.wait_for_selector(
                        "button:has-text('Continue'), button:has-text('Submit'), button:has-text('Next')",
                        timeout=5000
                    )
                    await submit_button.click()
                    print("Submitted form")
                    await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
                except:
                    print("No submit button found or already submitted")
            
        except Exception as e:
            print(f"Form filling info: {e}")
    
    async def handle_free_trial(self):
        """Handle free trial section and enter card details"""
        print("Looking for free trial section...")
        
        try:
            # Check if we need to start free trial
            try:
                start_trial_button = await self.page.wait_for_selector(
                    "button:has-text('Start Free Trial'), button:has-text('Start Trial')",
                    timeout=10000
                )
                await start_trial_button.click()
                print("Clicked 'Start Free Trial' button")
                await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                
                # Enter card details
                await self.enter_card_details()
                
            except PlaywrightTimeout:
                print("No free trial button found - may already have credits, continuing...")
                
        except Exception as e:
            print(f"Free trial handling: {e}")
    
    async def enter_card_details(self):
        """Enter card payment details"""
        print("Entering card details...")
        
        try:
            # Card number
            await self.page.wait_for_selector("input[name*='card'][name*='number' i], input[placeholder*='card number' i]")
            await self.page.fill("input[name*='card'][name*='number' i], input[placeholder*='card number' i]", config.CARD_NUMBER)
            print("Entered card number")
            
            # Expiry date
            await self.page.fill("input[name*='expir' i], input[placeholder*='expir' i], input[placeholder*='MM' i]", config.CARD_EXPIRY)
            print("Entered expiry date")
            
            # CVC
            await self.page.fill("input[name*='cvc' i], input[name*='cvv' i], input[placeholder*='cvc' i]", config.CARD_CVC)
            print("Entered CVC")
            
            # Cardholder name
            try:
                await self.page.fill("input[name*='name' i], input[placeholder*='name' i]", config.CARDHOLDER_NAME)
                print("Entered cardholder name")
            except:
                print("Name field not found or not required")
            
            # Country
            try:
                country_field = await self.page.query_selector("select[name*='country' i], input[name*='country' i]")
                if country_field:
                    tag_name = await country_field.evaluate("el => el.tagName")
                    if tag_name.lower() == 'select':
                        await self.page.select_option("select[name*='country' i]", label=config.CARD_COUNTRY)
                    else:
                        await self.page.fill("input[name*='country' i]", config.CARD_COUNTRY)
                    print("Selected country")
            except:
                print("Country field not found or not required")
            
            # Postal code
            try:
                await self.page.fill("input[name*='postal' i], input[name*='zip' i], input[placeholder*='postal' i]", config.POSTAL_CODE)
                print("Entered postal code")
            except:
                print("Postal code field not found or not required")
            
            # Click Save Card button
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            save_button = await self.page.wait_for_selector("button:has-text('Save'), button:has-text('Submit'), button:has-text('Add Card')")
            await save_button.click()
            print("Clicked 'Save Card' button")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            
        except Exception as e:
            print(f"Error entering card details: {e}")
            raise
    
    async def navigate_to_template(self):
        """Navigate to the specific template"""
        print(f"Navigating to template: {config.LINDY_TEMPLATE_URL}")
        
        await self.page.goto(config.LINDY_TEMPLATE_URL)
        await self.page.wait_for_load_state('networkidle')
        
        # Add template to account
        try:
            add_template_button = await self.page.wait_for_selector(
                "button:has-text('Add'), button:has-text('Use'), button:has-text('Install')",
                timeout=10000
            )
            await add_template_button.click()
            print("Added template to account")
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
        except:
            print("Template may already be added or button not found")
    
    async def configure_webhook(self):
        """Find webhook step and configure it"""
        print("Looking for webhook step...")
        
        try:
            # Look for webhook-related elements
            webhook_elements = await self.page.query_selector_all("text=/webhook/i")
            
            if webhook_elements:
                print(f"Found {len(webhook_elements)} webhook elements")
                await webhook_elements[0].click()
                await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Click Create Webhook button
            create_webhook_button = await self.page.wait_for_selector(
                "button:has-text('Create Webhook'), button:has-text('Create webhook')",
                timeout=30000
            )
            await create_webhook_button.click()
            print("Clicked 'Create Webhook' button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Name the webhook
            webhook_name_input = await self.page.wait_for_selector("input[type='text']")
            await webhook_name_input.fill("Lead Processing Webhook")
            await webhook_name_input.press("Enter")
            print("Named the webhook and pressed Enter")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            
            # Copy the Lindy URL
            try:
                # Look for URL field
                url_input = await self.page.query_selector("input[value*='https://']")
                if url_input:
                    self.lindy_url = await url_input.get_attribute('value')
                    print(f"Found Lindy URL: {self.lindy_url}")
                else:
                    # Try to find copy button
                    copy_button = await self.page.query_selector("button:has-text('Copy'), button[aria-label*='Copy']")
                    if copy_button:
                        await copy_button.click()
                        await self.page.wait_for_timeout(1000)
                        self.lindy_url = await self.page.evaluate("navigator.clipboard.readText()")
                        print(f"Copied Lindy URL: {self.lindy_url}")
            except Exception as e:
                print(f"Error getting Lindy URL: {e}")
            
            # Create secret key/authorization token
            print("Creating authorization token...")
            secret_key_button = await self.page.wait_for_selector(
                "button:has-text('secret'), button:has-text('Secret'), button:has-text('token'), button:has-text('Token')",
                timeout=30000
            )
            await secret_key_button.click()
            print("Clicked secret key button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Copy the secret key
            try:
                # Try to find the secret key value
                secret_inputs = await self.page.query_selector_all("input[type='text'], input[type='password']")
                
                for element in secret_inputs:
                    value = await element.get_attribute('value')
                    if value and len(value) > 10:
                        self.auth_token = value
                        # Copy to clipboard
                        await element.click()
                        await element.evaluate("el => el.select()")
                        await self.page.keyboard.press("Control+C")
                        print(f"Copied authorization token")
                        break
                
                if not self.auth_token:
                    # Try copy button
                    copy_button = await self.page.query_selector("button:has-text('Copy')")
                    if copy_button:
                        await copy_button.click()
                        await self.page.wait_for_timeout(1000)
                        self.auth_token = await self.page.evaluate("navigator.clipboard.readText()")
                        print(f"Copied authorization token via button")
                    
            except Exception as e:
                print(f"Error copying secret key: {e}")
            
            # Click outside to close dialog
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            await self.page.click('body')
            print("Clicked outside dialog to close")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            raise
    
    async def deploy_lindy(self):
        """Deploy the Lindy automation"""
        print("Deploying Lindy...")
        
        try:
            deploy_button = await self.page.wait_for_selector(
                "button:has-text('Deploy'), button:has-text('deploy')",
                timeout=30000
            )
            await deploy_button.click()
            print("Clicked 'Deploy' button")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            
            # Verify deployment
            try:
                success_indicator = await self.page.query_selector("text=/deployed|active/i")
                if success_indicator:
                    print("Deployment verified!")
            except:
                print("Deployment status unclear, but continuing...")
                
        except Exception as e:
            print(f"Error deploying: {e}")
            raise
    
    async def configure_n8n(self):
        """Navigate to N8N and configure with Lindy details"""
        print(f"Navigating to N8N: {config.N8N_URL}")
        
        await self.page.goto(config.N8N_URL)
        await self.page.wait_for_load_state('networkidle')
        
        try:
            # Find Lindy URL input
            lindy_url_input = await self.page.wait_for_selector(
                "input[placeholder*='Lindy URL'], input[name*='lindy']",
                timeout=30000
            )
            await lindy_url_input.fill(self.lindy_url)
            print("Entered Lindy URL in N8N")
            
            # Find Authorization Token input
            auth_token_input = await self.page.wait_for_selector(
                "input[placeholder*='Authorization'], input[placeholder*='Token']"
            )
            await auth_token_input.fill(self.auth_token)
            print("Entered authorization token in N8N")
            
            # Click Save Configuration
            save_config_button = await self.page.wait_for_selector(
                "button:has-text('Save Configuration'), button:has-text('Save')"
            )
            await save_config_button.click()
            print("Clicked 'Save Configuration' button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Scroll down to find Start Processing button
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(2000)
            
            # Click Start Processing
            start_button = await self.page.wait_for_selector(
                "button:has-text('Start Processing'), button:has-text('Start')"
            )
            await start_button.click()
            print("Clicked 'Start Processing' button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
        except Exception as e:
            print(f"Error configuring N8N: {e}")
            raise
    
    async def wait_period(self):
        """Wait for 10 minutes"""
        print(f"Waiting for {config.WAIT_TIME} seconds (10 minutes)...")
        
        for i in range(config.WAIT_TIME // 60):
            print(f"Waited {i+1} minute(s)...")
            await asyncio.sleep(60)
        
        print("Wait period completed!")
    
    async def delete_lindy_account(self):
        """Delete the Lindy account"""
        print("Deleting Lindy account...")
        
        try:
            # Navigate to settings/account page
            await self.page.goto("https://chat.lindy.ai/settings")
            await self.page.wait_for_load_state('networkidle')
            
            # Look for account or danger zone section
            try:
                delete_button = await self.page.wait_for_selector(
                    "button:has-text('Delete'), button:has-text('delete')",
                    timeout=30000
                )
                await delete_button.click()
                print("Clicked delete account button")
                
                await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                
                # Confirm deletion
                confirm_button = await self.page.wait_for_selector(
                    "button:has-text('Confirm'), button:has-text('Delete'), button:has-text('Yes')"
                )
                await confirm_button.click()
                print("Confirmed account deletion")
                
                await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
                print("Account deleted successfully!")
                
            except PlaywrightTimeout:
                print("Could not find delete button, trying alternative method...")
                # Try to find settings menu
                settings_links = await self.page.query_selector_all("a:has-text('Settings'), a:has-text('Account')")
                if settings_links:
                    await settings_links[0].click()
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    # Try again
                    delete_button = await self.page.wait_for_selector("button:has-text('Delete')")
                    await delete_button.click()
                    
        except Exception as e:
            print(f"Error deleting account: {e}")
            print("You may need to delete the account manually")
    
    async def run(self):
        """Execute the complete automation workflow"""
        try:
            print("\n" + "="*50)
            print("Starting Lindy Automation with Playwright")
            print("="*50 + "\n")
            
            await self.setup()
            await self.google_signin()
            await self.fill_signup_form()
            await self.handle_free_trial()
            await self.navigate_to_template()
            await self.configure_webhook()
            await self.deploy_lindy()
            await self.configure_n8n()
            await self.wait_period()
            await self.delete_lindy_account()
            
            print("\n" + "="*50)
            print("Automation completed successfully!")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"\n!!! Automation failed: {e}")
            raise
        finally:
            print("Closing browser...")
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            if self.browser:
                await self.browser.close()


async def main():
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

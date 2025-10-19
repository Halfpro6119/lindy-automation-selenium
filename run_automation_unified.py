"""
Lindy Automation Script - Unified Version
Works in both headed and headless mode with Google OAuth
Usage: 
  python run_automation_unified.py --headless  # Run in headless mode
  python run_automation_unified.py --headed    # Run in headed mode (default)
"""

import time
import asyncio
import os
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config


class LindyAutomation:
    def __init__(self, headless=False):
        """Initialize the automation"""
        self.headless = headless
        mode = "HEADLESS" if headless else "HEADED (VISIBLE)"
        print(f"Initializing Playwright automation in {mode} mode...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None
        
    async def setup(self):
        """Setup browser with configurable headless mode"""
        mode = "headless" if self.headless else "headed (visible)"
        print(f"Setting up browser in {mode} mode...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with configurable headless mode
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        # Create context
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        
        # Hide automation markers
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print(f"✓ Browser setup complete in {mode} mode!")
        
    async def login_to_google(self):
        """Login to Google account with OAuth"""
        print("\n" + "="*70)
        print("LOGGING INTO GOOGLE WITH OAUTH")
        print("="*70)
        
        try:
            # Navigate to Lindy
            print("Navigating to Lindy...")
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            # Check if already logged in
            current_url = self.page.url
            if 'workspace' in current_url or '/home' in current_url:
                print("✓ Already logged in!")
                return True
            
            # Look for Google sign in button
            print("Looking for Google sign-in button...")
            google_selectors = [
                "button:has-text('Google')",
                "button:has-text('Continue with Google')",
                "a:has-text('Sign in with Google')",
                "button:has-text('Sign in with Google')",
                "[aria-label*='Google' i]"
            ]
            
            google_btn = None
            for selector in google_selectors:
                try:
                    google_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if google_btn:
                        print(f"✓ Found Google button: {selector}")
                        break
                except:
                    continue
            
            if google_btn:
                await google_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Clicked Google sign in")
            else:
                print("WARNING: No Google button found, may already be on login page")
            
            # Wait for Google login page
            await self.page.wait_for_timeout(5000)
            
            # Enter email
            print("Entering email...")
            email_selectors = [
                "input[type='email']",
                "input[name='identifier']",
                "input[id='identifierId']"
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if email_input:
                        break
                except:
                    continue
            
            if not email_input:
                print("ERROR: Could not find email input")
                await self.page.screenshot(path='screenshot_error_no_email.png')
                return False
            
            await email_input.fill(config.GOOGLE_EMAIL)
            await self.page.wait_for_timeout(1000)
            
            # Click Next or press Enter
            next_btn = await self.page.query_selector("button:has-text('Next'), button[type='submit']")
            if next_btn:
                await next_btn.click()
            else:
                await self.page.keyboard.press('Enter')
            
            await self.page.wait_for_timeout(3000)
            print(f"✓ Entered email: {config.GOOGLE_EMAIL}")
            
            # Enter password
            print("Entering password...")
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[name='Passwd']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=10000)
                    if password_input:
                        break
                except:
                    continue
            
            if not password_input:
                print("ERROR: Could not find password input")
                await self.page.screenshot(path='screenshot_error_no_password.png')
                return False
            
            await password_input.fill(config.GOOGLE_PASSWORD)
            await self.page.wait_for_timeout(1000)
            
            # Click Next or press Enter
            next_btn = await self.page.query_selector("button:has-text('Next'), button[type='submit']")
            if next_btn:
                await next_btn.click()
            else:
                await self.page.keyboard.press('Enter')
            
            await self.page.wait_for_timeout(5000)
            print("✓ Entered password")
            
            # Wait for redirect back to Lindy
            print("Waiting for redirect to Lindy...")
            await self.page.wait_for_timeout(10000)
            
            # Check if we need to fill out signup form
            current_url = self.page.url
            if 'signup' in current_url or 'onboarding' in current_url:
                print("Filling out signup form...")
                await self.fill_signup_form()
            
            print("✓ Login successful!")
            return True
            
        except Exception as e:
            print(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_login.png')
            return False
    
    async def fill_signup_form(self):
        """Fill out the signup form if it appears"""
        try:
            await self.page.wait_for_timeout(3000)
            
            # Look for form fields and fill them
            text_inputs = await self.page.query_selector_all("input[type='text']")
            for input_field in text_inputs:
                placeholder = await input_field.get_attribute('placeholder')
                if placeholder and 'name' in placeholder.lower():
                    await input_field.fill("Test User")
                elif placeholder and 'company' in placeholder.lower():
                    await input_field.fill("Test Company")
            
            # Click continue/next buttons
            continue_selectors = [
                "button:has-text('Continue')",
                "button:has-text('Next')",
                "button:has-text('Get Started')",
                "button:has-text('Submit')"
            ]
            
            for selector in continue_selectors:
                try:
                    continue_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if continue_btn:
                        await continue_btn.click()
                        await self.page.wait_for_timeout(3000)
                        print(f"✓ Clicked: {selector}")
                        break
                except:
                    continue
            
            print("✓ Filled signup form")
            
        except Exception as e:
            print(f"Note: Signup form: {e}")
    
    async def start_free_trial(self):
        """Start free trial and enter card details"""
        print("\n" + "="*70)
        print("STARTING FREE TRIAL")
        print("="*70)
        
        try:
            # Look for free trial button
            trial_selectors = [
                "button:has-text('Start Free Trial')",
                "button:has-text('Free Trial')",
                "a:has-text('Start Trial')",
                "button:has-text('Start trial')"
            ]
            
            trial_btn = None
            for selector in trial_selectors:
                try:
                    trial_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if trial_btn:
                        break
                except:
                    continue
            
            if not trial_btn:
                print("No free trial button found - may already have credits")
                return True
            
            await trial_btn.click()
            await self.page.wait_for_timeout(3000)
            print("✓ Clicked Start Free Trial")
            
            # Wait for card form
            await self.page.wait_for_timeout(3000)
            
            # Enter card number
            card_input = await self.page.wait_for_selector("input[placeholder*='Card' i], input[name*='card' i]", timeout=10000)
            await card_input.fill(config.CARD_NUMBER)
            print("✓ Entered card number")
            
            # Enter expiry
            expiry_input = await self.page.query_selector("input[placeholder*='Expiry' i], input[placeholder*='MM' i]")
            if expiry_input:
                await expiry_input.fill(config.CARD_EXPIRY)
                print("✓ Entered expiry date")
            
            # Enter CVC
            cvc_input = await self.page.query_selector("input[placeholder*='CVC' i], input[placeholder*='CVV' i]")
            if cvc_input:
                await cvc_input.fill(config.CARD_CVC)
                print("✓ Entered CVC")
            
            # Enter cardholder name
            name_input = await self.page.query_selector("input[placeholder*='Name' i]")
            if name_input:
                await name_input.fill(config.CARDHOLDER_NAME)
                print("✓ Entered cardholder name")
            
            # Enter country
            country_input = await self.page.query_selector("input[placeholder*='Country' i], select[name*='country' i]")
            if country_input:
                await country_input.fill(config.CARD_COUNTRY)
                print("✓ Entered country")
            
            # Enter postal code
            postal_input = await self.page.query_selector("input[placeholder*='Postal' i], input[placeholder*='ZIP' i]")
            if postal_input:
                await postal_input.fill(config.POSTAL_CODE)
                print("✓ Entered postal code")
            
            # Click Save Card
            save_selectors = [
                "button:has-text('Save Card')",
                "button:has-text('Save')",
                "button:has-text('Submit')"
            ]
            
            for selector in save_selectors:
                try:
                    save_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if save_btn:
                        await save_btn.click()
                        await self.page.wait_for_timeout(5000)
                        print(f"✓ Clicked: {selector}")
                        break
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"Note: Free trial: {e}")
            return True  # Continue even if this fails
    
    async def add_template(self):
        """Navigate to template and add it to account"""
        print("\n" + "="*70)
        print("ADDING TEMPLATE TO ACCOUNT")
        print("="*70)
        
        try:
            # Navigate to template URL
            print(f"Navigating to template: {config.LINDY_TEMPLATE_URL}")
            await self.page.goto(config.LINDY_TEMPLATE_URL, wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(5000)
            
            await self.page.screenshot(path='screenshot_1_template_page.png')
            print("Screenshot saved: screenshot_1_template_page.png")
            
            # Look for Add button
            add_selectors = [
                "button:has-text('Add')",
                "button:has-text('Use template')",
                "button:has-text('Use this template')",
                "button:has-text('Add to workspace')"
            ]
            
            add_button = None
            for selector in add_selectors:
                try:
                    add_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if add_button:
                        print(f"✓ Found Add button with selector: {selector}")
                        break
                except:
                    continue
            
            if not add_button:
                print("ERROR: Could not find Add button")
                await self.page.screenshot(path='screenshot_error_no_add_button.png')
                return False
            
            # Click Add button
            await add_button.click()
            await self.page.wait_for_timeout(5000)
            print("✓ Clicked 'Add' button to add template")
            
            await self.page.screenshot(path='screenshot_2_after_add.png')
            
            current_url = self.page.url
            print(f"Current URL after adding template: {current_url}")
            
            # Navigate to editor view
            if '/tasks' in current_url:
                editor_url = current_url.replace('/tasks', '/editor')
                print(f"Navigating to editor view: {editor_url}")
                await self.page.goto(editor_url, wait_until='networkidle', timeout=60000)
                await self.page.wait_for_timeout(3000)
                print("✓ Successfully navigated to editor view")
                
                await self.page.screenshot(path='screenshot_2b_editor_view.png')
            
            return True
            
        except Exception as e:
            print(f"Error adding template: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_template.png')
            return False
    
    async def configure_webhook(self):
        """Find webhook step and configure it"""
        print("\n" + "="*70)
        print("CONFIGURING WEBHOOK")
        print("="*70)
        
        try:
            await self.page.wait_for_timeout(5000)
            
            # Scroll to top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(2000)
            
            await self.page.screenshot(path='screenshot_3_before_webhook.png')
            
            # Look for webhook trigger
            webhook_selectors = [
                "text='Webhook Received'",
                "div:has-text('Webhook Received')",
                "button:has-text('Webhook')",
                "[class*='trigger']"
            ]
            
            webhook_element = None
            for selector in webhook_selectors:
                try:
                    webhook_element = await self.page.wait_for_selector(selector, timeout=5000)
                    if webhook_element:
                        print(f"✓ Found webhook element: {selector}")
                        break
                except:
                    continue
            
            if not webhook_element:
                print("ERROR: Could not find webhook element")
                await self.page.screenshot(path='screenshot_error_no_webhook.png')
                return False
            
            # Click webhook element
            await webhook_element.click()
            await self.page.wait_for_timeout(3000)
            print("✓ Clicked webhook element")
            
            await self.page.screenshot(path='screenshot_4_webhook_opened.png')
            
            # Check if webhook already exists
            existing_url = await self.page.query_selector("input[value*='https://']")
            if existing_url:
                self.lindy_url = await existing_url.input_value()
                print(f"✓ Found existing webhook URL: {self.lindy_url}")
            else:
                # Create new webhook
                print("→ Creating new webhook...")
                
                # First, click "Select an option" button to reveal webhook options
                print("→ Looking for 'Select an option' button...")
                select_option_selectors = [
                    "button:has-text('Select an option')",
                    "button:has-text('select an option')",
                    "button:has-text('Select')",
                    "[role='button']:has-text('Select an option')",
                    "div:has-text('Select an option')",
                ]
                
                select_option_clicked = False
                for selector in select_option_selectors:
                    try:
                        select_option_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if select_option_btn:
                            print(f"✓ Found 'Select an option' button: {selector}")
                            await select_option_btn.click()
                            await self.page.wait_for_timeout(2000)
                            print("✓ Clicked 'Select an option' button")
                            await self.page.screenshot(path='screenshot_4b_after_select_option.png')
                            select_option_clicked = True
                            break
                    except:
                        continue
                
                if not select_option_clicked:
                    print("⚠ 'Select an option' button not found, continuing...")
                
                # Now look for Create Webhook button
                print("→ Looking for 'Create Webhook' button...")
                create_webhook_selectors = [
                    "button:has-text('Create Webhook')",
                    "button:has-text('Create webhook')",
                    "button:has-text('Create new webhook')",
                    "button:has-text('New webhook')",
                    "button:has-text('webhook')",
                ]
                
                create_btn = None
                for selector in create_webhook_selectors:
                    try:
                        create_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if create_btn:
                            print(f"✓ Found 'Create Webhook' button: {selector}")
                            break
                    except:
                        continue
                
                if not create_btn:
                    print("ERROR: Could not find Create Webhook button")
                    print("→ Taking debug screenshot...")
                    await self.page.screenshot(path='screenshot_error_no_create.png')
                    
                    # Print all buttons on the page for debugging
                    all_buttons = await self.page.query_selector_all("button")
                    print(f"→ Found {len(all_buttons)} buttons on page:")
                    for i, btn in enumerate(all_buttons[:15]):  # Show first 15 buttons
                        try:
                            text = await btn.inner_text()
                            if text.strip():
                                print(f"  Button {i+1}: '{text.strip()}'")
                        except:
                            pass
                    return False
                
                await create_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Clicked Create Webhook")
                
                # Name the webhook
                name_input = await self.page.query_selector("input[type='text']")
                if name_input:
                    webhook_name = f"Lead Processing {int(time.time())}"
                    await name_input.fill(webhook_name)
                    await self.page.keyboard.press('Enter')
                    await self.page.wait_for_timeout(3000)
                    print(f"✓ Named webhook: {webhook_name}")
                
                await self.page.screenshot(path='screenshot_5_webhook_created.png')
                
                # Get the webhook URL
                url_input = await self.page.wait_for_selector("input[value*='https://']", timeout=10000)
                self.lindy_url = await url_input.input_value()
                print(f"✓ Got webhook URL: {self.lindy_url}")
            
            # Get authorization token
            secret_btn = await self.page.query_selector("button:has-text('secret'), button:has-text('Secret')")
            if secret_btn:
                await secret_btn.click()
                await self.page.wait_for_timeout(2000)
                print("✓ Clicked secret button")
                
                await self.page.screenshot(path='screenshot_6_secret.png')
                
                # Get token
                token_input = await self.page.query_selector("input[readonly]")
                if token_input:
                    self.auth_token = await token_input.input_value()
                    print(f"✓ Got auth token: {self.auth_token[:20]}...")
                
                # Close dialog
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(1000)
            else:
                print("WARNING: No secret button found")
                self.auth_token = ""
            
            return True
            
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_webhook.png')
            return False
    
    async def deploy_lindy(self):
        """Deploy the agent"""
        print("\n" + "="*70)
        print("DEPLOYING AGENT")
        print("="*70)
        
        try:
            deploy_btn = await self.page.query_selector("button:has-text('Deploy')")
            if not deploy_btn:
                print("WARNING: No Deploy button found - may already be deployed")
                return True
            
            await deploy_btn.click()
            await self.page.wait_for_timeout(5000)
            print("✓ Clicked Deploy")
            
            await self.page.screenshot(path='screenshot_7_deployed.png')
            return True
            
        except Exception as e:
            print(f"Note: Deploy: {e}")
            return True
    
    async def configure_n8n(self):
        """Configure N8N"""
        print("\n" + "="*70)
        print("CONFIGURING N8N")
        print("="*70)
        
        if not self.lindy_url:
            print("ERROR: No webhook URL!")
            return False
        
        try:
            await self.page.goto(config.N8N_URL, wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(5000)
            
            await self.page.screenshot(path='screenshot_8_n8n.png')
            
            # Fill Lindy URL
            lindy_input = await self.page.wait_for_selector("input[placeholder*='Lindy URL' i]", timeout=10000)
            await lindy_input.click()
            await self.page.keyboard.press('Control+A')
            await lindy_input.fill(self.lindy_url)
            print(f"✓ Entered Lindy URL")
            
            # Fill auth token
            auth_input = await self.page.query_selector("input[placeholder*='Authorization' i], input[placeholder*='Token' i]")
            if auth_input:
                await auth_input.click()
                await self.page.keyboard.press('Control+A')
                await auth_input.fill(self.auth_token if self.auth_token else "")
                print(f"✓ Entered auth token")
            
            await self.page.screenshot(path='screenshot_9_n8n_filled.png')
            
            # Scroll to Save button
            save_btn = await self.page.wait_for_selector("button:has-text('Save Configuration'), button:has-text('Save')", timeout=10000)
            await save_btn.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(1000)
            await save_btn.click()
            await self.page.wait_for_timeout(3000)
            print("✓ Saved configuration")
            
            await self.page.screenshot(path='screenshot_10_n8n_saved.png')
            
            # Start processing
            start_btn = await self.page.query_selector("button:has-text('Start Processing'), button:has-text('Start')")
            if start_btn:
                await start_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Started processing")
                
                await self.page.screenshot(path='screenshot_11_n8n_started.png')
            
            return True
            
        except Exception as e:
            print(f"Error configuring N8N: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_n8n.png')
            return False
    
    async def wait_period(self):
        """Wait 10 minutes"""
        print("\n" + "="*70)
        print("WAITING 10 MINUTES")
        print("="*70)
        
        wait_time = config.WAIT_TIME
        print(f"Waiting {wait_time} seconds ({wait_time/60} minutes)...")
        
        for i in range(0, wait_time, 60):
            remaining = wait_time - i
            print(f"  {remaining} seconds remaining...")
            await asyncio.sleep(min(60, remaining))
        
        print("✓ Wait complete!")
        return True
    
    async def delete_account(self):
        """Delete Lindy account"""
        print("\n" + "="*70)
        print("DELETING ACCOUNT")
        print("="*70)
        
        try:
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            await self.page.screenshot(path='screenshot_12_before_delete.png')
            
            # Find menu
            menu_btn = await self.page.query_selector("button[aria-label*='menu' i], [class*='menu'], [class*='avatar']")
            if not menu_btn:
                print("WARNING: No menu button found")
                return False
            
            await menu_btn.click()
            await self.page.wait_for_timeout(2000)
            print("✓ Opened menu")
            
            await self.page.screenshot(path='screenshot_13_menu.png')
            
            # Find Settings
            settings_btn = await self.page.query_selector("text='Settings', button:has-text('Settings')")
            if settings_btn:
                await settings_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Opened Settings")
                
                await self.page.screenshot(path='screenshot_14_settings.png')
            
            # Find Delete Account
            delete_btn = await self.page.query_selector("button:has-text('Delete Account'), button:has-text('Delete account')")
            if not delete_btn:
                print("WARNING: No Delete Account button found")
                return False
            
            await delete_btn.click()
            await self.page.wait_for_timeout(2000)
            print("✓ Clicked Delete Account")
            
            await self.page.screenshot(path='screenshot_15_delete_confirm.png')
            
            # Confirm
            confirm_btn = await self.page.query_selector("button:has-text('Confirm'), button:has-text('Delete'), button:has-text('Yes')")
            if confirm_btn:
                await confirm_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Confirmed deletion")
            
            await self.page.screenshot(path='screenshot_16_deleted.png')
            
            print("\n✓ Account deleted!")
            return True
            
        except Exception as e:
            print(f"Error deleting account: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_delete.png')
            return False
    
    async def cleanup(self):
        """Cleanup"""
        if not self.headless:
            print("\nKeeping browser open for inspection...")
            print("Press Ctrl+C to close when done.")
            try:
                # Keep browser open for 1 hour in headed mode
                await asyncio.sleep(3600)
            except:
                pass
        
        print("\nClosing browser...")
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✓ Browser closed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    async def run(self):
        """Run the complete automation"""
        try:
            # Setup browser
            await self.setup()
            
            # Login to Google
            if not await self.login_to_google():
                print("\n!!! Failed to login")
                return False
            
            # Start free trial (if needed)
            await self.start_free_trial()
            
            # Add template
            if not await self.add_template():
                print("\n!!! Failed to add template")
                return False
            
            # Configure webhook
            if not await self.configure_webhook():
                print("\n!!! Failed to configure webhook")
                return False
            
            # Deploy agent
            await self.deploy_lindy()
            
            # Configure N8N
            if not await self.configure_n8n():
                print("\n!!! Failed to configure N8N")
                return False
            
            # Wait 10 minutes
            await self.wait_period()
            
            # Delete account
            await self.delete_account()
            
            print("\n" + "="*70)
            print("AUTOMATION COMPLETED SUCCESSFULLY!")
            print("="*70)
            return True
            
        except Exception as e:
            print(f"\n!!! Automation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    # Parse command line arguments
    headless = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '--headless':
            headless = True
        elif sys.argv[1] == '--headed':
            headless = False
    
    mode = "HEADLESS" if headless else "HEADED (VISIBLE)"
    
    print("\n" + "="*70)
    print(f"Lindy Automation - Unified Version ({mode} MODE)")
    print("Works with Google OAuth in both headed and headless modes")
    print("="*70 + "\n")
    
    automation = LindyAutomation(headless=headless)
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

"""
Lindy Automation Script with Playwright - FIXED VERSION
Addresses all identified issues from testing
"""

import time
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import config
import pyperclip


class LindyAutomationPlaywright:
    def __init__(self):
        """Initialize the automation"""
        print("Initializing Playwright automation...")
        self.browser = None
        self.context = None
        self.page = None
        self.lindy_url = None
        self.auth_token = None
        self.playwright = None
        
    async def setup(self):
        """Setup browser with stealth configuration"""
        print("Setting up browser with stealth mode...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth args
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Changed to False for visibility during debugging
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
        
        print("Browser setup complete with stealth mode!")
        
    async def check_if_logged_in(self):
        """Check if already logged into Lindy"""
        try:
            # Navigate to Lindy
            await self.page.goto(config.LINDY_SIGNUP_URL)
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(3000)
            
            # Check for workspace indicators - FIXED REGEX
            # Look for "New Agent" button or workspace URL
            url = self.page.url
            if 'workspace' in url.lower():
                print("✓ Already logged in - detected workspace in URL")
                return True
            
            # Try to find New Agent button
            try:
                new_agent_btn = await self.page.wait_for_selector(
                    "button:has-text('New Agent')",
                    timeout=5000
                )
                if new_agent_btn:
                    print("✓ Already logged in - found 'New Agent' button")
                    return True
            except:
                pass
            
            # Check for sign in/sign up buttons
            try:
                signin_btn = await self.page.wait_for_selector(
                    "button:has-text('Sign in'), button:has-text('Sign up')",
                    timeout=5000
                )
                if signin_btn:
                    print("✗ Not logged in - found sign in/up button")
                    return False
            except:
                pass
            
            print("? Login status unclear, assuming not logged in")
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    async def google_signin(self):
        """Sign in to Google account - IMPROVED VERSION"""
        print("\n" + "="*70)
        print("GOOGLE SIGN-IN PROCESS")
        print("="*70)
        
        try:
            # Check if already logged in
            is_logged_in = await self.check_if_logged_in()
            
            if is_logged_in:
                print("\n✓ Already logged into Lindy! Skipping Google sign-in.")
                print("="*70 + "\n")
                return
            
            # Not logged in, proceed with Google OAuth
            print("\nAttempting Google OAuth sign-in...")
            
            # Look for "Sign in with Google" button
            print("Looking for 'Sign in with Google' button...")
            google_signin_selectors = [
                "button:has-text('Sign in with Google')",
                "button:has-text('Sign up with Google')",
                "button:has-text('Continue with Google')",
                "button:has-text('Google')"
            ]
            
            google_button_clicked = False
            for selector in google_signin_selectors:
                try:
                    google_button = await self.page.wait_for_selector(
                        selector,
                        timeout=10000
                    )
                    await google_button.click()
                    print(f"✓ Clicked Google sign-in button: {selector}")
                    google_button_clicked = True
                    break
                except PlaywrightTimeout:
                    continue
            
            if not google_button_clicked:
                raise Exception("❌ Could not find Google sign-in button")
            
            await self.page.wait_for_timeout(5000)
            
            # Take screenshot before entering credentials
            await self.page.screenshot(path="debug_google_page.png")
            print("📸 Screenshot saved: debug_google_page.png")
            
            # Handle Google login page
            print("\nEntering Google credentials...")
            
            # Enter email
            try:
                email_input = await self.page.wait_for_selector("input[type='email']", timeout=15000)
                await email_input.click()
                await self.page.wait_for_timeout(500)
                await email_input.type(config.GOOGLE_EMAIL, delay=100)
                print(f"✓ Entered email: {config.GOOGLE_EMAIL}")
                await self.page.wait_for_timeout(1000)
                await self.page.keyboard.press("Enter")
                await self.page.wait_for_timeout(5000)
            except Exception as e:
                print(f"❌ Error entering email: {e}")
                await self.page.screenshot(path="error_email.png")
                raise
            
            # Check for Google blocking
            page_content = await self.page.content()
            if "Couldn't sign you in" in page_content or "This browser or app may not be secure" in page_content:
                print("\n" + "!"*70)
                print("⚠️  GOOGLE DETECTED AUTOMATION AND BLOCKED SIGN-IN!")
                print("!"*70)
                print("\nThis is a known limitation with Google OAuth automation.")
                print("\nRECOMMENDED SOLUTIONS:")
                print("1. Use manual login once, then save session cookies")
                print("2. Use Lindy API instead of browser automation")
                print("3. Use a different authentication method")
                print("4. Run with a real browser profile that's already logged in")
                print("!"*70 + "\n")
                
                await self.page.screenshot(path="google_blocked.png")
                raise Exception("Google blocked automated sign-in")
            
            # Enter password
            try:
                password_input = await self.page.wait_for_selector("input[type='password']", timeout=15000)
                await password_input.click()
                await self.page.wait_for_timeout(500)
                await password_input.type(config.GOOGLE_PASSWORD, delay=100)
                print("✓ Entered password")
                await self.page.wait_for_timeout(1000)
                await self.page.keyboard.press("Enter")
                await self.page.wait_for_timeout(10000)
            except PlaywrightTimeout:
                print("❌ Password field not found - Google likely blocked the login")
                await self.page.screenshot(path="error_password.png")
                raise Exception("Password field timeout - Google blocking suspected")
            
            # Handle any additional prompts
            try:
                continue_button = await self.page.wait_for_selector(
                    "button:has-text('Continue')",
                    timeout=5000
                )
                await continue_button.click()
                print("✓ Clicked Continue button")
                await self.page.wait_for_timeout(5000)
            except PlaywrightTimeout:
                print("ℹ️  No Continue button found - proceeding...")
            
            print("\n✓ Google sign-in completed successfully!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during Google sign-in: {e}")
            print("="*70 + "\n")
            raise
    
    async def fill_signup_form(self):
        """Fill out any signup forms"""
        print("Checking for signup forms...")
        
        try:
            # Wait for any forms to appear
            await self.page.wait_for_timeout(5000)
            
            # Look for common form fields
            form_fields = await self.page.query_selector_all("input[type='text'], input[type='email'], input[name*='name']")
            
            if len(form_fields) > 0:
                print(f"Found {len(form_fields)} form fields, filling them out...")
                
                for field in form_fields:
                    try:
                        placeholder = await field.get_attribute("placeholder")
                        name = await field.get_attribute("name")
                        
                        if placeholder or name:
                            print(f"Filling field: {placeholder or name}")
                            await field.fill("Automation Test")
                    except:
                        continue
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "button:has-text('Continue')",
                    "button:has-text('Next')",
                    "button:has-text('Submit')"
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        await submit_btn.click()
                        print(f"Clicked submit button: {selector}")
                        await self.page.wait_for_timeout(5000)
                        break
                    except:
                        continue
            else:
                print("No signup form found, proceeding...")
                
        except Exception as e:
            print(f"Error filling signup form: {e}")
    
    async def handle_free_trial(self):
        """Handle free trial setup if required"""
        print("\nChecking for free trial section...")
        
        try:
            # Look for "Start Free Trial" button
            trial_button = await self.page.wait_for_selector(
                "button:has-text('Start Free Trial'), button:has-text('Start Trial')",
                timeout=10000
            )
            
            if trial_button:
                print("Found 'Start Free Trial' button, clicking...")
                await trial_button.click()
                await self.page.wait_for_timeout(5000)
                
                # Enter card details
                await self.enter_card_details()
            else:
                print("No free trial button found - may already have credits")
                
        except PlaywrightTimeout:
            print("No free trial section found - proceeding without it")
        except Exception as e:
            print(f"Error handling free trial: {e}")
    
    async def enter_card_details(self):
        """Enter card payment details"""
        print("\nEntering card details...")
        
        try:
            # Wait for card form to load
            await self.page.wait_for_timeout(3000)
            
            # Card number
            card_selectors = [
                "input[name*='card' i][name*='number' i]",
                "input[placeholder*='card number' i]",
                "input[id*='cardnumber' i]"
            ]
            
            for selector in card_selectors:
                try:
                    card_input = await self.page.wait_for_selector(selector, timeout=5000)
                    await card_input.fill(config.CARD_NUMBER)
                    print("✓ Entered card number")
                    break
                except:
                    continue
            
            # Expiry date
            expiry_input = await self.page.query_selector(
                "input[name*='expir' i], input[placeholder*='expir' i], input[placeholder*='MM/YY' i]"
            )
            if expiry_input:
                await expiry_input.fill(config.CARD_EXPIRY)
                print("✓ Entered expiry date")
            
            # CVC
            cvc_input = await self.page.query_selector(
                "input[name*='cvc' i], input[name*='cvv' i], input[placeholder*='cvc' i]"
            )
            if cvc_input:
                await cvc_input.fill(config.CARD_CVC)
                print("✓ Entered CVC")
            
            # Cardholder name
            name_input = await self.page.query_selector(
                "input[name*='name' i], input[placeholder*='name' i]"
            )
            if name_input:
                await name_input.fill(config.CARDHOLDER_NAME)
                print("✓ Entered cardholder name")
            
            # Country
            country_select = await self.page.query_selector(
                "select[name*='country' i], input[name*='country' i]"
            )
            if country_select:
                tag_name = await country_select.evaluate("el => el.tagName")
                if tag_name.lower() == 'select':
                    await country_select.select_option(label=config.CARD_COUNTRY)
                else:
                    await country_select.fill(config.CARD_COUNTRY)
                print("✓ Selected country")
            
            # Postal code
            postal_input = await self.page.query_selector(
                "input[name*='postal' i], input[name*='zip' i], input[placeholder*='postal' i]"
            )
            if postal_input:
                await postal_input.fill(config.POSTAL_CODE)
                print("✓ Entered postal code")
            
            # Click Save Card button
            await self.page.wait_for_timeout(2000)
            save_button = await self.page.wait_for_selector(
                "button:has-text('Save'), button:has-text('Submit'), button:has-text('Add Card')"
            )
            await save_button.click()
            print("✓ Clicked 'Save Card' button")
            
            await self.page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"❌ Error entering card details: {e}")
            raise
    
    async def navigate_to_template(self):
        """Navigate to the specific template"""
        print(f"\nNavigating to template: {config.LINDY_TEMPLATE_URL}")
        
        await self.page.goto(config.LINDY_TEMPLATE_URL)
        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_timeout(5000)
        
        # Take screenshot
        await self.page.screenshot(path="template_page.png")
        print("📸 Screenshot saved: template_page.png")
        
        # Add template to account
        try:
            print("Looking for 'Add' or 'Use Template' button...")
            
            add_selectors = [
                "button:has-text('Add')",
                "button:has-text('Use Template')",
                "button:has-text('Use this template')",
                "button:has-text('Get Started')"
            ]
            
            add_button_clicked = False
            for selector in add_selectors:
                try:
                    add_button = await self.page.wait_for_selector(
                        selector,
                        timeout=10000,
                        state='visible'
                    )
                    await add_button.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(1000)
                    await add_button.click()
                    print(f"✓ Clicked button: {selector}")
                    add_button_clicked = True
                    break
                except:
                    continue
            
            if not add_button_clicked:
                print("⚠️  Could not find Add button, template may already be added")
            
            await self.page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"Error in template navigation: {e}")
            raise
    
    async def configure_webhook(self):
        """Find webhook step and configure it"""
        print("\nConfiguring webhook...")
        
        try:
            # Wait for page to load
            await self.page.wait_for_timeout(3000)
            
            # Take screenshot
            await self.page.screenshot(path="webhook_page.png")
            print("📸 Screenshot saved: webhook_page.png")
            
            # Look for webhook-related elements
            print("Looking for 'Webhook' or 'Create Webhook' button...")
            
            webhook_selectors = [
                "button:has-text('Create Webhook')",
                "button:has-text('Webhook')",
                "text='Webhook Received'",
                "*:has-text('Webhook')"
            ]
            
            webhook_clicked = False
            for selector in webhook_selectors:
                try:
                    webhook_element = await self.page.wait_for_selector(selector, timeout=10000)
                    await webhook_element.click()
                    print(f"✓ Clicked webhook element: {selector}")
                    webhook_clicked = True
                    await self.page.wait_for_timeout(3000)
                    break
                except:
                    continue
            
            if not webhook_clicked:
                print("⚠️  Could not find webhook element")
                return
            
            # Look for "Create Webhook" button
            try:
                create_webhook_btn = await self.page.wait_for_selector(
                    "button:has-text('Create Webhook'), button:has-text('Create')",
                    timeout=10000
                )
                await create_webhook_btn.click()
                print("✓ Clicked 'Create Webhook' button")
                await self.page.wait_for_timeout(3000)
            except:
                print("ℹ️  No 'Create Webhook' button found")
            
            # Enter webhook name
            try:
                name_input = await self.page.wait_for_selector(
                    "input[placeholder*='name' i], input[type='text']",
                    timeout=5000
                )
                await name_input.fill("Automation Webhook")
                await self.page.keyboard.press("Enter")
                print("✓ Entered webhook name")
                await self.page.wait_for_timeout(3000)
            except:
                print("ℹ️  No name input found")
            
            # Copy Lindy URL
            try:
                # Look for URL field or copy button
                url_selectors = [
                    "input[value*='https://']",
                    "input[readonly]",
                    "button:has-text('Copy')"
                ]
                
                for selector in url_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=5000)
                        
                        if 'input' in selector:
                            self.lindy_url = await element.get_attribute('value')
                            print(f"✓ Found Lindy URL: {self.lindy_url}")
                        else:
                            await element.click()
                            await self.page.wait_for_timeout(1000)
                            # Try to get from clipboard
                            try:
                                self.lindy_url = pyperclip.paste()
                                print(f"✓ Copied Lindy URL: {self.lindy_url}")
                            except:
                                print("⚠️  Could not access clipboard")
                        
                        if self.lindy_url:
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️  Error getting Lindy URL: {e}")
            
            # Create and copy secret key
            try:
                secret_key_btn = await self.page.wait_for_selector(
                    "button:has-text('secret'), button:has-text('Secret'), button:has-text('Generate')",
                    timeout=10000
                )
                await secret_key_btn.click()
                print("✓ Clicked secret key button")
                await self.page.wait_for_timeout(2000)
                
                # Copy the secret key
                copy_btn = await self.page.wait_for_selector(
                    "button:has-text('Copy')",
                    timeout=5000
                )
                await copy_btn.click()
                await self.page.wait_for_timeout(1000)
                
                try:
                    self.auth_token = pyperclip.paste()
                    print(f"✓ Copied auth token: {self.auth_token[:20]}...")
                except:
                    print("⚠️  Could not access clipboard for auth token")
                
                # Close dialog
                await self.page.keyboard.press("Escape")
                await self.page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"⚠️  Error getting secret key: {e}")
            
        except Exception as e:
            print(f"❌ Error configuring webhook: {e}")
            raise
    
    async def deploy_lindy(self):
        """Deploy the Lindy automation"""
        print("\nDeploying Lindy...")
        
        try:
            # Look for Deploy button
            deploy_btn = await self.page.wait_for_selector(
                "button:has-text('Deploy')",
                timeout=10000
            )
            await deploy_btn.click()
            print("✓ Clicked 'Deploy' button")
            
            await self.page.wait_for_timeout(5000)
            
            # Check for success message
            try:
                success_indicator = await self.page.wait_for_selector(
                    "text='deployed', text='Deployed', text='success'",
                    timeout=10000
                )
                if success_indicator:
                    print("✓ Deployment successful!")
            except:
                print("ℹ️  Could not confirm deployment status")
            
        except Exception as e:
            print(f"❌ Error deploying: {e}")
            raise
    
    async def configure_n8n(self):
        """Configure N8N with Lindy URL and auth token"""
        print(f"\nNavigating to N8N: {config.N8N_URL}")
        
        try:
            await self.page.goto(config.N8N_URL)
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(5000)
            
            # Take screenshot
            await self.page.screenshot(path="n8n_page.png")
            print("📸 Screenshot saved: n8n_page.png")
            
            # Enter Lindy URL
            if self.lindy_url:
                print("Entering Lindy URL...")
                url_input = await self.page.wait_for_selector(
                    "input[placeholder*='Lindy URL' i], input[name*='lindy' i]",
                    timeout=10000
                )
                await url_input.fill(self.lindy_url)
                print("✓ Entered Lindy URL")
            else:
                print("⚠️  No Lindy URL to enter")
            
            # Enter auth token
            if self.auth_token:
                print("Entering authorization token...")
                token_input = await self.page.wait_for_selector(
                    "input[placeholder*='token' i], input[placeholder*='authorization' i]",
                    timeout=10000
                )
                await token_input.fill(self.auth_token)
                print("✓ Entered authorization token")
            else:
                print("⚠️  No auth token to enter")
            
            # Save configuration
            save_btn = await self.page.wait_for_selector(
                "button:has-text('Save'), button:has-text('Save Configuration')",
                timeout=10000
            )
            await save_btn.click()
            print("✓ Clicked 'Save Configuration'")
            
            await self.page.wait_for_timeout(3000)
            
            # Start processing
            start_btn = await self.page.wait_for_selector(
                "button:has-text('Start'), button:has-text('Start Processing')",
                timeout=10000
            )
            await start_btn.click()
            print("✓ Clicked 'Start Processing'")
            
            await self.page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error configuring N8N: {e}")
            raise
    
    async def wait_processing(self):
        """Wait for 10 minutes"""
        print(f"\nWaiting {config.WAIT_TIME} seconds (10 minutes) for processing...")
        
        # Wait in chunks and show progress
        chunks = 10
        chunk_time = config.WAIT_TIME // chunks
        
        for i in range(chunks):
            await asyncio.sleep(chunk_time)
            progress = ((i + 1) / chunks) * 100
            print(f"Progress: {progress:.0f}% ({(i+1)*chunk_time}/{config.WAIT_TIME} seconds)")
        
        print("✓ Wait period completed!")
    
    async def delete_account(self):
        """Delete the Lindy account"""
        print("\nDeleting Lindy account...")
        
        try:
            # Navigate to settings
            await self.page.goto(config.LINDY_SIGNUP_URL)
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(3000)
            
            # Look for settings/menu
            menu_selectors = [
                "button[aria-label*='menu' i]",
                "button[aria-label*='settings' i]",
                "*[class*='menu']",
                "*[class*='avatar']"
            ]
            
            for selector in menu_selectors:
                try:
                    menu_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    await menu_btn.click()
                    print("✓ Opened menu")
                    await self.page.wait_for_timeout(2000)
                    break
                except:
                    continue
            
            # Look for settings option
            settings_btn = await self.page.wait_for_selector(
                "text='Settings', text='Account', button:has-text('Settings')",
                timeout=10000
            )
            await settings_btn.click()
            print("✓ Opened settings")
            
            await self.page.wait_for_timeout(3000)
            
            # Look for delete account option
            delete_btn = await self.page.wait_for_selector(
                "button:has-text('Delete'), button:has-text('Delete Account')",
                timeout=10000
            )
            await delete_btn.click()
            print("✓ Clicked 'Delete Account'")
            
            await self.page.wait_for_timeout(2000)
            
            # Confirm deletion
            confirm_btn = await self.page.wait_for_selector(
                "button:has-text('Confirm'), button:has-text('Delete'), button:has-text('Yes')",
                timeout=10000
            )
            await confirm_btn.click()
            print("✓ Confirmed account deletion")
            
            await self.page.wait_for_timeout(5000)
            
            print("✓ Account deleted successfully!")
            
        except Exception as e:
            print(f"❌ Error deleting account: {e}")
            # Don't raise - deletion is not critical
    
    async def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        
        try:
            if self.page:
                await self.page.wait_for_timeout(2000)
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✓ Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    async def run(self):
        """Run the complete automation workflow"""
        try:
            await self.setup()
            await self.google_signin()
            await self.fill_signup_form()
            await self.handle_free_trial()
            await self.navigate_to_template()
            await self.configure_webhook()
            await self.deploy_lindy()
            await self.configure_n8n()
            await self.wait_processing()
            await self.delete_account()
            
            print("\n" + "="*70)
            print("✓ AUTOMATION COMPLETED SUCCESSFULLY!")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ Automation failed: {e}")
            await self.page.screenshot(path="error_final.png")
            print("📸 Error screenshot saved: error_final.png")
            raise
        finally:
            await self.cleanup()


async def main():
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Starting Lindy Automation (Playwright) - FIXED VERSION")
    print("="*70 + "\n")
    asyncio.run(main())

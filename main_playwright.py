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
                    "button:has-text('Google'), button:has-text('google'), button:has-text('Sign in')",
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
            
            # NEW: Handle "You're signing back in to Lindy" page
            try:
                print("Checking for 'Continue' button on sign-in page...")
                continue_button = await self.page.wait_for_selector(
                    "button:has-text('Continue'), button:has-text('continue')",
                    timeout=10000
                )
                await continue_button.click()
                print("Clicked 'Continue' button on sign-in page")
                await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            except PlaywrightTimeout:
                print("No 'Continue' button found - proceeding...")
            
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
                        is_visible = await field.is_visible()
                        is_enabled = await field.is_enabled()
                        
                        if not is_visible or not is_enabled:
                            continue
                        
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
            # Wait for card form to load
            await self.page.wait_for_timeout(2000)
            
            # Card number
            card_number_input = await self.page.wait_for_selector(
                "input[name*='card' i][name*='number' i], input[placeholder*='card number' i], input[placeholder*='Card number' i]",
                timeout=30000
            )
            await card_number_input.fill(config.CARD_NUMBER)
            print("Entered card number")
            
            # Expiry date
            expiry_input = await self.page.query_selector(
                "input[name*='expir' i], input[placeholder*='expir' i], input[placeholder*='MM' i]"
            )
            await expiry_input.fill(config.CARD_EXPIRY)
            print("Entered expiry date")
            
            # CVC
            cvc_input = await self.page.query_selector(
                "input[name*='cvc' i], input[name*='cvv' i], input[placeholder*='cvc' i]"
            )
            await cvc_input.fill(config.CARD_CVC)
            print("Entered CVC")
            
            # Cardholder name
            try:
                name_input = await self.page.query_selector(
                    "input[name*='name' i], input[placeholder*='name' i]"
                )
                if name_input:
                    await name_input.fill(config.CARDHOLDER_NAME)
                    print("Entered cardholder name")
            except:
                print("Name field not found or not required")
            
            # Country
            try:
                country_select = await self.page.query_selector(
                    "select[name*='country' i], input[name*='country' i]"
                )
                if country_select:
                    tag_name = await country_select.evaluate("el => el.tagName")
                    if tag_name.lower() == 'select':
                        await country_select.select_option(label=config.CARD_COUNTRY)
                    else:
                        await country_select.fill(config.CARD_COUNTRY)
                    print("Selected country")
            except:
                print("Country field not found or not required")
            
            # Postal code
            try:
                postal_input = await self.page.query_selector(
                    "input[name*='postal' i], input[name*='zip' i], input[placeholder*='postal' i]"
                )
                if postal_input:
                    await postal_input.fill(config.POSTAL_CODE)
                    print("Entered postal code")
            except:
                print("Postal code field not found or not required")
            
            # Click Save Card button
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            save_button = await self.page.wait_for_selector(
                "button:has-text('Save'), button:has-text('Submit'), button:has-text('Add Card')"
            )
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
            print("Looking for 'Add' button...")
            add_template_button = await self.page.wait_for_selector(
                "button:has-text('Add'), button:has-text('Use'), button:has-text('Install')",
                timeout=30000
            )
            await add_template_button.click()
            print("Clicked 'Add' button")
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            
            # NEW: Wait for page to load and click "Flow Editor" button
            print("Waiting for page to load and looking for 'Flow Editor' button...")
            await self.page.wait_for_timeout(5000)  # Wait 5 seconds for page to fully load
            
            # Try multiple selectors for Flow Editor button
            flow_editor_clicked = False
            selectors = [
                "button:has-text('Flow Editor')",
                "button:has-text('flow editor')",
                "button:has-text('Editor')",
                "a:has-text('Flow Editor')",
                "a:has-text('Editor')"
            ]
            
            for selector in selectors:
                try:
                    flow_editor_button = await self.page.wait_for_selector(selector, timeout=10000)
                    await flow_editor_button.click()
                    print(f"Clicked 'Flow Editor' button using selector: {selector}")
                    flow_editor_clicked = True
                    await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
                    break
                except:
                    continue
            
            if not flow_editor_clicked:
                print("Warning: Could not find Flow Editor button, attempting to continue...")
            
        except Exception as e:
            print(f"Error in template navigation: {e}")
            raise
    
    async def configure_webhook(self):
        """Find webhook step and configure it"""
        print("Looking for 'Webhook Received' near the top of the page...")
        
        try:
            # Wait for page to fully load
            await self.page.wait_for_timeout(3000)
            
            # NEW: Look specifically for "Webhook Received" text near the top
            webhook_received_clicked = False
            selectors = [
                "text='Webhook Received'",
                "text='webhook received'",
                "text='Webhook received'",
                "*:has-text('Webhook Received')",
                "*:has-text('Webhook') >> *:has-text('Received')"
            ]
            
            for selector in selectors:
                try:
                    webhook_received_element = await self.page.wait_for_selector(selector, timeout=10000)
                    await webhook_received_element.click()
                    print(f"Clicked 'Webhook Received' element using selector: {selector}")
                    webhook_received_clicked = True
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    break
                except:
                    continue
            
            if not webhook_received_clicked:
                print("Warning: Could not find 'Webhook Received', trying alternative approach...")
                # Try to find any webhook-related element
                webhook_elements = await self.page.query_selector_all("*:has-text('webhook'), *:has-text('Webhook')")
                if webhook_elements:
                    await webhook_elements[0].click()
                    print("Clicked first webhook element found")
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # NEW: Click "Select an option..." dropdown
            print("Looking for 'Select an option...' dropdown...")
            dropdown_clicked = False
            dropdown_selectors = [
                "text='Select an option'",
                "select",
                "input[placeholder*='Select an option']",
                "[role='combobox']",
                "*:has-text('Select an option')"
            ]
            
            for selector in dropdown_selectors:
                try:
                    select_dropdown = await self.page.wait_for_selector(selector, timeout=10000)
                    await select_dropdown.click()
                    print(f"Clicked dropdown using selector: {selector}")
                    dropdown_clicked = True
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    break
                except:
                    continue
            
            if not dropdown_clicked:
                print("Warning: Could not find dropdown, trying to type directly...")
            
            # NEW: Click "Create new..." option
            print("Looking for 'Create new...' option...")
            create_new_clicked = False
            create_selectors = [
                "text='Create new'",
                "text='create new'",
                "option:has-text('Create new')",
                "li:has-text('Create new')",
                "*:has-text('Create new')"
            ]
            
            for selector in create_selectors:
                try:
                    create_new_option = await self.page.wait_for_selector(selector, timeout=10000)
                    await create_new_option.click()
                    print(f"Clicked 'Create new...' using selector: {selector}")
                    create_new_clicked = True
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    break
                except:
                    continue
            
            if not create_new_clicked:
                print("Warning: Could not find 'Create new' option, attempting to type directly...")
            
            # NEW: Type "Webhook" and press Enter
            print("Typing 'Webhook' and pressing Enter...")
            await self.page.wait_for_timeout(1000)
            
            # Try to find visible input field or use keyboard
            try:
                # Look for visible input fields
                input_fields = await self.page.query_selector_all("input[type='text']:not([disabled])")
                input_used = False
                
                for input_field in input_fields:
                    is_visible = await input_field.is_visible()
                    is_enabled = await input_field.is_enabled()
                    
                    if is_visible and is_enabled:
                        await input_field.fill("Webhook")
                        await input_field.press("Enter")
                        print("Typed 'Webhook' in visible input field")
                        input_used = True
                        break
                
                if not input_used:
                    # Use keyboard directly
                    await self.page.keyboard.type("Webhook")
                    await self.page.keyboard.press("Enter")
                    print("Typed 'Webhook' using keyboard")
                    
            except Exception as e:
                print(f"Error typing webhook name: {e}")
            
            await self.page.wait_for_timeout(config.MEDIUM_WAIT * 1000)
            
            # NEW: Click the webhook that was just created
            print("Looking for the newly created webhook...")
            webhook_clicked = False
            webhook_selectors = [
                "text='Webhook'",
                "div:has-text('Webhook'):not(:has-text('Webhook Received'))",
                "li:has-text('Webhook'):not(:has-text('Received'))",
                "span:has-text('Webhook'):not(:has-text('Received'))"
            ]
            
            for selector in webhook_selectors:
                try:
                    webhook_item = await self.page.wait_for_selector(selector, timeout=10000)
                    await webhook_item.click()
                    print(f"Clicked newly created webhook using selector: {selector}")
                    webhook_clicked = True
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    break
                except:
                    continue
            
            if not webhook_clicked:
                print("Warning: Could not find newly created webhook, continuing...")
            
            # Continue from generate secret button onwards
            # Copy the Lindy URL
            print("Looking for Lindy URL...")
            await self.page.wait_for_timeout(2000)
            
            try:
                # Look for URL field
                url_elements = await self.page.query_selector_all("input[value*='https://']")
                
                for url_elem in url_elements:
                    value = await url_elem.get_attribute('value')
                    if value and 'lindy' in value.lower():
                        self.lindy_url = value
                        print(f"Found Lindy URL: {self.lindy_url}")
                        break
                
                if not self.lindy_url:
                    # Try to find copy button for URL
                    copy_buttons = await self.page.query_selector_all("button:has-text('Copy')")
                    if copy_buttons:
                        await copy_buttons[0].click()
                        await self.page.wait_for_timeout(1000)
                        self.lindy_url = await self.page.evaluate("navigator.clipboard.readText()")
                        print(f"Copied Lindy URL: {self.lindy_url}")
                        
            except Exception as e:
                print(f"Error getting Lindy URL: {e}")
            
            # Create secret key/authorization token
            print("Creating authorization token...")
            secret_button_clicked = False
            secret_selectors = [
                "button:has-text('Generate secret')",
                "button:has-text('generate secret')",
                "button:has-text('Secret')",
                "button:has-text('secret')",
                "button:has-text('Generate')",
                "button:has-text('Token')",
                "button:has-text('token')"
            ]
            
            for selector in secret_selectors:
                try:
                    secret_key_button = await self.page.wait_for_selector(selector, timeout=10000)
                    await secret_key_button.click()
                    print(f"Clicked secret key button using selector: {selector}")
                    secret_button_clicked = True
                    await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
                    break
                except:
                    continue
            
            if not secret_button_clicked:
                print("Warning: Could not find secret key button")
            
            # Copy the secret key
            await self.page.wait_for_timeout(2000)
            try:
                # Try to find the secret key value
                secret_elements = await self.page.query_selector_all("input[type='text'], input[type='password']")
                
                for element in secret_elements:
                    is_visible = await element.is_visible()
                    if not is_visible:
                        continue
                    
                    value = await element.get_attribute('value')
                    if value and len(value) > 15:  # Secret keys are usually longer
                        self.auth_token = value
                        # Copy to clipboard
                        await element.click()
                        await element.select_text()
                        await self.page.keyboard.press("Control+C")
                        print(f"Copied authorization token")
                        break
                
                if not self.auth_token:
                    # Try copy button
                    copy_buttons = await self.page.query_selector_all("button:has-text('Copy')")
                    for btn in copy_buttons:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            await btn.click()
                            await self.page.wait_for_timeout(1000)
                            self.auth_token = await self.page.evaluate("navigator.clipboard.readText()")
                            print(f"Copied authorization token via button")
                            break
                    
            except Exception as e:
                print(f"Error copying secret key: {e}")
            
            # Click outside to close dialog
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            try:
                # Press Escape key
                await self.page.keyboard.press("Escape")
                print("Pressed Escape to close dialog")
            except:
                # Fallback to clicking body
                await self.page.click("body")
                print("Clicked outside dialog to close")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            import traceback
            traceback.print_exc()
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
                success_indicator = await self.page.query_selector(
                    "*:has-text('deployed'), *:has-text('Deployed'), *:has-text('active'), *:has-text('Active')"
                )
                if success_indicator:
                    print("Deployment verified!")
            except:
                print("Deployment status unclear, but continuing...")
                
        except Exception as e:
            print(f"Error deploying: {e}")
            print("Continuing despite deployment error...")
    
    async def configure_n8n(self):
        """Navigate to N8N and configure with Lindy details"""
        print(f"Navigating to N8N: {config.N8N_URL}")
        
        if not self.lindy_url or not self.auth_token:
            print("ERROR: Missing Lindy URL or Auth Token!")
            print(f"Lindy URL: {self.lindy_url}")
            print(f"Auth Token: {self.auth_token}")
            raise Exception("Cannot configure N8N without Lindy URL and Auth Token")
        
        await self.page.goto(config.N8N_URL)
        await self.page.wait_for_load_state('networkidle')
        
        try:
            # Find Lindy URL input
            lindy_url_input = await self.page.wait_for_selector(
                "input[placeholder*='Lindy URL'], input[name*='lindy'], input[id*='lindy']",
                timeout=30000
            )
            await lindy_url_input.fill(self.lindy_url)
            print("Entered Lindy URL in N8N")
            
            # Find Authorization Token input
            auth_token_input = await self.page.query_selector(
                "input[placeholder*='Authorization'], input[placeholder*='Token'], input[name*='token'], input[name*='auth']"
            )
            await auth_token_input.fill(self.auth_token)
            print("Entered authorization token in N8N")
            
            # Click Save Configuration
            save_config_button = await self.page.query_selector(
                "button:has-text('Save Configuration'), button:has-text('Save')"
            )
            await save_config_button.click()
            print("Clicked 'Save Configuration' button")
            
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            
            # Scroll down to find Start Processing button
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(2000)
            
            # Click Start Processing
            start_button = await self.page.query_selector(
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
                    "button:has-text('Confirm'), button:has-text('Delete'), button:has-text('Yes')",
                    timeout=30000
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
                    delete_button = await self.page.query_selector("button:has-text('Delete')")
                    await delete_button.click()
                    
        except Exception as e:
            print(f"Error deleting account: {e}")
            print("You may need to delete the account manually")
    
    async def run(self):
        """Execute the complete automation workflow"""
        try:
            print("\n" + "="*50)
            print("Starting Lindy Automation (Playwright)")
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
            import traceback
            traceback.print_exc()
            raise
        finally:
            print("Closing browser...")
            await self.page.wait_for_timeout(config.SHORT_WAIT * 1000)
            await self.browser.close()


async def main():
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

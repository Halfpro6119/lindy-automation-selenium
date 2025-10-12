"""
Lindy Automation Script - Final Version
This version handles Google login issues by using alternative authentication methods
"""

import time
import asyncio
import os
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
        self.playwright = None
        self.session_file = "lindy_session.json"
        
    async def setup(self, use_saved_session=True):
        """Setup browser"""
        print("Setting up browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Check if we have a saved session
        storage_state = None
        if use_saved_session and os.path.exists(self.session_file):
            print(f"✓ Found saved session file: {self.session_file}")
            storage_state = self.session_file
        
        # Create context
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            storage_state=storage_state
        )
        
        self.page = await self.context.new_page()
        
        # Hide automation
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("Browser setup complete!")
        
    async def save_session(self):
        """Save the current session state"""
        try:
            await self.context.storage_state(path=self.session_file)
            print(f"✓ Session saved to {self.session_file}")
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
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
            print(f"Error checking login status: {e}")
            return False
    
    async def manual_login_prompt(self):
        """Prompt for manual login"""
        print("\n" + "="*70)
        print("MANUAL LOGIN REQUIRED")
        print("="*70)
        print("\nGoogle is blocking automated logins.")
        print("Please log in manually in the browser window that will open.")
        print("\nSteps:")
        print("1. A browser window will open")
        print("2. Log in to Lindy with your Google account")
        print("3. Wait until you see the Lindy workspace/home page")
        print("4. The automation will detect the login and continue")
        print("\nPress Enter to open the browser...")
        input()
        
        # Relaunch with visible browser
        await self.cleanup()
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Navigate to Lindy
        await self.page.goto("https://chat.lindy.ai")
        
        print("\nWaiting for you to log in...")
        print("The automation will continue once you're logged in.")
        
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
        
        # Save the session
        await self.save_session()
        
        # Close visible browser and reopen headless
        await self.cleanup()
        await self.setup(use_saved_session=True)
        
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
            print("→ Waiting 5 seconds for page to fully load...")
            await self.page.wait_for_timeout(5000)
            
            # Verify we're on the right page
            current_url = self.page.url
            print(f"→ Verifying URL: {current_url}")
            
            # Check if we need to login
            if 'login' in current_url or 'signin' in current_url or 'signup' in current_url:
                print("✗ ERROR: Not logged in!")
                return False
            
            print("✓ URL verified")
            
            # Take screenshot before looking for button
            await self.page.screenshot(path='screenshot_1_template_page.png', full_page=True)
            print("→ Screenshot saved: screenshot_1_template_page.png")
            
            # Current URL for debugging
            print(f"→ Current URL before button search: {current_url}")
            
            # Wait for the template modal/dialog to appear
            # The template details are usually shown in a modal or specific container
            print("\n→ Looking for 'Add' button...")
            
            # Try multiple strategies to find the correct Add button
            add_button = None
            
            # Strategy 1: Look for button within a dialog/modal
            print("  Trying selector: [role='dialog'] button:has-text('Add')")
            try:
                add_button = await self.page.wait_for_selector("[role='dialog'] button:has-text('Add')", timeout=3000)
                if add_button:
                    print("✓ Found Add button in dialog")
            except:
                pass
            
            # Strategy 2: Look for button with specific data attributes or classes
            if not add_button:
                print("  Trying selector: button[class*='template'] >> text='Add'")
                try:
                    add_button = await self.page.wait_for_selector("button[class*='template'] >> text='Add'", timeout=3000)
                    if add_button:
                        print("✓ Found Add button with template class")
                except:
                    pass
            
            # Strategy 3: Find all buttons with "Add" and filter by visibility and position
            if not add_button:
                print("  Trying to find all 'Add' buttons and selecting the visible one...")
                try:
                    all_add_buttons = await self.page.query_selector_all("button:has-text('Add')")
                    print(f"  Found {len(all_add_buttons)} buttons with 'Add' text")
                    
                    # Filter for visible buttons in the center of the page
                    for i, btn in enumerate(all_add_buttons):
                        is_visible = await btn.is_visible()
                        box = await btn.bounding_box()
                        
                        if is_visible and box:
                            print(f"  Button {i}: visible={is_visible}, x={box['x']:.0f}, y={box['y']:.0f}, width={box['width']:.0f}, height={box['height']:.0f}")
                            
                            # The template Add button is usually in the center/right area of the page
                            # and not in the top navigation (y > 100)
                            if box['y'] > 100 and box['x'] > 300:
                                add_button = btn
                                print(f"✓ Selected button {i} as the template Add button")
                                break
                except Exception as e:
                    print(f"  Error finding buttons: {e}")
            
            # Strategy 4: Look for specific button text variations
            if not add_button:
                selectors = [
                    "button:has-text('Use template')",
                    "button:has-text('Use this template')",
                    "button:has-text('Add to workspace')",
                    "button:has-text('Add template')"
                ]
                
                for selector in selectors:
                    print(f"  Trying selector: {selector}")
                    try:
                        add_button = await self.page.wait_for_selector(selector, timeout=3000)
                        if add_button:
                            print(f"✓ Found Add button with selector: {selector}")
                            break
                    except:
                        continue
            
            # Strategy 5: Use JavaScript to find the button more precisely
            if not add_button:
                print("  Trying JavaScript approach...")
                try:
                    add_button = await self.page.evaluate_handle("""
                        () => {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            // Find button with "Add" text that's not in navigation
                            const addButton = buttons.find(btn => {
                                const text = btn.textContent.trim();
                                const rect = btn.getBoundingClientRect();
                                // Must contain "Add", be visible, and be in main content area
                                return text === 'Add' && 
                                       rect.y > 100 && 
                                       rect.x > 300 &&
                                       window.getComputedStyle(btn).display !== 'none';
                            });
                            return addButton;
                        }
                    """)
                    
                    if add_button:
                        print("✓ Found Add button using JavaScript")
                except Exception as e:
                    print(f"  JavaScript approach failed: {e}")
            
            if not add_button:
                print("✗ ERROR: Could not find Add button")
                await self.page.screenshot(path='screenshot_error_no_add_button.png', full_page=True)
                return False
            
            # Get button position before clicking
            try:
                box = await add_button.bounding_box()
                if box:
                    print(f"→ Add button position: x={box['x']:.0f}, y={box['y']:.0f}")
            except:
                pass
            
            # URL before clicking
            print(f"→ URL before clicking Add button: {self.page.url}")
            
            # Click the Add button
            print("\n→ Clicking 'Add' button...")
            try:
                # Try normal click first
                await add_button.click(timeout=5000)
                print("✓ Clicked Add button (normal click)")
            except:
                # If normal click fails, try force click
                try:
                    await add_button.click(force=True, timeout=5000)
                    print("✓ Clicked Add button (force click)")
                except Exception as e:
                    print(f"✗ Failed to click: {e}")
                    # Try JavaScript click as last resort
                    await self.page.evaluate("(button) => button.click()", add_button)
                    print("✓ Clicked Add button (JavaScript click)")
            
            # Wait for navigation or modal to close
            await self.page.wait_for_timeout(5000)
            
            # Check URL after clicking
            current_url = self.page.url
            print(f"→ URL after clicking Add button: {current_url}")
            
            # Take screenshot after clicking
            await self.page.screenshot(path='screenshot_2_after_add.png', full_page=True)
            print("→ Screenshot saved: screenshot_2_after_add.png")
            
            # Verify we navigated to the template page (not back to home)
            if '/home' in current_url and 'templateId' not in current_url:
                print("✗ WARNING: Returned to home page - Add button click may have failed")
                print("→ Attempting to navigate to template again...")
                
                # Try to find the template in the workspace
                await self.page.wait_for_timeout(3000)
                
                # Look for the newly added template
                try:
                    # Templates are usually shown as cards or list items
                    template_link = await self.page.wait_for_selector("a[href*='/editor'], a[href*='/tasks']", timeout=10000)
                    if template_link:
                        print("✓ Found template link, clicking...")
                        await template_link.click()
                        await self.page.wait_for_timeout(3000)
                        current_url = self.page.url
                        print(f"→ Navigated to: {current_url}")
                except Exception as e:
                    print(f"✗ Could not find template: {e}")
                    return False
            
            # Modify URL from /tasks to /editor if needed
            if '/tasks' in current_url:
                editor_url = current_url.replace('/tasks', '/editor')
                print(f"→ Navigating to editor view: {editor_url}")
                await self.page.goto(editor_url, wait_until='networkidle', timeout=60000)
                await self.page.wait_for_timeout(3000)
                print("✓ Successfully navigated to editor view")
                
                # Take screenshot of editor view
                await self.page.screenshot(path='screenshot_2b_editor_view.png', full_page=True)
                print("→ Screenshot saved: screenshot_2b_editor_view.png")
            
            print("\n✓ Template added successfully")
            return True
            
        except Exception as e:
            print(f"\n✗ Error adding template: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_template.png', full_page=True)
            return False

    async def configure_webhook(self):
        """Find webhook step and configure it"""
        print("\n" + "="*70)
        print("CONFIGURING WEBHOOK")
        print("="*70)
        
        try:
            # Wait for page to load
            await self.page.wait_for_timeout(5000)
            
            # Scroll to top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot
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
                create_btn = await self.page.query_selector("button:has-text('Create Webhook'), button:has-text('Create webhook')")
                if not create_btn:
                    print("ERROR: Could not find Create Webhook button")
                    await self.page.screenshot(path='screenshot_error_no_create.png')
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
            
            # Save
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
        """Run the automation"""
        try:
            # Setup browser
            await self.setup(use_saved_session=True)
            
            # Check if logged in
            if not await self.check_login_status():
                print("\nNot logged in. Need to establish session...")
                await self.manual_login_prompt()
                
                # Verify login worked
                if not await self.check_login_status():
                    print("\n!!! Still not logged in. Aborting.")
                    return False
            
            # Run the automation steps
            if not await self.add_template():
                print("\n!!! Failed to add template")
                return False
            
            if not await self.configure_webhook():
                print("\n!!! Failed to configure webhook")
                return False
            
            await self.deploy_lindy()
            
            if not await self.configure_n8n():
                print("\n!!! Failed to configure N8N")
                return False
            
            await self.wait_period()
            
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
    print("\n" + "="*70)
    print("Lindy Automation - Final Version")
    print("="*70 + "\n")
    
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

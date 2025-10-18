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
            storage_state=storage_state,
            permissions=["clipboard-read", "clipboard-write"]  # Grant clipboard permissions
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
            
            # Find and click the Add button
            # Use JavaScript to find and click the button to avoid any Playwright click issues
            print("→ Looking for Add button...")
            
            clicked = await self.page.evaluate("""
                () => {
                    // Find all buttons
                    const buttons = Array.from(document.querySelectorAll('button'));
                    
                    // Find button with exact text "Add"
                    const addButton = buttons.find(btn => {
                        const text = btn.textContent.trim();
                        const rect = btn.getBoundingClientRect();
                        
                        // Log all buttons with "Add" for debugging
                        if (text.includes('Add')) {
                            console.log('Found button:', text, 'at position:', rect.x, rect.y);
                        }
                        
                        // Find the Add button that's visible and in the main content area
                        // Not in the top navigation (y > 150) and visible
                        return text === 'Add' && 
                               rect.y > 150 && 
                               rect.width > 0 && 
                               rect.height > 0 &&
                               window.getComputedStyle(btn).visibility === 'visible';
                    });
                    
                    if (addButton) {
                        console.log('Clicking Add button at:', addButton.getBoundingClientRect());
                        addButton.click();
                        return true;
                    }
                    
                    return false;
                }
            """)
            
            if clicked:
                print("✓ Clicked Add button")
            else:
                print("✗ Could not find Add button")
                return False
            
            # Wait for navigation
            await self.page.wait_for_timeout(5000)
            
            # Check new URL
            current_url = self.page.url
            print(f"→ URL after clicking: {current_url}")
            
            # Take screenshot
            await self.page.screenshot(path='screenshot_2_after_add.png', full_page=True)
            print("→ Screenshot saved: screenshot_2_after_add.png")
            
            # Navigate to editor view if we're on tasks view
            if '/tasks' in current_url:
                editor_url = current_url.replace('/tasks', '/editor')
                print(f"→ Navigating to editor: {editor_url}")
                await self.page.goto(editor_url, wait_until='networkidle', timeout=60000)
                await self.page.wait_for_timeout(3000)
                print("✓ Navigated to editor view")
                
                await self.page.screenshot(path='screenshot_2b_editor_view.png', full_page=True)
                print("→ Screenshot saved: screenshot_2b_editor_view.png")
            
            print("✓ Template added successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error adding template: {e}")
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
                await self.page.wait_for_timeout(2000)
                print("✓ Clicked Create Webhook (opened dropdown)")
                
                # After clicking "Create New", type "webhook" and press Enter
                print("→ Typing 'webhook' in the dropdown...")
                await self.page.keyboard.type("webhook")
                await self.page.wait_for_timeout(1000)
                print("✓ Typed 'webhook'")
                
                print("→ Pressing Enter to create webhook...")
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(3000)
                print("✓ Pressed Enter - webhook should be created")
                
                await self.page.screenshot(path='screenshot_5_webhook_created.png')
                print("✓ Screenshot saved: screenshot_5_webhook_created.png")
                
                # Click on the newly created webhook to open it
                print("\n→ Clicking on the newly created webhook...")
                webhook_selectors = [
                    "button:has-text('webhook')",
                    "div:has-text('webhook')",
                    "[role='button']:has-text('webhook')",
                    "a:has-text('webhook')"
                ]
                
                webhook_clicked = False
                for selector in webhook_selectors:
                    try:
                        webhook_element = await self.page.wait_for_selector(selector, timeout=3000)
                        if webhook_element:
                            await webhook_element.click()
                            await self.page.wait_for_timeout(2000)
                            print(f"✓ Clicked on webhook: {selector}")
                            webhook_clicked = True
                            break
                    except:
                        continue
                
                if not webhook_clicked:
                    print("ERROR: Could not find the webhook to click")
                    await self.page.screenshot(path='screenshot_error_no_webhook.png')
                    return False
                
                # Click the "Copy to clipboard" button to get the webhook URL
                print("\n→ Clicking 'Copy to clipboard' button...")
                copy_selectors = [
                    "button:has-text('Copy to clipboard')",
                    "button:has-text('Copy')",
                    "button[title*='Copy']",
                    "[aria-label*='Copy']"
                ]
                
                copy_clicked = False
                for selector in copy_selectors:
                    try:
                        copy_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if copy_btn:
                            await copy_btn.click()
                            await self.page.wait_for_timeout(1000)
                            print(f"✓ Clicked copy button: {selector}")
                            copy_clicked = True
                            break
                    except:
                        continue
                
                if not copy_clicked:
                    print("ERROR: Could not find 'Copy to clipboard' button")
                    await self.page.screenshot(path='screenshot_error_no_copy.png')
                    return False
                
                # Get the URL from clipboard using CDP
                print("\n→ Getting webhook URL from clipboard...")
                try:
                    cdp = await self.context.new_cdp_session(self.page)
                    clipboard_data = await cdp.send('Runtime.evaluate', {
                        'expression': 'navigator.clipboard.readText()',
                        'awaitPromise': True
                    })
                    self.lindy_url = clipboard_data['result']['value']
                    print(f"✓ Got webhook URL from clipboard: {self.lindy_url}")
                except Exception as e:
                    print(f"ERROR getting URL from clipboard: {e}")
                    # Fallback: try to find the URL in the page
                    try:
                        url_element = await self.page.wait_for_selector("input[value*='https://'], code:has-text('https://'), pre:has-text('https://')", timeout=5000)
                        if url_element:
                            self.lindy_url = await url_element.text_content() or await url_element.input_value()
                            print(f"✓ Got webhook URL from page: {self.lindy_url}")
                    except:
                        print("ERROR: Could not retrieve webhook URL")
                        return False
            
            
            
            # Take screenshot before looking for generate secret button
            await self.page.screenshot(path='screenshot_5_5_before_generate.png')
            print("✓ Screenshot saved: screenshot_5_5_before_generate.png")
            
            # STEP 1: Click the first "Generate Secret" button to open the dialog
            print("\n→ Looking for first Generate Secret button...")
            
            # Wait a bit to ensure page is fully loaded
            await self.page.wait_for_timeout(2000)
            
            first_generate_selectors = [
                "button:has-text('Generate Secret')",
                "button:has-text('Generate secret')",
                "a:has-text('Generate Secret')",
                "a:has-text('Generate secret')"
            ]
            
            first_generate_btn = None
            for selector in first_generate_selectors:
                try:
                    first_generate_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if first_generate_btn:
                        button_text = await first_generate_btn.text_content()
                        print(f"✓ Found first generate secret button: {selector}")
                        print(f"→ Button text: '{button_text}'")
                        await first_generate_btn.click()
                        await self.page.wait_for_timeout(3000)
                        print("✓ Clicked first generate secret button")
                        
                        # Take screenshot after clicking first button
                        await self.page.screenshot(path='screenshot_5_6_after_first_generate.png')
                        print("✓ Screenshot saved: screenshot_5_6_after_first_generate.png")
                        break
                except Exception as e:
                    print(f"→ Error with selector {selector}: {e}")
                    continue
            
            if not first_generate_btn:
                print("ERROR: Could not find first Generate Secret button")
                await self.page.screenshot(path='screenshot_error_no_first_generate.png')
                return False
            
            # Count existing copy buttons BEFORE clicking second generate button
            print("\n→ Counting existing copy buttons before generating secret...")
            existing_copy_buttons = await self.page.query_selector_all("button[title*='Copy' i], button[aria-label*='Copy' i]")
            initial_copy_count = len(existing_copy_buttons)
            print(f"→ Found {initial_copy_count} copy buttons before secret generation")
            
            # STEP 2: Click the second "Generate Secret" button in the dialog/modal
            print("\n→ Looking for second Generate Secret button in dialog...")
            
            # Wait longer for dialog/modal to fully appear and animations to complete
            await self.page.wait_for_timeout(3000)
            
            second_generate_selectors = [
                "div[role='dialog'] button:has-text('Generate Secret')",
                "div[role='dialog'] button:has-text('Generate secret')",
                "div[role='dialog'] button:has-text('Generate')",
                "[role='dialog'] button:has-text('Generate Secret')",
                "[role='dialog'] button:has-text('Generate secret')",
                "button:has-text('Generate Secret')",
                "button:has-text('Generate secret')"
            ]
            
            second_generate_btn = None
            for selector in second_generate_selectors:
                try:
                    # Look for all matching buttons
                    buttons = await self.page.query_selector_all(selector)
                    print(f"→ Found {len(buttons)} buttons matching: {selector}")
                    
                    for btn in buttons:
                        button_text = await btn.text_content()
                        print(f"→ Button text: '{button_text}'")
                        
                        # Click the button if it contains "generate"
                        if 'generate' in button_text.lower():
                            second_generate_btn = btn
                            print(f"✓ Found second generate secret button: {selector}")
                            
                            # Try multiple click methods
                            try:
                                # Method 1: Force click (ignores overlays)
                                await second_generate_btn.click(force=True)
                                print("✓ Clicked second generate secret button (force click)")
                            except Exception as e1:
                                print(f"→ Force click failed: {e1}")
                                try:
                                    # Method 2: JavaScript click
                                    await self.page.evaluate("(element) => element.click()", second_generate_btn)
                                    print("✓ Clicked second generate secret button (JavaScript click)")
                                except Exception as e2:
                                    print(f"→ JavaScript click failed: {e2}")
                                    # Method 3: Regular click with longer timeout
                                    await second_generate_btn.click(timeout=10000)
                                    print("✓ Clicked second generate secret button (regular click)")
                            
                            await self.page.wait_for_timeout(3000)
                            print("✓ Secret key should now be created!")
                            
                            # Take screenshot after clicking second button
                            await self.page.screenshot(path='screenshot_5_7_after_second_generate.png')
                            print("✓ Screenshot saved: screenshot_5_7_after_second_generate.png")
                            break
                    
                    if second_generate_btn:
                        break
                except Exception as e:
                    print(f"→ Error with selector {selector}: {e}")
                    continue
            
            if not second_generate_btn:
                print("WARNING: Could not find second Generate Secret button")
                await self.page.screenshot(path='screenshot_error_no_second_generate.png')
                print("✓ Screenshot saved: screenshot_error_no_second_generate.png")
            
            # STEP 3: Wait for NEW copy button to appear and click it
            print("\n→ Waiting for NEW copy button to appear after secret generation...")
            
            # Wait a bit for the new copy button to appear
            await self.page.wait_for_timeout(2000)
            
            # Helper function to validate if string is a hex secret
            def is_hex_secret(value):
                """Check if value is a hexadecimal secret key (like c8f50ee43017ae1e59be6f1e2c5b1389fc304f6a3ff14a0e7a7735b8f159b300)"""
                if not value or len(value) < 40:
                    return False
                # Check if it's all hexadecimal characters (0-9, a-f)
                import re
                return bool(re.match(r'^[0-9a-fA-F]{40,}$', value.strip()))
            
            token_copied = False
            
            # Look for copy buttons that appeared AFTER clicking generate
            print("→ Looking for copy buttons with 'Copy to clipboard' tooltip...")
            copy_button_selectors = [
                "button[title='Copy to clipboard']",
                "button[aria-label='Copy to clipboard']",
                "button[title*='Copy to clipboard' i]",
                "button[aria-label*='Copy to clipboard' i]"
            ]
            
            for selector in copy_button_selectors:
                try:
                    all_copy_buttons = await self.page.query_selector_all(selector)
                    print(f"→ Found {len(all_copy_buttons)} buttons with selector: {selector}")
                    
                    # Try buttons that weren't there before (new ones)
                    for i, copy_btn in enumerate(all_copy_buttons):
                        try:
                            is_visible = await copy_btn.is_visible()
                            if not is_visible:
                                print(f"→ Copy button {i+1} is not visible, skipping")
                                continue
                            
                            # Get the title/aria-label to confirm it's "Copy to clipboard"
                            title = await copy_btn.get_attribute('title') or await copy_btn.get_attribute('aria-label') or ''
                            print(f"→ Copy button {i+1} title: '{title}'")
                            
                            print(f"→ Clicking copy button {i+1}...")
                            await copy_btn.click(force=True)
                            await self.page.wait_for_timeout(1500)
                            print(f"✓ Clicked copy button {i+1}")
                            
                            # Get token from clipboard
                            try:
                                cdp = await self.context.new_cdp_session(self.page)
                                clipboard_data = await cdp.send('Runtime.evaluate', {
                                    'expression': 'navigator.clipboard.readText()',
                                    'awaitPromise': True
                                })
                                clipboard_value = clipboard_data['result']['value']
                                
                                print(f"→ Clipboard contains: {clipboard_value[:60] if clipboard_value else 'empty'}...")
                                
                                # Check if this is a hexadecimal secret key (not the webhook URL)
                                if is_hex_secret(clipboard_value):
                                    self.auth_token = clipboard_value.strip()
                                    print(f"✓ Got hex secret token from clipboard: {self.auth_token[:20]}... (length: {len(self.auth_token)})")
                                    token_copied = True
                                    break
                                else:
                                    print(f"→ Not a hex secret (might be webhook URL, trying next button)")
                            except Exception as e:
                                print(f"→ Error getting from clipboard: {e}")
                        except Exception as e:
                            print(f"→ Error with copy button {i+1}: {e}")
                            continue
                    
                    if token_copied:
                        break
                except Exception as e:
                    print(f"→ Error with selector {selector}: {e}")
                    continue
            
            # If specific selectors didn't work, try all copy buttons and filter by clipboard content
            if not token_copied:
                print("\n→ Trying all copy buttons and checking clipboard content...")
                all_copy_selectors = [
                    "button[title*='Copy' i]",
                    "button[aria-label*='Copy' i]"
                ]
                
                for selector in all_copy_selectors:
                    try:
                        all_buttons = await self.page.query_selector_all(selector)
                        print(f"→ Found {len(all_buttons)} total copy buttons")
                        
                        # Try buttons starting from the end (newest buttons)
                        for i in range(len(all_buttons) - 1, -1, -1):
                            try:
                                copy_btn = all_buttons[i]
                                is_visible = await copy_btn.is_visible()
                                if not is_visible:
                                    continue
                                
                                print(f"→ Trying copy button {i+1}...")
                                await copy_btn.click(force=True)
                                await self.page.wait_for_timeout(1500)
                                
                                cdp = await self.context.new_cdp_session(self.page)
                                clipboard_data = await cdp.send('Runtime.evaluate', {
                                    'expression': 'navigator.clipboard.readText()',
                                    'awaitPromise': True
                                })
                                clipboard_value = clipboard_data['result']['value']
                                
                                print(f"→ Clipboard: {clipboard_value[:60] if clipboard_value else 'empty'}...")
                                
                                if is_hex_secret(clipboard_value):
                                    self.auth_token = clipboard_value.strip()
                                    print(f"✓ Got hex secret token: {self.auth_token[:20]}... (length: {len(self.auth_token)})")
                                    token_copied = True
                                    break
                            except Exception as e:
                                print(f"→ Error with button {i+1}: {e}")
                                continue
                        
                        if token_copied:
                            break
                    except Exception as e:
                        print(f"→ Error: {e}")
                        continue
            
            # Last resort: try to read secret directly from page elements
            if not token_copied:
                print("\n→ Trying to read secret directly from page elements...")
                secret_selectors = [
                    "div[role='dialog'] input[readonly]",
                    "div[role='dialog'] input[type='text']",
                    "div[role='dialog'] code",
                    "div[role='dialog'] pre",
                    "[role='dialog'] input",
                    "[role='dialog'] code"
                ]
                
                for selector in secret_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        print(f"→ Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                value = await element.input_value() if 'input' in selector else await element.text_content()
                                if value:
                                    print(f"→ Element contains: {value[:60]}...")
                                    if is_hex_secret(value):
                                        self.auth_token = value.strip()
                                        print(f"✓ Got hex secret from element: {self.auth_token[:20]}... (length: {len(self.auth_token)})")
                                        token_copied = True
                                        break
                            except:
                                continue
                        
                        if token_copied:
                            break
                    except:
                        continue
            
            if not token_copied:
                print("WARNING: Could not retrieve hex secret token")
                await self.page.screenshot(path='screenshot_error_no_secret.png')
                print("✓ Screenshot saved: screenshot_error_no_secret.png")
                self.auth_token = ""
            
            # Close dialog
            print("\n→ Closing secret dialog...")
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(1000)
            print("✓ Closed dialog")
            
            return True
                        
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_webhook.png')
            return False
        print("\n" + "="*70)
        print("CONFIGURING N8N")
        print("="*70)
        
        if not self.lindy_url:
            print("ERROR: No webhook URL!")
            return False
        
        try:
            print(f"\n→ Navigating to N8N: {config.N8N_URL}")
            await self.page.goto(config.N8N_URL, wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(5000)
            print("✓ N8N page loaded")
            
            await self.page.screenshot(path='screenshot_8_n8n.png')
            print("✓ Screenshot saved: screenshot_8_n8n.png")
            
            # First, let's find all input fields on the page for debugging
            print("\n→ Looking for input fields on the page...")
            all_inputs = await self.page.query_selector_all("input")
            print(f"✓ Found {len(all_inputs)} input fields")
            
            # Try to identify the Lindy URL input field
            print("\n→ Locating Lindy URL input field...")
            lindy_input = None
            lindy_selectors = [
                "input[placeholder*='Lindy URL' i]",
                "input[placeholder*='lindy' i]",
                "input[name*='lindy' i]",
                "input[id*='lindy' i]",
                "input[type='text']",
                "input[type='url']"
            ]
            
            for selector in lindy_selectors:
                try:
                    lindy_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if lindy_input:
                        print(f"✓ Found Lindy URL input using selector: {selector}")
                        break
                except:
                    continue
            
            # If still not found, try to find by position (first input field)
            if not lindy_input and len(all_inputs) > 0:
                lindy_input = all_inputs[0]
                print("✓ Using first input field for Lindy URL")
            
            if not lindy_input:
                print("ERROR: Could not find Lindy URL input field")
                await self.page.screenshot(path='screenshot_error_no_lindy_input.png')
                return False
            
            # Fill Lindy URL
            print(f"\n→ Entering Lindy URL: {self.lindy_url}")
            await lindy_input.click()
            await self.page.wait_for_timeout(500)
            await self.page.keyboard.press('Control+A')
            await lindy_input.fill(self.lindy_url)
            await self.page.wait_for_timeout(1000)
            print(f"✓ Entered Lindy URL")
            
            # Try to identify the Authorization Token input field
            print("\n→ Locating Authorization Token input field...")
            auth_input = None
            auth_selectors = [
                "input[placeholder*='Authorization' i]",
                "input[placeholder*='Token' i]",
                "input[placeholder*='auth' i]",
                "input[name*='token' i]",
                "input[name*='auth' i]",
                "input[id*='token' i]",
                "input[id*='auth' i]"
            ]
            
            for selector in auth_selectors:
                try:
                    auth_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if auth_input:
                        print(f"✓ Found Authorization Token input using selector: {selector}")
                        break
                except:
                    continue
            
            # If still not found, try second input field
            if not auth_input and len(all_inputs) > 1:
                auth_input = all_inputs[1]
                print("✓ Using second input field for Authorization Token")
            
            if auth_input:
                print(f"\n→ Entering authorization token...")
                await auth_input.click()
                await self.page.wait_for_timeout(500)
                await self.page.keyboard.press('Control+A')
                await auth_input.fill(self.auth_token if self.auth_token else "")
                await self.page.wait_for_timeout(1000)
                print(f"✓ Entered auth token")
            else:
                print("WARNING: Could not find Authorization Token input field")
            
            await self.page.screenshot(path='screenshot_9_n8n_filled.png')
            print("✓ Screenshot saved: screenshot_9_n8n_filled.png")
            
            # Save
            print("\n→ Saving configuration...")
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

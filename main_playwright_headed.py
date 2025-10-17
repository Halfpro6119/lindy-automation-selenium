"""
Lindy Automation Script - Headed Mode (Visible Browser)
This version runs with a visible browser so you can see what's happening
Browser stays open throughout the entire process
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
        
        # Launch browser in HEADED mode (visible) with larger window
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Browser is visible
            args=[
                '--start-maximized',  # Start maximized
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
        
        # Create context with larger viewport
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
        
        print("✓ Browser setup complete and visible!")
        print("✓ You can now see everything the automation is doing")
        print("✓ Clipboard permissions granted automatically")
        
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
        print("\n→ Checking login status...")
        try:
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            print(f"  Current URL: {current_url}")
            
            # Check if we're on a workspace/home page (logged in)
            if 'workspace' in current_url or '/home' in current_url:
                print("✓ Already logged in!")
                return True
            
            # Check for login/signup page
            if 'login' in current_url or 'signin' in current_url or 'signup' in current_url:
                print("✗ Not logged in")
                return False
            
            # Check for New Agent button with error handling
            try:
                new_agent_btn = await self.page.query_selector("button:has-text('New Agent')")
                if new_agent_btn:
                    print("✓ Already logged in!")
                    return True
            except Exception:
                pass
            
            print("✗ Not logged in")
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    async def manual_login_prompt(self):
        """Prompt for manual login - browser stays open"""
        print("\n" + "="*70)
        print("MANUAL LOGIN REQUIRED")
        print("="*70)
        print("\n→ The browser window is now open and visible")
        print("→ Please log in manually in the browser window")
        print("\nSteps:")
        print("1. Log in to Lindy with your Google account")
        print("2. Wait until you see the Lindy workspace/home page")
        print("3. The automation will detect the login and continue automatically")
        print("\n→ Waiting for you to log in...")
        print("→ Browser will stay open throughout the entire process")
        
        # Navigate to Lindy
        print("\n→ Navigating to Lindy login page...")
        await self.page.goto("https://chat.lindy.ai")
        await self.page.wait_for_timeout(2000)
        
        # Wait for login (check every 5 seconds)
        max_wait = 300  # 5 minutes
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(5)
            waited += 5
            
            try:
                # Wait for page to be stable after navigation
                await self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            
            current_url = self.page.url
            
            # Check URL for login success
            if 'workspace' in current_url or '/home' in current_url:
                print("\n✓ Login detected!")
                break
            
            # Try to find New Agent button with error handling
            try:
                new_agent_btn = await self.page.query_selector("button:has-text('New Agent')")
                if new_agent_btn:
                    print("\n✓ Login detected!")
                    break
            except Exception:
                # Ignore errors during navigation
                pass
            
            print(f"  Still waiting for login... ({waited}s elapsed)")
        
        # Wait a bit more to ensure page is stable
        await self.page.wait_for_timeout(3000)
        
        # Save the session
        print("\n→ Saving login session for future use...")
        await self.save_session()
        print("✓ Session saved!")
        
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
        print("STEP 2: CONFIGURING WEBHOOK")
        print("="*70)
        
        try:
            # Wait for page to load
            print("\n→ Waiting for page to load...")
            await self.page.wait_for_timeout(5000)
            
            # Scroll to top
            print("→ Scrolling to top of page...")
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot
            await self.page.screenshot(path='screenshot_3_before_webhook.png')
            print("✓ Screenshot saved: screenshot_3_before_webhook.png")
            
            # Look for webhook trigger
            print("\n→ Looking for webhook element...")
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
            print("\n→ Clicking webhook element...")
            await webhook_element.click()
            await self.page.wait_for_timeout(3000)
            print("✓ Webhook element opened")
            
            await self.page.screenshot(path='screenshot_4_webhook_opened.png')
            print("✓ Screenshot saved: screenshot_4_webhook_opened.png")
            
            # NEW: Click "Select an option" button to open dropdown
            print("\n→ Looking for 'Select an option' button...")
            select_option_selectors = [
                "button:has-text('Select an option')",
                "button:has-text('select an option')",
                "[role='combobox']:has-text('Select')",
                "button:has-text('Select')"
            ]
            
            select_btn = None
            for selector in select_option_selectors:
                try:
                    select_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if select_btn:
                        print(f"✓ Found 'Select an option' button: {selector}")
                        break
                except:
                    continue
            
            if select_btn:
                print("→ Clicking 'Select an option' button...")
                await select_btn.click()
                await self.page.wait_for_timeout(2000)
                print("✓ Dropdown opened")
                
                await self.page.screenshot(path='screenshot_4b_dropdown_opened.png')
                print("✓ Screenshot saved: screenshot_4b_dropdown_opened.png")
            else:
                print("→ No 'Select an option' button found, checking if webhook already exists...")
            
            # Check if webhook already exists
            print("\n→ Checking for existing webhook...")
            existing_url = await self.page.query_selector("input[value*='https://']")
            if existing_url:
                self.lindy_url = await existing_url.input_value()
                print(f"✓ Found existing webhook URL: {self.lindy_url}")
            else:
                # Create new webhook - look for "Create new" button
                print("→ Creating new webhook...")
                create_btn_selectors = [
                    "button:has-text('Create new')",
                    "button:has-text('Create New')",
                    "button:has-text('Create Webhook')",
                    "button:has-text('Create webhook')"
                ]
                
                create_btn = None
                for selector in create_btn_selectors:
                    try:
                        create_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if create_btn:
                            print(f"✓ Found create button: {selector}")
                            break
                    except:
                        continue
                
                if not create_btn:
                    print("ERROR: Could not find Create button")
                    await self.page.screenshot(path='screenshot_error_no_create.png')
                    return False
                
                await create_btn.click()
                await self.page.wait_for_timeout(2000)
                print("✓ Clicked Create button (opened dropdown)")
                
                # After clicking "Create New", type "webhook" and press Enter
                print("\n→ Naming the webhook...")
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
            
            
            
            # First, look for and click the "Generate Secret" button to create the secret
            print("\n→ Looking for Generate Secret button...")
            generate_secret_selectors = [
                "button:has-text('Generate Secret')",
                "button:has-text('Generate secret')",
                "button:has-text('generate secret')",
                "button[aria-label*='Generate Secret' i]",
                "button[aria-label*='Generate secret' i]",
                "a:has-text('Generate Secret')",
                "a:has-text('Generate secret')"
            ]
            
            generate_btn = None
            for selector in generate_secret_selectors:
                try:
                    generate_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if generate_btn:
                        print(f"✓ Found generate secret button: {selector}")
                        await generate_btn.click()
                        await self.page.wait_for_timeout(2000)
                        print("✓ Clicked generate secret button")
                        break
                except:
                    continue
            
            if not generate_btn:
                print("INFO: No generate secret button found, secret may already exist")
            
            # Now get authorization token
            print("\n→ Getting authorization token...")
            secret_selectors = [
                "button:has-text('secret')",
                "button:has-text('Secret')",
                "button:has-text('Show secret')",
                "button:has-text('View secret')",
                "button[aria-label*='secret' i]"
            ]
            
            secret_btn = None
            for selector in secret_selectors:
                try:
                    secret_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if secret_btn:
                        print(f"✓ Found secret button: {selector}")
                        break
                except:
                    continue
            
            if secret_btn:
                await secret_btn.click()
                await self.page.wait_for_timeout(2000)
                print("✓ Clicked secret button")
                
                await self.page.screenshot(path='screenshot_6_secret.png')
                print("✓ Screenshot saved: screenshot_6_secret.png")
                
                # Try to find and click the copy button for the token
                print("\n→ Looking for token copy button...")
                token_copy_selectors = [
                    "button:has-text('Copy')",
                    "button[title*='Copy' i]",
                    "button[aria-label*='Copy' i]"
                ]
                
                token_copied = False
                for selector in token_copy_selectors:
                    try:
                        # Find all copy buttons and try the second one (first is for URL, second for token)
                        copy_buttons = await self.page.query_selector_all(selector)
                        if len(copy_buttons) > 1:
                            await copy_buttons[1].click()
                            await self.page.wait_for_timeout(1000)
                            print(f"✓ Clicked token copy button")
                            
                            # Get token from clipboard
                            try:
                                cdp = await self.context.new_cdp_session(self.page)
                                clipboard_data = await cdp.send('Runtime.evaluate', {
                                    'expression': 'navigator.clipboard.readText()',
                                    'awaitPromise': True
                                })
                                self.auth_token = clipboard_data['result']['value']
                                print(f"✓ Got auth token from clipboard: {self.auth_token[:20]}...")
                                token_copied = True
                                break
                            except Exception as e:
                                print(f"ERROR getting token from clipboard: {e}")
                    except:
                        continue
                
                # If copy button didn't work, try to get token from input field
                if not token_copied:
                    print("\n→ Trying to get token from input field...")
                    token_selectors = [
                        "input[readonly]",
                        "input[type='text'][value]",
                        "input[type='password']",
                        "code",
                        "pre"
                    ]
                    
                    for selector in token_selectors:
                        try:
                            token_element = await self.page.wait_for_selector(selector, timeout=3000)
                            if token_element:
                                token_value = await token_element.input_value() if selector.startswith('input') else await token_element.text_content()
                                if token_value and len(token_value) > 10:  # Make sure it's not empty
                                    self.auth_token = token_value.strip()
                                    print(f"✓ Got auth token from {selector}: {self.auth_token[:20]}...")
                                    token_copied = True
                                    break
                        except:
                            continue
                
                if not token_copied:
                    print("WARNING: Could not retrieve auth token")
                    self.auth_token = ""
                
                # Close dialog
                print("\n→ Closing secret dialog...")
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(1000)
                print("✓ Closed dialog")
            else:
                print("WARNING: No secret button found")
                self.auth_token = ""
            
            return True
            print(f"ERROR configuring webhook: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_webhook.png')
            return False

    
    async def deploy_lindy(self):
        """Deploy the agent"""
        print("\n" + "="*70)
        print("STEP 3: DEPLOYING AGENT")
        print("="*70)
        
        try:
            print("\n→ Looking for Deploy button...")
            deploy_btn = await self.page.query_selector("button:has-text('Deploy')")
            if not deploy_btn:
                print("WARNING: No Deploy button found - may already be deployed")
                return True
            
            print("→ Clicking Deploy button...")
            await deploy_btn.click()
            await self.page.wait_for_timeout(5000)
            print("✓ Agent deployed!")
            
            await self.page.screenshot(path='screenshot_7_deployed.png')
            print("✓ Screenshot saved: screenshot_7_deployed.png")
            return True
            
        except Exception as e:
            print(f"Note: Deploy: {e}")
            return True
    
    async def configure_n8n(self):
        """Configure N8N"""
        print("\n" + "="*70)
        print("STEP 4: CONFIGURING N8N")
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
            print("\n→ Saving configuration...")
            save_btn = await self.page.wait_for_selector("button:has-text('Save Configuration'), button:has-text('Save')", timeout=10000)
            await save_btn.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(1000)
            await save_btn.click()
            await self.page.wait_for_timeout(3000)
            print("✓ Configuration saved!")
            
            await self.page.screenshot(path='screenshot_10_n8n_saved.png')
            print("✓ Screenshot saved: screenshot_10_n8n_saved.png")
            
            # Start processing
            print("\n→ Starting processing...")
            start_btn = await self.page.query_selector("button:has-text('Start Processing'), button:has-text('Start')")
            if start_btn:
                await start_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Processing started!")
                
                await self.page.screenshot(path='screenshot_11_n8n_started.png')
                print("✓ Screenshot saved: screenshot_11_n8n_started.png")
            
            return True
            
        except Exception as e:
            print(f"ERROR configuring N8N: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_n8n.png')
            return False
    
    async def wait_period(self):
        """Wait 10 minutes"""
        print("\n" + "="*70)
        print("STEP 5: WAITING PERIOD")
        print("="*70)
        
        wait_time = config.WAIT_TIME
        print(f"\n→ Waiting {wait_time} seconds ({wait_time/60} minutes)...")
        print("→ Browser will remain open during this time")
        
        for i in range(0, wait_time, 60):
            remaining = wait_time - i
            print(f"  ⏱  {remaining} seconds remaining...")
            await asyncio.sleep(min(60, remaining))
        
        print("✓ Wait complete!")
        return True
    
    async def delete_account(self):
        """Delete Lindy account"""
        print("\n" + "="*70)
        print("STEP 6: DELETING ACCOUNT")
        print("="*70)
        
        try:
            print("\n→ Navigating to Lindy...")
            await self.page.goto("https://chat.lindy.ai", wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            await self.page.screenshot(path='screenshot_12_before_delete.png')
            print("✓ Screenshot saved: screenshot_12_before_delete.png")
            
            # Find menu
            print("\n→ Looking for menu button...")
            menu_btn = await self.page.query_selector("button[aria-label*='menu' i], [class*='menu'], [class*='avatar']")
            if not menu_btn:
                print("WARNING: No menu button found")
                return False
            
            await menu_btn.click()
            await self.page.wait_for_timeout(2000)
            print("✓ Opened menu")
            
            await self.page.screenshot(path='screenshot_13_menu.png')
            print("✓ Screenshot saved: screenshot_13_menu.png")
            
            # Find Settings
            print("\n→ Looking for Settings...")
            settings_btn = await self.page.query_selector("text='Settings', button:has-text('Settings')")
            if settings_btn:
                await settings_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Opened Settings")
                
                await self.page.screenshot(path='screenshot_14_settings.png')
                print("✓ Screenshot saved: screenshot_14_settings.png")
            
            # Find Delete Account
            print("\n→ Looking for Delete Account button...")
            delete_btn = await self.page.query_selector("button:has-text('Delete Account'), button:has-text('Delete account')")
            if not delete_btn:
                print("WARNING: No Delete Account button found")
                return False
            
            await delete_btn.click()
            await self.page.wait_for_timeout(2000)
            print("✓ Clicked Delete Account")
            
            await self.page.screenshot(path='screenshot_15_delete_confirm.png')
            print("✓ Screenshot saved: screenshot_15_delete_confirm.png")
            
            # Confirm
            print("\n→ Confirming deletion...")
            confirm_btn = await self.page.query_selector("button:has-text('Confirm'), button:has-text('Delete'), button:has-text('Yes')")
            if confirm_btn:
                await confirm_btn.click()
                await self.page.wait_for_timeout(3000)
                print("✓ Deletion confirmed")
            
            await self.page.screenshot(path='screenshot_16_deleted.png')
            print("✓ Screenshot saved: screenshot_16_deleted.png")
            
            print("\n✓ Account deleted successfully!")
            return True
            
        except Exception as e:
            print(f"ERROR deleting account: {e}")
            import traceback
            traceback.print_exc()
            await self.page.screenshot(path='screenshot_error_delete.png')
            return False
    
    async def run(self):
        """Run the automation"""
        try:
            print("\n→ Starting automation with visible browser...")
            
            # Setup browser
            await self.setup(use_saved_session=True)
            
            # Check if logged in
            if not await self.check_login_status():
                print("\n→ Not logged in. Need to establish session...")
                await self.manual_login_prompt()
                
                # Verify login worked
                if not await self.check_login_status():
                    print("\n!!! Still not logged in. Aborting.")
                    print("!!! Browser will remain open for inspection.")
                    await asyncio.sleep(3600)  # Keep open for 1 hour
                    return False
            
            # Run the automation steps
            if not await self.add_template():
                print("\n!!! Failed to add template")
                print("!!! Browser will remain open for inspection.")
                await asyncio.sleep(3600)
                return False
            
            if not await self.configure_webhook():
                print("\n!!! Failed to configure webhook")
                print("!!! Browser will remain open for inspection.")
                await asyncio.sleep(3600)
                return False
            
            await self.deploy_lindy()
            
            if not await self.configure_n8n():
                print("\n!!! Failed to configure N8N")
                print("!!! Browser will remain open for inspection.")
                await asyncio.sleep(3600)
                return False
            
            await self.wait_period()
            
            await self.delete_account()
            
            print("\n" + "="*70)
            print("✓✓✓ AUTOMATION COMPLETED SUCCESSFULLY! ✓✓✓")
            print("="*70)
            print("\n→ Browser will remain open so you can review the results")
            print("→ Press Ctrl+C to close when done")
            
            # Keep browser open indefinitely
            await asyncio.sleep(3600)  # Wait 1 hour before auto-closing
            return True
            
        except KeyboardInterrupt:
            print("\n\n→ Keyboard interrupt detected")
            print("→ Closing browser...")
            return False
        except Exception as e:
            print(f"\n!!! Automation failed: {e}")
            import traceback
            traceback.print_exc()
            print("\n→ Browser will remain open for inspection")
            await asyncio.sleep(3600)
            return False
        finally:
            # Cleanup
            print("\n→ Cleaning up...")
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
                print(f"Note during cleanup: {e}")


async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("Lindy Automation - Headed Mode (Visible Browser)")
    print("Browser will stay open throughout the entire process")
    print("="*70 + "\n")
    
    automation = LindyAutomationPlaywright()
    await automation.run()


if __name__ == "__main__":
    asyncio.run(main())

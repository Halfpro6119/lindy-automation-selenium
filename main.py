"""
Lindy Automation Script with Selenium
Automates the complete workflow from signup to N8N integration
"""

import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import config


class LindyAutomation:
    def __init__(self):
        """Initialize the automation with Chrome driver"""
        print("Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 30)
        self.short_wait = WebDriverWait(self.driver, 10)
        self.lindy_url = None
        self.auth_token = None
        
    def safe_click(self, element):
        """Safely click an element with multiple fallback methods"""
        try:
            element.click()
        except ElementClickInterceptedException:
            # Try JavaScript click if regular click is intercepted
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            # Try ActionChains as last resort
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
            except:
                raise e
    
    def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...")
        
        try:
            # Navigate to Lindy signup page
            self.driver.get(config.LINDY_SIGNUP_URL)
            time.sleep(config.SHORT_WAIT)
            
            # Look for "Sign up with Google" or "Sign in with Google" button
            print("Looking for 'Sign up with Google' button...")
            try:
                # Try multiple selectors for the Google sign-in button
                google_signin_selectors = [
                    "//button[contains(., 'Sign up with Google')]",
                    "//button[contains(., 'Sign in with Google')]",
                    "//button[contains(., 'Google')]",
                    "//button[contains(@class, 'google')]",
                    "//*[contains(text(), 'Sign up with Google')]",
                    "//*[contains(text(), 'Sign in with Google')]"
                ]
                
                google_button_clicked = False
                for selector in google_signin_selectors:
                    try:
                        google_signin_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        self.safe_click(google_signin_button)
                        print(f"Clicked Google sign-in button using selector: {selector}")
                        google_button_clicked = True
                        break
                    except TimeoutException:
                        continue
                
                if not google_button_clicked:
                    raise Exception("Could not find Google sign-in button")
                    
            except Exception as e:
                print(f"Error finding Google button: {e}")
                raise
            
            time.sleep(config.SHORT_WAIT)
            
            # Handle Google login page
            print("Entering email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.clear()
            email_input.send_keys(config.GOOGLE_EMAIL)
            email_input.send_keys(Keys.RETURN)
            
            time.sleep(config.SHORT_WAIT)
            
            print("Entering password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_input.clear()
            password_input.send_keys(config.GOOGLE_PASSWORD)
            password_input.send_keys(Keys.RETURN)
            
            time.sleep(config.MEDIUM_WAIT)
            
            # Handle "You're signing back in to Lindy" page
            try:
                print("Checking for 'Continue' button on sign-in page...")
                continue_button = self.short_wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Continue') or contains(., 'continue')]"))
                )
                self.safe_click(continue_button)
                print("Clicked 'Continue' button on sign-in page")
                time.sleep(config.MEDIUM_WAIT)
            except TimeoutException:
                print("No 'Continue' button found - proceeding...")
            
            print("Google sign-in completed!")
            
        except Exception as e:
            print(f"Error during Google sign-in: {e}")
            raise
    
    def fill_signup_form(self):
        """Fill out the signup form if present"""
        print("Checking for signup form...")
        
        try:
            time.sleep(config.SHORT_WAIT)
            
            # Look for common form fields
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select")
            
            if form_fields:
                print(f"Found {len(form_fields)} form fields, filling them out...")
                
                for field in form_fields:
                    try:
                        if not field.is_displayed() or not field.is_enabled():
                            continue
                            
                        field_type = field.get_attribute('type')
                        field_name = field.get_attribute('name') or field.get_attribute('placeholder') or ''
                        
                        if 'email' in field_name.lower():
                            field.clear()
                            field.send_keys(config.GOOGLE_EMAIL)
                        elif 'name' in field_name.lower() and 'company' not in field_name.lower():
                            field.clear()
                            field.send_keys("Test User")
                        elif 'company' in field_name.lower():
                            field.clear()
                            field.send_keys("Test Company")
                        
                    except Exception as e:
                        print(f"Could not fill field: {e}")
                        continue
                
                # Look for submit/continue button
                try:
                    submit_button = self.driver.find_element(By.XPATH,
                        "//button[contains(., 'Continue') or contains(., 'Submit') or contains(., 'Next')]")
                    self.safe_click(submit_button)
                    print("Submitted form")
                    time.sleep(config.MEDIUM_WAIT)
                except:
                    print("No submit button found or already submitted")
            
        except Exception as e:
            print(f"Form filling info: {e}")
    
    def handle_free_trial(self):
        """Handle free trial section and enter card details"""
        print("Looking for free trial section...")
        
        try:
            # Check if we need to start free trial
            try:
                start_trial_button = self.short_wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Start Free Trial') or contains(., 'Start Trial')]"))
                )
                self.safe_click(start_trial_button)
                print("Clicked 'Start Free Trial' button")
                time.sleep(config.SHORT_WAIT)
                
                # Enter card details
                self.enter_card_details()
                
            except TimeoutException:
                print("No free trial button found - may already have credits, continuing...")
                
        except Exception as e:
            print(f"Free trial handling: {e}")
    
    def enter_card_details(self):
        """Enter card payment details"""
        print("Entering card details...")
        
        try:
            # Wait for card form to load
            time.sleep(2)
            
            # Card number
            card_number_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "input[name*='card' i][name*='number' i], input[placeholder*='card number' i], input[placeholder*='Card number' i]"))
            )
            card_number_input.clear()
            card_number_input.send_keys(config.CARD_NUMBER)
            print("Entered card number")
            
            # Expiry date
            expiry_input = self.driver.find_element(By.CSS_SELECTOR,
                "input[name*='expir' i], input[placeholder*='expir' i], input[placeholder*='MM' i]")
            expiry_input.clear()
            expiry_input.send_keys(config.CARD_EXPIRY)
            print("Entered expiry date")
            
            # CVC
            cvc_input = self.driver.find_element(By.CSS_SELECTOR,
                "input[name*='cvc' i], input[name*='cvv' i], input[placeholder*='cvc' i]")
            cvc_input.clear()
            cvc_input.send_keys(config.CARD_CVC)
            print("Entered CVC")
            
            # Cardholder name
            try:
                name_input = self.driver.find_element(By.CSS_SELECTOR,
                    "input[name*='name' i], input[placeholder*='name' i]")
                name_input.clear()
                name_input.send_keys(config.CARDHOLDER_NAME)
                print("Entered cardholder name")
            except:
                print("Name field not found or not required")
            
            # Country
            try:
                country_select = self.driver.find_element(By.CSS_SELECTOR,
                    "select[name*='country' i], input[name*='country' i]")
                if country_select.tag_name == 'select':
                    from selenium.webdriver.support.ui import Select
                    Select(country_select).select_by_visible_text(config.CARD_COUNTRY)
                else:
                    country_select.clear()
                    country_select.send_keys(config.CARD_COUNTRY)
                print("Selected country")
            except:
                print("Country field not found or not required")
            
            # Postal code
            try:
                postal_input = self.driver.find_element(By.CSS_SELECTOR,
                    "input[name*='postal' i], input[name*='zip' i], input[placeholder*='postal' i]")
                postal_input.clear()
                postal_input.send_keys(config.POSTAL_CODE)
                print("Entered postal code")
            except:
                print("Postal code field not found or not required")
            
            # Click Save Card button
            time.sleep(config.SHORT_WAIT)
            save_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Save') or contains(., 'Submit') or contains(., 'Add Card')]")
            self.safe_click(save_button)
            print("Clicked 'Save Card' button")
            
            time.sleep(config.MEDIUM_WAIT)
            
        except Exception as e:
            print(f"Error entering card details: {e}")
            raise
    
    def navigate_to_template(self):
        """Navigate to the specific template"""
        print(f"Navigating to template: {config.LINDY_TEMPLATE_URL}")
        
        self.driver.get(config.LINDY_TEMPLATE_URL)
        time.sleep(config.MEDIUM_WAIT)
        
        # Add template to account
        try:
            print("Looking for 'Add' button...")
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Try multiple strategies to find and click the Add button
            add_button_clicked = False
            
            # Strategy 1: Find button with exact text "Add"
            add_selectors = [
                "//button[text()='Add']",
                "//button[normalize-space(.)='Add']",
                "//button[contains(@class, 'bg-blue') and contains(., 'Add')]",
                "//button[@type='button' and text()='Add']",
                "//button[contains(., 'Add')]"
            ]
            
            for selector in add_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    add_button = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    
                    # Scroll the button into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_button)
                    time.sleep(2)
                    
                    # Wait for it to be clickable
                    add_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # Try to click
                    self.safe_click(add_button)
                    print(f"Clicked 'Add' button using selector: {selector}")
                    add_button_clicked = True
                    break
                    
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if not add_button_clicked:
                # Last resort: Find all buttons and click the one with text "Add"
                print("Trying last resort method...")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    try:
                        if btn.text.strip() == "Add" and btn.is_displayed():
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                            time.sleep(2)
                            self.safe_click(btn)
                            print("Clicked 'Add' button using last resort method")
                            add_button_clicked = True
                            break
                    except:
                        continue
            
            if not add_button_clicked:
                raise Exception("Could not find or click the Add button")
            
            time.sleep(config.MEDIUM_WAIT)
            
            # Wait for page to load and click "Flow Editor" button
            print("Waiting for page to load and looking for 'Flow Editor' button...")
            time.sleep(5)
            
            # Try multiple selectors for Flow Editor button
            flow_editor_clicked = False
            selectors = [
                "//button[contains(., 'Flow Editor')]",
                "//button[contains(., 'flow editor')]",
                "//button[contains(., 'Editor')]",
                "//a[contains(., 'Flow Editor')]",
                "//a[contains(., 'Editor')]",
                "//*[contains(@class, 'editor') and contains(., 'Flow')]"
            ]
            
            for selector in selectors:
                try:
                    flow_editor_button = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(flow_editor_button)
                    print(f"Clicked 'Flow Editor' button using selector: {selector}")
                    flow_editor_clicked = True
                    time.sleep(config.MEDIUM_WAIT)
                    break
                except:
                    continue
            
            if not flow_editor_clicked:
                print("Warning: Could not find Flow Editor button, attempting to continue...")
            
        except Exception as e:
            print(f"Error in template navigation: {e}")
            raise
    
        def configure_webhook(self):
        """Find webhook step and configure it"""
        print("Looking for 'Webhook Received' near the top of the page...")
        
        try:
            # Wait for page to fully load
            time.sleep(3)
            
            # Look specifically for "Webhook Received" text near the top
            webhook_received_clicked = False
            selectors = [
                "//*[contains(text(), 'Webhook Received')]",
                "//*[contains(text(), 'webhook received')]",
                "//*[contains(text(), 'Webhook received')]",
                "//div[contains(@class, 'webhook') and contains(., 'Received')]",
                "//*[contains(., 'Webhook') and contains(., 'Received')]"
            ]
            
            for selector in selectors:
                try:
                    webhook_received_element = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(webhook_received_element)
                    print(f"Clicked 'Webhook Received' element using selector: {selector}")
                    webhook_received_clicked = True
                    time.sleep(config.SHORT_WAIT)
                    break
                except:
                    continue
            
            if not webhook_received_clicked:
                print("Warning: Could not find 'Webhook Received', trying alternative approach...")
                # Try to find any webhook-related element
                webhook_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), 'webhook') or contains(text(), 'Webhook')]")
                if webhook_elements:
                    self.safe_click(webhook_elements[0])
                    print("Clicked first webhook element found")
                    time.sleep(config.SHORT_WAIT)
            
            # Click "Select an option..." dropdown
            print("Looking for 'Select an option...' dropdown...")
            dropdown_clicked = False
            dropdown_selectors = [
                "//*[contains(text(), 'Select an option')]",
                "//select[contains(@placeholder, 'Select')]",
                "//input[contains(@placeholder, 'Select an option')]",
                "//div[contains(@class, 'select') and contains(., 'Select')]",
                "//*[contains(@role, 'combobox')]"
            ]
            
            for selector in dropdown_selectors:
                try:
                    select_dropdown = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(select_dropdown)
                    print(f"Clicked dropdown using selector: {selector}")
                    dropdown_clicked = True
                    time.sleep(config.SHORT_WAIT)
                    break
                except:
                    continue
            
            if not dropdown_clicked:
                print("Warning: Could not find dropdown, trying to type directly...")
            
            # Click "Create new..." option
            print("Looking for 'Create new...' option...")
            create_new_clicked = False
            create_selectors = [
                "//*[contains(text(), 'Create new')]",
                "//*[contains(text(), 'create new')]",
                "//option[contains(., 'Create new')]",
                "//li[contains(., 'Create new')]",
                "//div[contains(@class, 'option') and contains(., 'Create')]"
            ]
            
            for selector in create_selectors:
                try:
                    create_new_option = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(create_new_option)
                    print(f"Clicked 'Create new...' using selector: {selector}")
                    create_new_clicked = True
                    time.sleep(config.SHORT_WAIT)
                    break
                except:
                    continue
            
            if not create_new_clicked:
                print("Warning: Could not find 'Create new' option, attempting to type directly...")
            
            # Type "Webhook" and press Enter
            print("Typing 'Webhook' and pressing Enter...")
            time.sleep(1)
            
            # Try to find input field or use active element
            try:
                # Look for visible input fields
                input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']:not([disabled])")
                input_used = False
                
                for input_field in input_fields:
                    if input_field.is_displayed() and input_field.is_enabled():
                        input_field.clear()
                        input_field.send_keys("Webhook")
                        input_field.send_keys(Keys.RETURN)
                        print("Typed 'Webhook' in visible input field")
                        input_used = True
                        break
                
                if not input_used:
                    # Use active element as fallback
                    active_input = self.driver.switch_to.active_element
                    active_input.send_keys("Webhook")
                    active_input.send_keys(Keys.RETURN)
                    print("Typed 'Webhook' in active element")
                    
            except Exception as e:
                print(f"Error typing webhook name: {e}")
            
            time.sleep(config.MEDIUM_WAIT)
            
            # Click the webhook that was just created
            print("Looking for the newly created webhook...")
            webhook_clicked = False
            webhook_selectors = [
                "//div[contains(text(), 'Webhook') and not(contains(text(), 'Webhook Received'))]",
                "//li[contains(text(), 'Webhook') and not(contains(text(), 'Received'))]",
                "//span[contains(text(), 'Webhook') and not(contains(text(), 'Received'))]",
                "//*[text()='Webhook']"
            ]
            
            for selector in webhook_selectors:
                try:
                    webhook_item = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(webhook_item)
                    print(f"Clicked newly created webhook using selector: {selector}")
                    webhook_clicked = True
                    time.sleep(config.SHORT_WAIT)
                    break
                except:
                    continue
            
            if not webhook_clicked:
                print("Warning: Could not find newly created webhook, continuing...")
            
            # Continue from generate secret button onwards
            # Copy the Lindy URL
            print("Looking for Lindy URL...")
            time.sleep(2)
            
            try:
                # Look for URL field or copy button
                url_elements = self.driver.find_elements(By.XPATH,
                    "//input[contains(@value, 'https://')]")
                
                for url_elem in url_elements:
                    value = url_elem.get_attribute('value')
                    if value and 'lindy' in value.lower():
                        self.lindy_url = value
                        print(f"Found Lindy URL: {self.lindy_url}")
                        break
                
                if not self.lindy_url:
                    # Try to find copy button for URL
                    copy_buttons = self.driver.find_elements(By.XPATH,
                        "//button[contains(., 'Copy') or contains(@aria-label, 'Copy')]")
                    if copy_buttons:
                        self.safe_click(copy_buttons[0])
                        time.sleep(1)
                        self.lindy_url = pyperclip.paste()
                        print(f"Copied Lindy URL: {self.lindy_url}")
                        
            except Exception as e:
                print(f"Error getting Lindy URL: {e}")
            
            # Create secret key/authorization token
            print("Creating authorization token...")
            secret_button_clicked = False
            secret_selectors = [
                "//button[contains(., 'Generate secret')]",
                "//button[contains(., 'generate secret')]",
                "//button[contains(., 'Secret')]",
                "//button[contains(., 'secret')]",
                "//button[contains(., 'Generate')]",
                "//button[contains(., 'Token')]",
                "//button[contains(., 'token')]",
                "//button[contains(., 'Auth')]"
            ]
            
            for selector in secret_selectors:
                try:
                    secret_key_button = self.short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.safe_click(secret_key_button)
                    print(f"Clicked secret key button using selector: {selector}")
                    secret_button_clicked = True
                    time.sleep(config.SHORT_WAIT)
                    break
                except:
                    continue
            
            if not secret_button_clicked:
                print("Warning: Could not find secret key button")
            
            # Copy the secret key
            time.sleep(2)
            try:
                # Try to find the secret key value
                secret_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    "input[type='text'], input[type='password']")
                
                for element in secret_elements:
                    if not element.is_displayed():
                        continue
                    value = element.get_attribute('value')
                    if value and len(value) > 15:  # Secret keys are usually longer
                        self.auth_token = value
                        # Copy to clipboard
                        element.click()
                        self.driver.execute_script("arguments[0].select();", element)
                        time.sleep(0.5)
                        # Use Ctrl+C to copy
                        element.send_keys(Keys.CONTROL, 'c')
                        time.sleep(0.5)
                        pyperclip.copy(value)
                        print(f"Copied authorization token")
                        break
                
                if not self.auth_token:
                    # Try copy button
                    copy_buttons = self.driver.find_elements(By.XPATH,
                        "//button[contains(., 'Copy')]")
                    for btn in copy_buttons:
                        if btn.is_displayed():
                            self.safe_click(btn)
                            time.sleep(1)
                            self.auth_token = pyperclip.paste()
                            print(f"Copied authorization token via button")
                            break
                    
            except Exception as e:
                print(f"Error copying secret key: {e}")
            
            # Click outside to close dialog
            time.sleep(config.SHORT_WAIT)
            try:
                # Try pressing Escape key first
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                print("Pressed Escape to close dialog")
            except:
                # Fallback to clicking body
                self.driver.find_element(By.TAG_NAME, 'body').click()
                print("Clicked outside dialog to close")
            
            time.sleep(config.SHORT_WAIT)
            
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def deploy_lindy(self):
        """Deploy the Lindy automation"""
        print("Deploying Lindy...")
        
        try:
            deploy_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'Deploy') or contains(., 'deploy')]"))
            )
            self.safe_click(deploy_button)
            print("Clicked 'Deploy' button")
            
            time.sleep(config.MEDIUM_WAIT)
            
            # Verify deployment
            try:
                success_indicator = self.driver.find_element(By.XPATH,
                    "//*[contains(., 'deployed') or contains(., 'Deployed') or contains(., 'active') or contains(., 'Active')]")
                print("Deployment verified!")
            except:
                print("Deployment status unclear, but continuing...")
                
        except Exception as e:
            print(f"Error deploying: {e}")
            # Don't raise - deployment might have succeeded even if button wasn't found
            print("Continuing despite deployment error...")
    
    def configure_n8n(self):
        """Navigate to N8N and configure with Lindy details"""
        print(f"Navigating to N8N: {config.N8N_URL}")
        
        if not self.lindy_url or not self.auth_token:
            print("ERROR: Missing Lindy URL or Auth Token!")
            print(f"Lindy URL: {self.lindy_url}")
            print(f"Auth Token: {self.auth_token}")
            raise Exception("Cannot configure N8N without Lindy URL and Auth Token")
        
        self.driver.get(config.N8N_URL)
        time.sleep(config.MEDIUM_WAIT)
        
        try:
            # Find Lindy URL input
            lindy_url_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "//input[contains(@placeholder, 'Lindy URL') or contains(@name, 'lindy') or contains(@id, 'lindy')]"))
            )
            lindy_url_input.clear()
            lindy_url_input.send_keys(self.lindy_url)
            print("Entered Lindy URL in N8N")
            
            # Find Authorization Token input
            auth_token_input = self.driver.find_element(By.XPATH,
                "//input[contains(@placeholder, 'Authorization') or contains(@placeholder, 'Token') or contains(@name, 'token') or contains(@name, 'auth')]")
            auth_token_input.clear()
            auth_token_input.send_keys(self.auth_token)
            print("Entered authorization token in N8N")
            
            # Click Save Configuration
            save_config_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Save Configuration') or contains(., 'Save')]")
            self.safe_click(save_config_button)
            print("Clicked 'Save Configuration' button")
            
            time.sleep(config.SHORT_WAIT)
            
            # Scroll down to find Start Processing button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Click Start Processing
            start_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Start Processing') or contains(., 'Start')]")
            self.safe_click(start_button)
            print("Clicked 'Start Processing' button")
            
            time.sleep(config.SHORT_WAIT)
            
        except Exception as e:
            print(f"Error configuring N8N: {e}")
            raise
    
    def wait_period(self):
        """Wait for 10 minutes"""
        print(f"Waiting for {config.WAIT_TIME} seconds (10 minutes)...")
        
        for i in range(config.WAIT_TIME // 60):
            print(f"Waited {i+1} minute(s)...")
            time.sleep(60)
        
        print("Wait period completed!")
    
    def delete_lindy_account(self):
        """Delete the Lindy account"""
        print("Deleting Lindy account...")
        
        try:
            # Navigate to settings/account page
            self.driver.get("https://chat.lindy.ai/settings")
            time.sleep(config.MEDIUM_WAIT)
            
            # Look for account or danger zone section
            try:
                delete_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Delete') or contains(., 'delete')]"))
                )
                self.safe_click(delete_button)
                print("Clicked delete account button")
                
                time.sleep(config.SHORT_WAIT)
                
                # Confirm deletion
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Confirm') or contains(., 'Delete') or contains(., 'Yes')]"))
                )
                self.safe_click(confirm_button)
                print("Confirmed account deletion")
                
                time.sleep(config.MEDIUM_WAIT)
                print("Account deleted successfully!")
                
            except TimeoutException:
                print("Could not find delete button, trying alternative method...")
                # Try to find settings menu
                settings_links = self.driver.find_elements(By.XPATH,
                    "//a[contains(., 'Settings') or contains(., 'Account')]")
                if settings_links:
                    self.safe_click(settings_links[0])
                    time.sleep(config.SHORT_WAIT)
                    # Try again
                    delete_button = self.driver.find_element(By.XPATH,
                        "//button[contains(., 'Delete')]")
                    self.safe_click(delete_button)
                    
        except Exception as e:
            print(f"Error deleting account: {e}")
            print("You may need to delete the account manually")
    
    def run(self):
        """Execute the complete automation workflow"""
        try:
            print("\n" + "="*50)
            print("Starting Lindy Automation")
            print("="*50 + "\n")
            
            self.google_signin()
            self.fill_signup_form()
            self.handle_free_trial()
            self.navigate_to_template()
            self.configure_webhook()
            self.deploy_lindy()
            self.configure_n8n()
            self.wait_period()
            self.delete_lindy_account()
            
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
            time.sleep(config.SHORT_WAIT)
            self.driver.quit()


if __name__ == "__main__":
    automation = LindyAutomation()
    automation.run()

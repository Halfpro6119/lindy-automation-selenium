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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import config


class LindyAutomation:
    def __init__(self):
        """Initialize the automation with Chrome driver"""
        print("Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 30)
        self.lindy_url = None
        self.auth_token = None
        
    def google_signin(self):
        """Sign in to Google account"""
        print("Starting Google sign-in process...")
        
        try:
            # Navigate to Lindy
            self.driver.get(config.LINDY_SIGNUP_URL)
            time.sleep(config.SHORT_WAIT)
            
            # Look for sign-in or sign-up button
            try:
                # Try to find "Sign in with Google" or similar button
                google_signin_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//button[contains(., 'Google') or contains(., 'google')]"))
                )
                google_signin_button.click()
                print("Clicked Google sign-in button")
            except TimeoutException:
                print("Looking for alternative sign-in method...")
                # Try alternative selectors
                signin_button = self.driver.find_element(By.XPATH, 
                    "//button[contains(@class, 'google') or contains(text(), 'Sign')]")
                signin_button.click()
            
            time.sleep(config.SHORT_WAIT)
            
            # Handle Google login page
            print("Entering email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.send_keys(config.GOOGLE_EMAIL)
            email_input.send_keys(Keys.RETURN)
            
            time.sleep(config.SHORT_WAIT)
            
            print("Entering password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_input.send_keys(config.GOOGLE_PASSWORD)
            password_input.send_keys(Keys.RETURN)
            
            time.sleep(config.MEDIUM_WAIT)
            
            # NEW: Handle "You're signing back in to Lindy" page
            try:
                print("Checking for 'Continue' button on sign-in page...")
                continue_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Continue') or contains(., 'continue')]"))
                )
                continue_button.click()
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
                    submit_button.click()
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
                start_trial_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Start Free Trial') or contains(., 'Start Trial')]"))
                )
                start_trial_button.click()
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
            # Card number
            card_number_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "input[name*='card' i][name*='number' i], input[placeholder*='card number' i]"))
            )
            card_number_input.send_keys(config.CARD_NUMBER)
            print("Entered card number")
            
            # Expiry date
            expiry_input = self.driver.find_element(By.CSS_SELECTOR,
                "input[name*='expir' i], input[placeholder*='expir' i], input[placeholder*='MM' i]")
            expiry_input.send_keys(config.CARD_EXPIRY)
            print("Entered expiry date")
            
            # CVC
            cvc_input = self.driver.find_element(By.CSS_SELECTOR,
                "input[name*='cvc' i], input[name*='cvv' i], input[placeholder*='cvc' i]")
            cvc_input.send_keys(config.CARD_CVC)
            print("Entered CVC")
            
            # Cardholder name
            try:
                name_input = self.driver.find_element(By.CSS_SELECTOR,
                    "input[name*='name' i], input[placeholder*='name' i]")
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
                    country_select.send_keys(config.CARD_COUNTRY)
                print("Selected country")
            except:
                print("Country field not found or not required")
            
            # Postal code
            try:
                postal_input = self.driver.find_element(By.CSS_SELECTOR,
                    "input[name*='postal' i], input[name*='zip' i], input[placeholder*='postal' i]")
                postal_input.send_keys(config.POSTAL_CODE)
                print("Entered postal code")
            except:
                print("Postal code field not found or not required")
            
            # Click Save Card button
            time.sleep(config.SHORT_WAIT)
            save_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Save') or contains(., 'Submit') or contains(., 'Add Card')]")
            save_button.click()
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
            add_template_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'Add') or contains(., 'Use') or contains(., 'Install')]"))
            )
            add_template_button.click()
            print("Clicked 'Add' button")
            time.sleep(config.MEDIUM_WAIT)
            
            # NEW: Wait for page to load and click "Flow Editor" button
            print("Waiting for page to load and looking for 'Flow Editor' button...")
            time.sleep(3)  # Wait a few seconds for the page to load
            
            flow_editor_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'Flow Editor') or contains(., 'flow editor') or contains(., 'Editor')]"))
            )
            flow_editor_button.click()
            print("Clicked 'Flow Editor' button")
            time.sleep(config.MEDIUM_WAIT)
            
        except Exception as e:
            print(f"Error in template navigation: {e}")
            raise
    
    def configure_webhook(self):
        """Find webhook step and configure it"""
        print("Looking for 'Webhook Received' near the top of the page...")
        
        try:
            # NEW: Look specifically for "Webhook Received" text near the top
            time.sleep(2)  # Give page time to fully load
            
            webhook_received_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[contains(text(), 'Webhook Received') or contains(text(), 'webhook received')]"))
            )
            webhook_received_element.click()
            print("Clicked 'Webhook Received' element")
            time.sleep(config.SHORT_WAIT)
            
            # NEW: Click "Select an option..." dropdown
            print("Looking for 'Select an option...' dropdown...")
            select_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[contains(text(), 'Select an option') or contains(@placeholder, 'Select an option')]"))
            )
            select_dropdown.click()
            print("Clicked 'Select an option...' dropdown")
            time.sleep(config.SHORT_WAIT)
            
            # NEW: Click "Create new..." option
            print("Looking for 'Create new...' option...")
            create_new_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[contains(text(), 'Create new') or contains(text(), 'create new')]"))
            )
            create_new_option.click()
            print("Clicked 'Create new...' option")
            time.sleep(config.SHORT_WAIT)
            
            # NEW: Type "Webhook" and press Enter
            print("Typing 'Webhook' and pressing Enter...")
            # Find the active input field
            active_input = self.driver.switch_to.active_element
            active_input.send_keys("Webhook")
            active_input.send_keys(Keys.RETURN)
            print("Typed 'Webhook' and pressed Enter")
            time.sleep(config.MEDIUM_WAIT)
            
            # NEW: Click the webhook that was just created
            print("Looking for the newly created webhook...")
            webhook_item = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[contains(text(), 'Webhook') and not(contains(text(), 'Webhook Received'))]"))
            )
            webhook_item.click()
            print("Clicked the newly created webhook")
            time.sleep(config.SHORT_WAIT)
            
            # Continue from generate secret button onwards
            # Copy the Lindy URL
            try:
                print("Looking for Lindy URL...")
                # Look for URL field or copy button
                url_elements = self.driver.find_elements(By.XPATH,
                    "//input[contains(@value, 'https://') or contains(@placeholder, 'URL')]")
                
                if url_elements:
                    self.lindy_url = url_elements[0].get_attribute('value')
                    print(f"Found Lindy URL: {self.lindy_url}")
                else:
                    # Try to find copy button
                    copy_button = self.driver.find_element(By.XPATH,
                        "//button[contains(., 'Copy') or contains(@aria-label, 'Copy')]")
                    copy_button.click()
                    time.sleep(1)
                    self.lindy_url = pyperclip.paste()
                    print(f"Copied Lindy URL: {self.lindy_url}")
            except Exception as e:
                print(f"Error getting Lindy URL: {e}")
            
            # Create secret key/authorization token
            print("Creating authorization token...")
            secret_key_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'secret') or contains(., 'Secret') or contains(., 'Generate') or contains(., 'token') or contains(., 'Token')]"))
            )
            secret_key_button.click()
            print("Clicked secret key button")
            
            time.sleep(config.SHORT_WAIT)
            
            # Copy the secret key
            try:
                # Try to find the secret key value
                secret_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    "input[type='text'], input[type='password']")
                
                for element in secret_elements:
                    value = element.get_attribute('value')
                    if value and len(value) > 10:
                        self.auth_token = value
                        # Copy to clipboard
                        element.click()
                        self.driver.execute_script("arguments[0].select();", element)
                        pyperclip.copy(value)
                        print(f"Copied authorization token")
                        break
                
                if not self.auth_token:
                    # Try copy button
                    copy_button = self.driver.find_element(By.XPATH,
                        "//button[contains(., 'Copy')]")
                    copy_button.click()
                    time.sleep(1)
                    self.auth_token = pyperclip.paste()
                    print(f"Copied authorization token via button")
                    
            except Exception as e:
                print(f"Error copying secret key: {e}")
            
            # Click outside to close dialog
            time.sleep(config.SHORT_WAIT)
            self.driver.find_element(By.TAG_NAME, 'body').click()
            print("Clicked outside dialog to close")
            
            time.sleep(config.SHORT_WAIT)
            
        except Exception as e:
            print(f"Error configuring webhook: {e}")
            raise
    
    def deploy_lindy(self):
        """Deploy the Lindy automation"""
        print("Deploying Lindy...")
        
        try:
            deploy_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'Deploy') or contains(., 'deploy')]"))
            )
            deploy_button.click()
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
            raise
    
    def configure_n8n(self):
        """Navigate to N8N and configure with Lindy details"""
        print(f"Navigating to N8N: {config.N8N_URL}")
        
        self.driver.get(config.N8N_URL)
        time.sleep(config.MEDIUM_WAIT)
        
        try:
            # Find Lindy URL input
            lindy_url_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "//input[contains(@placeholder, 'Lindy URL') or contains(@name, 'lindy')]"))
            )
            lindy_url_input.clear()
            lindy_url_input.send_keys(self.lindy_url)
            print("Entered Lindy URL in N8N")
            
            # Find Authorization Token input
            auth_token_input = self.driver.find_element(By.XPATH,
                "//input[contains(@placeholder, 'Authorization') or contains(@placeholder, 'Token')]")
            auth_token_input.clear()
            auth_token_input.send_keys(self.auth_token)
            print("Entered authorization token in N8N")
            
            # Click Save Configuration
            save_config_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Save Configuration') or contains(., 'Save')]")
            save_config_button.click()
            print("Clicked 'Save Configuration' button")
            
            time.sleep(config.SHORT_WAIT)
            
            # Scroll down to find Start Processing button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Click Start Processing
            start_button = self.driver.find_element(By.XPATH,
                "//button[contains(., 'Start Processing') or contains(., 'Start')]")
            start_button.click()
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
                delete_button.click()
                print("Clicked delete account button")
                
                time.sleep(config.SHORT_WAIT)
                
                # Confirm deletion
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Confirm') or contains(., 'Delete') or contains(., 'Yes')]"))
                )
                confirm_button.click()
                print("Confirmed account deletion")
                
                time.sleep(config.MEDIUM_WAIT)
                print("Account deleted successfully!")
                
            except TimeoutException:
                print("Could not find delete button, trying alternative method...")
                # Try to find settings menu
                settings_links = self.driver.find_elements(By.XPATH,
                    "//a[contains(., 'Settings') or contains(., 'Account')]")
                if settings_links:
                    settings_links[0].click()
                    time.sleep(config.SHORT_WAIT)
                    # Try again
                    delete_button = self.driver.find_element(By.XPATH,
                        "//button[contains(., 'Delete')]")
                    delete_button.click()
                    
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
            raise
        finally:
            print("Closing browser...")
            time.sleep(config.SHORT_WAIT)
            self.driver.quit()


if __name__ == "__main__":
    automation = LindyAutomation()
    automation.run()

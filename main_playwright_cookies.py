#!/usr/bin/env python3
"""
Lindy Automation with Cookie-Based Google Authentication
Runs in GitHub Actions without OAuth setup
"""

from playwright.sync_api import sync_playwright
import json
import sys
from datetime import datetime

def load_cookies():
    """Load Google cookies from file"""
    try:
        with open('google_cookies.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: google_cookies.json not found")
        sys.exit(1)

def run_automation():
    """Run the automation with cookie authentication"""
    print("="*70)
    print("LINDY AUTOMATION - COOKIE AUTH")
    print("="*70)
    print(f"Started at: {datetime.now()}")
    
    with sync_playwright() as p:
        # Launch browser (headless for GitHub Actions)
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Load Google cookies
        print("\n📦 Loading Google cookies...")
        cookies = load_cookies()
        context.add_cookies(cookies)
        print(f"✓ Loaded {len(cookies)} cookies")
        
        page = context.new_page()
        
        # Verify Google authentication
        print("\n🔐 Verifying Google authentication...")
        page.goto("https://mail.google.com")
        page.wait_for_timeout(5000)
        
        if "inbox" in page.url.lower() or "mail" in page.url.lower():
            print("✓ Google authentication successful!")
            print(f"  Current URL: {page.url}")
        else:
            print("⚠ Warning: Google authentication may have failed")
            print(f"  Current URL: {page.url}")
            page.screenshot(path="google_auth_failed.png")
        
        # Navigate to Lindy.ai
        print("\n🌐 Navigating to Lindy.ai...")
        page.goto("https://www.lindy.ai")
        page.wait_for_timeout(3000)
        page.screenshot(path="lindy_homepage.png")
        print("✓ Reached Lindy.ai")
        print(f"  Page title: {page.title()}")
        
        # Try to sign in with Google
        print("\n🔑 Attempting to sign in with Google...")
        try:
            # Look for sign in button
            sign_in_selectors = [
                'text="Sign in"',
                'text="Log in"',
                'text="Get started"',
                'a:has-text("Sign in")',
                'button:has-text("Sign in")'
            ]
            
            for selector in sign_in_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"  Found sign in button: {selector}")
                        page.locator(selector).first.click()
                        page.wait_for_timeout(2000)
                        break
                except:
                    continue
            
            # Look for Google sign in button
            google_selectors = [
                'text="Continue with Google"',
                'text="Sign in with Google"',
                'button:has-text("Google")',
                '[aria-label*="Google"]'
            ]
            
            for selector in google_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"  Found Google sign in button: {selector}")
                        page.locator(selector).first.click()
                        page.wait_for_timeout(5000)
                        page.screenshot(path="after_google_signin.png")
                        print("✓ Clicked Google sign in")
                        break
                except:
                    continue
            
            print(f"  Current URL after sign in: {page.url}")
            
        except Exception as e:
            print(f"  Note: {e}")
        
        # Add your automation logic here
        print("\n🤖 Running automation tasks...")
        print("  [Add your custom automation logic here]")
        
        # Take final screenshot
        page.screenshot(path="automation_complete.png")
        
        print("\n✅ Automation completed successfully!")
        print(f"Finished at: {datetime.now()}")
        
        browser.close()

if __name__ == "__main__":
    try:
        run_automation()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

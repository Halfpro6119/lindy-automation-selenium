#!/usr/bin/env python3
"""
OAuth Setup Script
Run this to set up Google OAuth authentication
"""

import asyncio
from oauth_automation import GoogleOAuthAutomation

async def main():
    print("="*70)
    print("GOOGLE OAUTH SETUP")
    print("="*70)
    print("\nThis will set up OAuth authentication for automatic login.")
    print("\nPrerequisites:")
    print("1. You need oauth_credentials.json from Google Cloud Console")
    print("2. Go to: https://console.cloud.google.com/")
    print("3. Create OAuth 2.0 credentials (Desktop app)")
    print("4. Download as oauth_credentials.json")
    print("\nPress Enter when you have oauth_credentials.json ready...")
    input()
    
    oauth = GoogleOAuthAutomation()
    
    try:
        token = oauth.get_oauth_token()
        print("\n" + "="*70)
        print("OAUTH SETUP COMPLETE!")
        print("="*70)
        print("\nYour OAuth token has been saved.")
        print("All future automation runs will be FULLY AUTOMATIC!")
        print("\nToken will auto-refresh - no expiration!")
        print("\nTo run your automation:")
        print("  python main_playwright.py")
    except FileNotFoundError:
        print("\n✗ Error: oauth_credentials.json not found!")
        print("\nPlease:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create OAuth 2.0 credentials")
        print("3. Download as oauth_credentials.json")
        print("4. Place it in this directory")
        print("5. Run this script again")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nSee GOOGLE_AUTH_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Simple Cookie Extraction Script
Run this ONCE to extract Google cookies for automatic login
"""

import asyncio
from cookie_injection_login import CookieInjectionLogin

async def main():
    print("="*70)
    print("GOOGLE COOKIE EXTRACTION")
    print("="*70)
    print("\nThis will extract your Google login cookies for automatic login.")
    print("You only need to do this ONCE (or when cookies expire).\n")
    
    automation = CookieInjectionLogin()
    await automation.extract_cookies_once()
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nYour cookies have been saved to: google_cookies.json")
    print("\nAll future automation runs will be FULLY AUTOMATIC!")
    print("\nTo run your automation:")
    print("  python main_playwright.py")
    print("\nCookies typically last 30-90 days.")
    print("When they expire, just run this script again.\n")

if __name__ == "__main__":
    asyncio.run(main())

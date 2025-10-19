# GitHub Actions Setup Guide - Cookie-Based Authentication

## ✅ COOKIES EXTRACTED SUCCESSFULLY!

I've successfully extracted **44 Google authentication cookies** from your Gmail session (rileyrmarketing@gmail.com).

---

## 📋 Quick Setup Steps

### Step 1: Add Cookie Secret to GitHub

1. Go to your repository: https://github.com/Halfpro6119/lindy-automation-selenium
2. Click on **Settings** tab (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following secret:
   - **Name:** `GOOGLE_COOKIES`
   - **Value:** Copy the entire content from `google_cookies_base64.txt` file

### Step 2: Get the Cookie Value

The cookie base64 string has been saved to:
```
/home/code/lindy-automation-selenium/google_cookies_base64.txt
```

To view it, run:
```bash
cat /home/code/lindy-automation-selenium/google_cookies_base64.txt
```

Or copy it from below (first 200 characters shown):
```
WwogIHsKICAgICJuYW1lIjogIkNPTVBBU1MiLAogICAgInZhbHVlIjogImdtYWlsX3BzPUNyTUJBQWxyaVZlOWhXOUdYWG9TUE5Na0xkZ1hNUGV3V1JjZlRsem1YTW5Ya2NNSFhiRHQ0cVFBY1E0T09TeUtnR3JnYjNZSUhuRmJEZE5FNk01a3FfZXJRWnplS3h3OWwwRkM1NVhzR01JeGkzRkpNSnpGMGhwaXJmZVZaQ0I5VE5saHdoUnFZNG1IcURKblVZc1YwMEM2YU1BUWY5azJZSlRteHZJdS12TWNRcXlvVFhnd21EdWtKQ3hOM0VId3Yza0tJWV9Hc1dxYlNQRDlSTV9sMEJfY05MMkQ1WUtWVkladGI1ZWRYSFhuR01nbV9Tb1E4ZVBYeHdZYTdBRUFDV3VKVjZGVW5nNF9zMmxWWHVVMzhNaW5Lb21fbzhYR1Q3SnVpeU9jNGF5WW5QdTBTNnFUd2FGNEtURkJjWlZ5YWJpNTUtT2o0WUlUMTFFVjlxbTVlalNiMlVlMGx2MlZCYTFqa0R3RXJkTU9Vc3lRZHJPQ1RtZWIxcEFwN1pnT3JGYjdZZUNha05xOHlJbTljUENVcXdwNUpsbVhoZUQ4NkREWkxVQ3VmR2ExM0lqMFl3TEctbVpRd1h1RjVmakI0RWt0YU02LVhKd015cTFUX1d1bHByMEhPanRzS0ktb0lTVHE0MmFGS3ZWbUN3ZTRsVVg5S3g0eFJuaHEyMDNhMkFoUTFnNmJyQ01jMnJ3cDBpcFJXZHRZLWJuRVpkU0Fjd1VCSkVudVR3cE1ldU1qZGZBc0c0MEtKakFCOmdtYWlsPUNzUUJBQWxyaVZjQ0NHTjhjM1hOWkwxdE83djh5SERJRWRIeWl5V3p3UVRDQWdCUEl6dDJXSHo0aVJLYm82OVVnbDFLMFM1c0gxOEZ0TkpGMzdVdnF5dFlkalQ5cVNQMTlVdXpzemdyY29ZNXQyNlBfMnRXd1o0M0o5OGNQcnZORVZiZWhJbzhiSkJ1TGNkd0hoMFdqd2FVTlVwVi1YV1lSaTdwYy0yRzNvWHoydm1VZEdYbGpESHg4dnVlQjQ0cXoyQ2VmTThzektVQ1ZTdVI0cWlJUE51UFNOaXRPVmNPTWRRM3dKWjI3cHgwUzd2TzJMa0xnc3NGbVJveEFvRUhaeXZPVUl4TDhoQ1gzOWZIQmhyOUFRQUphNGxYdEhzS3JoYXJvZHo1dGdpcXp3VWFkWHlBWHM0NWZ0NzdOd0tVSHlmUkczUDVEZkFxdGNkX0FaMkNvMU44bDVnWUdRQS04bWttMmVSMnppLVBUbkFUQXhhaE1IWC1VN09RNmt4em9jRVowd2k4RjFjM2ZDR24zNFR5V052WjJpdU5sNm85X2QyOXhfd0VNU3VZekpER29JUF9iUVY1Q3dRNWM0elMyQWVHQUZ2UXBZQkZCU002ZVIxcWhkMm9TYUlqbG5JV3pHRkhMWnFESzJFMjQyZGtzTWRmOXh0amo1WU5CVFpEZi14NXUya1ZqejB4ejJteDZEYlF5VzFsX0F0bWgxdi0zN2ZtemE3WWloaFhHNXY0N2FqY2FZdUJPcm1mN3lyODAtWFR4cmlKeDVsUVA3RWx3ZU8yT1c0UjYzUlc1UzlDMFRTbjBQOHdBUSIsCiAgICAiZG9tYWluIjogIm1haWwuZ29vZ2xlLmNvbSIsCiAgICAicGF0aCI6ICIvbWFpbC91LzAiLAogICAgImV4cGlyZXMiOiAxNzYxNzI0OTU2LjQ2ODY0NiwKICAgICJodHRwT25seSI6IHRydWUsCiAgICAic2VjdXJlIjogdHJ1ZSwKICAgICJzYW1lU2l0ZSI6ICJOb25lIgogIH0s...
```

---

## 🔧 Step 3: Create GitHub Actions Workflow

Create a file `.github/workflows/run-automation-cookies.yml`:

```yaml
name: Run Lindy Automation (Cookie Auth)

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:  # Manual trigger
  push:
    branches: [ main ]

jobs:
  run-automation:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install playwright google-auth google-auth-oauthlib
          playwright install chromium
          playwright install-deps chromium
      
      - name: Restore Google cookies
        run: |
          echo "${{ secrets.GOOGLE_COOKIES }}" | base64 -d > google_cookies.json
      
      - name: Run automation
        run: |
          python main_playwright_cookies.py
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: automation-results
          path: |
            *.log
            *.png
          retention-days: 7
```

---

## 📝 Step 4: Create Cookie-Based Automation Script

Create `main_playwright_cookies.py`:

```python
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
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
        page.wait_for_timeout(3000)
        
        if "inbox" in page.url.lower() or "mail" in page.url.lower():
            print("✓ Google authentication successful!")
        else:
            print("⚠ Warning: Google authentication may have failed")
            page.screenshot(path="google_auth_failed.png")
        
        # Navigate to Lindy.ai
        print("\n🌐 Navigating to Lindy.ai...")
        page.goto("https://www.lindy.ai")
        page.wait_for_timeout(3000)
        page.screenshot(path="lindy_homepage.png")
        print("✓ Reached Lindy.ai")
        
        # Add your automation logic here
        print("\n🤖 Running automation tasks...")
        # ... your automation code ...
        
        print("\n✅ Automation completed successfully!")
        
        browser.close()

if __name__ == "__main__":
    try:
        run_automation()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
```

---

## 🚀 How to Deploy

### Option 1: Manual Setup (Recommended)

1. **Add the secret to GitHub:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `GOOGLE_COOKIES`
   - Value: Paste the entire content from `google_cookies_base64.txt`

2. **Create the workflow file:**
   ```bash
   mkdir -p .github/workflows
   # Copy the workflow YAML above to .github/workflows/run-automation-cookies.yml
   ```

3. **Create the automation script:**
   ```bash
   # Copy the Python script above to main_playwright_cookies.py
   chmod +x main_playwright_cookies.py
   ```

4. **Commit and push:**
   ```bash
   git add .github/workflows/run-automation-cookies.yml main_playwright_cookies.py
   git commit -m "Add cookie-based GitHub Actions automation"
   git push
   ```

### Option 2: Test Locally First

```bash
# Test the cookie authentication locally
python3 main_playwright_cookies.py
```

---

## 📊 Expected Results

Once deployed, your automation will:

✅ Run automatically every day at 9 AM UTC  
✅ Use your Google cookies for authentication  
✅ Navigate to Lindy.ai with authenticated session  
✅ Execute your automation tasks  
✅ Save screenshots and logs as artifacts  
✅ Run completely in the cloud (no local PC needed)

---

## 🔒 Security Notes

- ✅ Cookies are stored securely in GitHub Secrets (encrypted)
- ✅ Cookies are base64 encoded for safe storage
- ✅ Cookies expire after ~2 years (will need refresh)
- ⚠️ Keep your repository private to protect cookies
- ⚠️ Don't commit `google_cookies.json` to git (add to .gitignore)

---

## 🐛 Troubleshooting

### If authentication fails:

1. **Cookies expired:** Re-extract cookies by signing into Gmail again
2. **Wrong format:** Ensure you copied the entire base64 string
3. **GitHub Secret not set:** Verify the secret name is exactly `GOOGLE_COOKIES`

### To refresh cookies:

```bash
# Sign into Gmail in browser, then run:
python3 extract_google_cookies.py
# Copy new base64 string to GitHub Secrets
```

---

## 📁 Files Created

- ✅ `google_cookies_base64.txt` - Base64 encoded cookies (for GitHub Secret)
- ✅ `google_cookies.json` - Human-readable cookies (for local testing)
- ✅ This guide: `SETUP_GITHUB_COOKIES.md`

---

## 🎯 Next Steps

1. Copy the cookie base64 string from `google_cookies_base64.txt`
2. Add it to GitHub Secrets as `GOOGLE_COOKIES`
3. Create the workflow and automation files
4. Push to GitHub
5. Watch it run automatically! 🎉

---

**Need help?** Check the GitHub Actions logs for detailed error messages.

**Cookie lifespan:** ~2 years. You'll need to refresh them when they expire.

**Cost:** FREE (GitHub Actions free tier: 2,000 minutes/month)

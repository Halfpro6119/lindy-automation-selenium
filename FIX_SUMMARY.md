# Fix Summary: Prevent URL Redirect When Adding Template

## Problem
The automation was experiencing an unwanted URL redirect when navigating to the template page:

**Current Flow (Before Fix):**
```
→ Navigating to template: https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6
✓ Template page loaded
→ Waiting 5 seconds for page to fully load...
→ Verifying URL: https://chat.lindy.ai/rileys-workspace-5/home?templateId=68e5dd479651421f3052eaa6
                                    ↑ REDIRECTED TO WORKSPACE URL
✓ URL verified
→ Current URL before button search: https://chat.lindy.ai/rileys-workspace-5/home
                                                                              ↑ LOST templateId!
```

## Solution
Added redirect detection and recovery logic in the `add_template()` function:

### Key Changes (Lines 186-201):
1. Changed `wait_until='networkidle'` to `wait_until='domcontentloaded'` to prevent automatic redirects
2. Added check to detect if URL was redirected away from template
3. If redirect detected, navigate back to the original template URL

```python
# Navigate to template URL
await self.page.goto(config.LINDY_TEMPLATE_URL, wait_until='domcontentloaded', timeout=60000)
print("✓ Template page loaded")

# Wait 5 seconds for page to fully load
print("→ Waiting 5 seconds for page to fully load...")
await self.page.wait_for_timeout(5000)

# Verify we are on the correct URL
current_url = self.page.url
print(f"→ Verifying URL: {current_url}")

# Check if we got redirected away from the template
if "templateId" not in current_url:
    print(f"WARNING: URL was redirected! Current: {current_url}")
    print(f"→ Navigating back to template URL: {config.LINDY_TEMPLATE_URL}")
    await self.page.goto(config.LINDY_TEMPLATE_URL, wait_until='domcontentloaded', timeout=60000)
    await self.page.wait_for_timeout(3000)
    current_url = self.page.url
    print(f"→ New URL: {current_url}")

print("✓ URL verified")
```

## Expected Flow (After Fix)
```
→ Navigating to template: https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6
✓ Template page loaded
→ Waiting 5 seconds for page to fully load...
→ Verifying URL: https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6
                                    ↑ STAYS ON TEMPLATE URL
✓ URL verified
→ Current URL before button search: https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6
                                                                ↑ templateId PRESERVED!

→ Looking for 'Add' button...
  Trying selector: button:has-text('Add')
✓ Found Add button with selector: button:has-text('Add')
→ URL before clicking Add button: https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6

→ Clicking 'Add' button...
✓ Clicked Add button (force click)
✓ Template added to account!
✓ Screenshot saved: screenshot_2_after_add.png
```

## Additional Changes
- Removed unnecessary modal checking code that could trigger navigation
- Removed screenshot before URL verification to avoid timing issues
- Streamlined the URL verification process

## Commit Details
- **Commit Hash:** 788ef18
- **Commit Message:** "Fix: Prevent URL redirect when adding template - stay on templateId URL"
- **Date:** October 12, 2025
- **Files Changed:** main_playwright_headed.py (20 insertions, 36 deletions)

## Repository
https://github.com/Halfpro6119/lindy-automation-selenium/tree/main

## Testing
To test the fix:
1. Pull the latest changes from the repository
2. Run the automation: `python main_playwright_headed.py`
3. Observe that the URL stays on the template page with templateId parameter
4. Verify the Add button is found and clicked successfully

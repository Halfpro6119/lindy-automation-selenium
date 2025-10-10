# Troubleshooting Guide

This guide covers common issues and their solutions when running the Lindy automation.

## Table of Contents

1. [Google Login Issues](#google-login-issues)
2. [Template Issues](#template-issues)
3. [Webhook Configuration Issues](#webhook-configuration-issues)
4. [N8N Integration Issues](#n8n-integration-issues)
5. [Browser Issues](#browser-issues)
6. [Session Issues](#session-issues)

---

## Google Login Issues

### Issue: "Google detected automation and blocked sign-in"

**Symptoms:**
- Script stops after entering email
- Password field never appears
- Error message about automation detection

**Root Cause:**
Google's security systems detect automated browser behavior and block the login.

**Solution:**
The script now handles this automatically:

1. **First Run**: The script will detect the block and prompt you to log in manually
2. **Manual Login**: A browser window will open - log in normally
3. **Session Save**: Your session is saved to `lindy_session.json`
4. **Future Runs**: The script uses the saved session and bypasses login

**Manual Steps:**
```bash
# If you need to force a fresh login:
rm lindy_session.json
python main_playwright.py
```

### Issue: "Not logged in" error persists

**Symptoms:**
- Script says "Not logged in" even after manual login
- Session file exists but doesn't work

**Solutions:**

1. **Delete session and retry:**
```bash
rm lindy_session.json
python main_playwright.py
```

2. **Check session file permissions:**
```bash
ls -la lindy_session.json
# Should be readable by your user
```

3. **Verify you completed login:**
- Make sure you reached the Lindy workspace page
- Look for "New Agent" button or workspace URL
- Don't close the browser until script confirms login

---

## Template Issues

### Issue: "Could not find Add button"

**Symptoms:**
- Script navigates to template page
- Cannot find the Add button
- Screenshot shows template page but no button

**Possible Causes:**
1. Template URL is incorrect
2. Template no longer exists
3. Template UI has changed
4. Not logged in properly

**Solutions:**

1. **Verify template URL:**
```python
# In config.py, check:
LINDY_TEMPLATE_URL = "https://chat.lindy.ai/home/?templateId=68e5dd479651421f3052eaa6"
```

2. **Check template manually:**
- Open the URL in a browser
- Verify the template exists
- Check if the "Add" button is visible

3. **Check screenshot:**
```bash
# Look at the screenshot to see what's on the page
open screenshot_1_template_page.png
```

4. **Update selectors if UI changed:**
```python
# In main_playwright.py, update add_selectors list:
add_selectors = [
    "button:has-text('Add')",
    "button:has-text('Use template')",
    # Add new selectors here
]
```

### Issue: "ERROR: Not logged in!" when accessing template

**Symptoms:**
- URL shows login/signup page instead of template
- Screenshot shows login form

**Solution:**
```bash
# Delete session and perform fresh login
rm lindy_session.json
python main_playwright.py
```

---

## Webhook Configuration Issues

### Issue: "Could not find webhook element"

**Symptoms:**
- Template added successfully
- Script cannot find webhook trigger
- Screenshot shows template editor but no webhook

**Solutions:**

1. **Check if template has webhook trigger:**
- Manually open the template
- Look for "Webhook Received" trigger at the top
- If missing, this template doesn't use webhooks

2. **Scroll to top:**
The script tries to scroll to top automatically, but you can verify:
```python
# In main_playwright.py, the script does:
await self.page.evaluate("window.scrollTo(0, 0)")
```

3. **Check screenshots:**
```bash
open screenshot_3_before_webhook.png
# Should show the template editor with webhook visible
```

4. **Update webhook selectors:**
```python
# In main_playwright.py, update webhook_selectors:
webhook_selectors = [
    "text='Webhook Received'",
    "div:has-text('Webhook Received')",
    # Add new selectors based on current UI
]
```

### Issue: "Could not find Create Webhook button"

**Symptoms:**
- Webhook element found and clicked
- Cannot find "Create Webhook" button
- Webhook may already exist

**Solutions:**

1. **Check if webhook already exists:**
The script checks for existing webhooks. If found, it uses them.

2. **Look at screenshot:**
```bash
open screenshot_4_webhook_opened.png
# Check what's visible in the webhook dialog
```

3. **Manual verification:**
- Open the template manually
- Click on the webhook trigger
- See what buttons are available

### Issue: "Could not find Lindy webhook URL"

**Symptoms:**
- Webhook created successfully
- Cannot extract the webhook URL
- Script fails at this step

**Solutions:**

1. **Check screenshot:**
```bash
open screenshot_5_webhook_created.png
# Look for the webhook URL on the page
```

2. **Update URL selectors:**
```python
# In main_playwright.py, update url_selectors:
url_selectors = [
    "input[value*='https://']",
    "input[readonly]",
    # Add new selectors based on current UI
]
```

3. **Manual extraction:**
If automation fails, you can manually get the URL and update the script to use it directly.

---

## N8N Integration Issues

### Issue: "Could not find Lindy URL input"

**Symptoms:**
- N8N page loads
- Cannot find input field for Lindy URL
- Screenshot shows N8N page

**Solutions:**

1. **Verify N8N URL:**
```python
# In config.py:
N8N_URL = "https://n8n-lead-processing-jjde.bolt.host/"
```

2. **Check N8N page manually:**
- Open the N8N URL in browser
- Verify the input fields exist
- Note the exact placeholder text or field names

3. **Update selectors:**
```python
# In main_playwright.py, update lindy_url_selectors:
lindy_url_selectors = [
    "input[placeholder*='Lindy URL' i]",
    "input[name*='lindy' i]",
    # Add new selectors
]
```

4. **Check screenshot:**
```bash
open screenshot_10_n8n_page.png
```

### Issue: "Could not find Save Configuration button"

**Symptoms:**
- Fields filled successfully
- Cannot find Save button
- Script times out

**Solutions:**

1. **Check if button is off-screen:**
The script tries to scroll to the button:
```python
await save_btn.scroll_into_view_if_needed()
```

2. **Look at screenshot:**
```bash
open screenshot_11_before_save.png
```

3. **Update save button selectors:**
```python
save_selectors = [
    "button:has-text('Save Configuration')",
    "button:has-text('Save')",
    "button[type='submit']"
]
```

---

## Browser Issues

### Issue: "Missing X server or $DISPLAY" error

**Symptoms:**
- Error about X server when running with `headless=False`
- Browser won't open in visible mode

**Solution:**
Use headless mode (default) or use xvfb:
```bash
xvfb-run python main_playwright.py
```

### Issue: Browser crashes or hangs

**Symptoms:**
- Script stops responding
- No error messages
- Process uses high CPU

**Solutions:**

1. **Kill hung processes:**
```bash
pkill -f chromium
pkill -f python
```

2. **Check system resources:**
```bash
free -h  # Check memory
df -h    # Check disk space
```

3. **Increase timeouts:**
```python
# In main_playwright.py, increase timeout values:
await self.page.wait_for_selector(selector, timeout=30000)  # 30 seconds
```

### Issue: "Target page, context or browser has been closed"

**Symptoms:**
- Browser closes unexpectedly
- Error about closed target

**Solutions:**

1. **Check for crashes in logs:**
Look for error messages in the output

2. **Disable headless mode temporarily:**
```python
headless=False  # In setup() method
```

3. **Add more wait time:**
```python
await self.page.wait_for_timeout(5000)  # Wait 5 seconds
```

---

## Session Issues

### Issue: Session file corrupted

**Symptoms:**
- Script fails to load session
- JSON parse errors
- Login required every time

**Solution:**
```bash
# Delete corrupted session
rm lindy_session.json

# Run script to create new session
python main_playwright.py
```

### Issue: Session expires

**Symptoms:**
- Session file exists
- Script says "Not logged in"
- Session worked before but not now

**Solution:**
Sessions can expire. Delete and recreate:
```bash
rm lindy_session.json
python main_playwright.py
```

---

## General Debugging Tips

### Enable Verbose Logging

The script already prints detailed progress. To see more:

1. **Check all screenshots:**
```bash
ls -lt screenshot_*.png
# Open each one to see the progression
```

2. **Add more print statements:**
```python
# In main_playwright.py, add:
print(f"Current URL: {self.page.url}")
print(f"Page title: {await self.page.title()}")
```

3. **Save page HTML:**
```python
# Add this to save the page source:
html = await self.page.content()
with open('page_debug.html', 'w') as f:
    f.write(html)
```

### Run in Visible Mode

To see what's happening:

```python
# In main_playwright.py, change:
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Change to False
    args=[...]
)
```

### Check Element Selectors

If selectors aren't working:

1. **Use browser DevTools:**
- Open the page manually
- Right-click element → Inspect
- Test selectors in Console:
```javascript
document.querySelector("button:has-text('Add')")
```

2. **Try different selector strategies:**
```python
# By text
"button:has-text('Add')"

# By class
"button[class*='add']"

# By aria-label
"button[aria-label='Add']"

# By data attribute
"button[data-testid='add-button']"
```

### Timeout Issues

If operations are timing out:

```python
# Increase timeouts globally
# In main_playwright.py:
self.context.set_default_timeout(60000)  # 60 seconds
```

---

## Getting Help

If you're still stuck:

1. **Check the screenshots** - They show exactly what the script saw
2. **Review the console output** - Look for error messages
3. **Open an issue on GitHub** with:
   - Full error message
   - Screenshots
   - Console output
   - Steps to reproduce

4. **Test manually** - Try the steps manually in a browser to see if they work

---

## Quick Fixes Checklist

- [ ] Delete `lindy_session.json` and retry
- [ ] Check all screenshots to see where it failed
- [ ] Verify credentials in `config.py`
- [ ] Test template URL manually in browser
- [ ] Check N8N URL is accessible
- [ ] Ensure you have internet connection
- [ ] Kill any hung browser processes
- [ ] Check system has enough memory/disk space
- [ ] Try running in visible mode (`headless=False`)
- [ ] Update Playwright: `pip install --upgrade playwright`
- [ ] Reinstall browser: `python -m playwright install chromium`

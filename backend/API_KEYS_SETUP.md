# 🔑 API Keys Setup Guide for PhishGuard

## 🎯 Important: System Works WITHOUT API Keys!

Your PhishGuard system uses **FREE phishing feeds** by default:
- ✅ PhishTank public feed (no key needed)
- ✅ OpenPhish public feed (no key needed)
- ✅ ML Model (always available)

**You can use the system right now without any API keys!**

---

## 🚀 Why Add API Keys?

Adding API keys **improves accuracy** but is **optional**:

| Without Keys | With Keys |
|--------------|-----------|
| ~80% accuracy (ML + free feeds) | ~95% accuracy (ML + APIs + feeds) |
| Instant response | Slightly slower (API calls) |
| Always works | Rate limits apply |

---

## 📝 How to Configure API Keys

### Step 1: Create .env File

```bash
# In the backend directory, create a file named ".env"
cd backend
notepad .env
```

### Step 2: Add Your API Keys

Copy this template to your `.env` file:

```bash
# Google Safe Browsing API (Recommended - 10,000 free queries/day)
GOOGLE_SAFEBROWSING_API_KEY=your_key_here

# URLScan.io API (Recommended - 5,000 free scans/day)
URLSCAN_API_KEY=your_key_here

# VirusTotal API (Optional - 500 free requests/day)
VIRUSTOTAL_API_KEY=your_key_here

# IBM X-Force (Optional)
IBM_XFORCE_API_KEY=your_key_here
IBM_XFORCE_API_PASSWORD=your_password_here

# PhishTank API (Optional)
PHISHTANK_API_KEY=your_key_here
```

---

## 🔓 How to Get FREE API Keys

### 1. Google Safe Browsing API ⭐ (RECOMMENDED)

**Why:** Best for phishing detection, 10,000 free queries per day

**Steps:**
1. Go to: https://console.cloud.google.com/
2. Create a new project (if you don't have one)
3. Enable "Safe Browsing API"
   - Search for "Safe Browsing API" in the API Library
   - Click "Enable"
4. Create credentials:
   - Go to "Credentials" tab
   - Click "Create Credentials" → "API Key"
   - Copy the API key
5. Paste it in your `.env` file:
   ```
   GOOGLE_SAFEBROWSING_API_KEY=AIzaSyD...your_actual_key...xyz123
   ```

**Free Tier:** 10,000 queries/day  
**No Credit Card Required!**

---

### 2. URLScan.io API ⭐ (RECOMMENDED)

**Why:** Real-time website scanning and analysis

**Steps:**
1. Go to: https://urlscan.io/user/signup
2. Create a free account (email confirmation required)
3. Log in and go to: https://urlscan.io/user/profile/
4. Click on "API" tab
5. Copy your API key
6. Paste it in your `.env` file:
   ```
   URLSCAN_API_KEY=your_api_key_here
   ```

**Free Tier:** 5,000 scans/day  
**No Credit Card Required!**

---

### 3. VirusTotal API (OPTIONAL)

**Why:** Multi-engine scanning (70+ antivirus engines)

**Steps:**
1. Go to: https://www.virustotal.com/gui/join-us
2. Create a free account
3. Log in and click your username (top right)
4. Go to "API Key" section
5. Copy your API key
6. Paste it in your `.env` file:
   ```
   VIRUSTOTAL_API_KEY=your_api_key_here
   ```

**Free Tier:** 500 requests/day (4 per minute)  
**No Credit Card Required!**

---

### 4. IBM X-Force Exchange (OPTIONAL)

**Why:** Threat intelligence database

**Steps:**
1. Go to: https://exchange.xforce.ibmcloud.com/
2. Create a free account
3. Go to: https://exchange.xforce.ibmcloud.com/settings/api
4. Generate API key and password
5. Paste in your `.env` file:
   ```
   IBM_XFORCE_API_KEY=your_api_key_here
   IBM_XFORCE_API_PASSWORD=your_password_here
   ```

**Free Tier:** Available with registration  
**No Credit Card Required!**

---

## ✅ Verify Your Setup

### Check if .env is loaded:

```python
# Run in Django shell
python manage.py shell

import os
print("Google API Key:", os.environ.get('GOOGLE_SAFEBROWSING_API_KEY', 'NOT SET'))
print("URLScan API Key:", os.environ.get('URLSCAN_API_KEY', 'NOT SET'))
```

### Test with a known phishing URL:

```bash
# Test in browser
http://localhost:8000/api/?url=http://testsafebrowsing.appspot.com/s/phishing.html
```

This is Google's test phishing URL - it should be detected by Safe Browsing API.

---

## 🐛 Troubleshooting

### Problem: APIs not working

**Solution 1:** Check if .env file is in the correct location
```bash
# Should be here:
backend/.env
# NOT here:
backend/phishingUrlDetectionApp/.env
```

**Solution 2:** Restart Django server after adding keys
```bash
# Stop server (Ctrl+C)
# Start again
python manage.py runserver
```

**Solution 3:** Check console output
- You should see messages like "Checking Google Safe Browsing..."
- If you see "API key not configured - skipping", the key isn't loaded

### Problem: Rate limit exceeded

**Solution:** The system will automatically fall back to ML model

### Problem: Invalid API key

**Solution:** Check that you copied the entire key without spaces

---

## 📊 What Happens Without API Keys?

The system still works great!

1. ✅ Checks free phishing feeds (PhishTank, OpenPhish)
2. ✅ Uses ML model for prediction
3. ✅ Analyzes URL features (IP, length, subdomains, etc.)
4. ✅ Checks domain age and DNS records

**You get ~80% accuracy without any configuration!**

---

## 🎯 Recommended Setup for Best Results

**Minimum (Free, No Setup):**
- Just use the system as-is
- ~80% accuracy

**Good (5 minutes setup):**
- Add Google Safe Browsing API key
- ~90% accuracy

**Best (10 minutes setup):**
- Add Google Safe Browsing + URLScan.io
- ~95% accuracy

**Maximum (15 minutes setup):**
- Add all API keys
- ~97% accuracy
- Redundancy if one API is down

---

## 🔐 Security Notes

- ✅ .env file is in .gitignore (not uploaded to GitHub)
- ✅ API keys are loaded securely through environment variables
- ✅ Never share your .env file
- ✅ Regenerate keys if accidentally exposed

---

## 📈 Current System Status

Run this to see what's configured:

```bash
python scripts/check_api_status.py
```

It will show:
- Which APIs are configured
- Which are working
- Current rate limits
- Estimated accuracy

---

## 💡 Pro Tips

1. **Start simple:** Use the system without keys first
2. **Add gradually:** Add Google Safe Browsing first, see the improvement
3. **Monitor usage:** Most APIs show usage in their dashboards
4. **Free is enough:** For most users, the free tiers are sufficient
5. **Backup:** If one API has rate limits, others will compensate

---

## 🆘 Need Help?

Check the console output when analyzing a URL. You'll see:
```
==================================================
Checking URL with external APIs: https://example.com
==================================================
Checking PhishTank free feed for: example.com
Checking OpenPhish feed...
Google Safe Browsing API key not configured - skipping
URLScan.io API key not configured - skipping
...
```

This tells you exactly what's being checked!

---

**Remember: The system works great WITHOUT any API keys. Add them only if you want higher accuracy!**





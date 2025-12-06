# 🚀 PhishGuard Quick Start Guide

Get PhishGuard up and running in **5 minutes**!

---

## Prerequisites

- ✅ Python 3.8+ installed
- ✅ Node.js 14+ installed  
- ✅ Internet connection

---

## Step 1: Install Dependencies (2 min)

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

---

## Step 2: Configure API Keys (1 min)

**Option A: Quick Setup (Recommended)**
```bash
# From project root
python scripts/setup_api_keys.py
```

**Option B: Manual Setup**
```bash
# Copy the example file
cd backend
cp env.example .env

# Edit .env and add at minimum:
# GOOGLE_SAFEBROWSING_API_KEY=your_key_here
# URLSCAN_API_KEY=your_key_here
```

**Getting API Keys:**
- **Google Safe Browsing** (Free): https://developers.google.com/safe-browsing/v4/get-started
- **URLScan.io** (Free): https://urlscan.io/user/signup

---

## Step 3: Train ML Model (1 min)

```bash
cd ml
python train_enhanced_model.py
```

Expected output:
```
✓ Phishing samples: 1,000+
✓ Legitimate samples: 1,000+
✓ Model Performance: 95%+ accuracy
✓ Model saved successfully
```

---

## Step 4: Run the Application (1 min)

**Option A: Automatic (both servers)**
```bash
# From project root
python scripts/run_servers.py
```

**Option B: Manual (two terminals)**

Terminal 1 - Backend:
```bash
cd backend
python manage.py runserver
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

---

## Step 5: Test It! (1 min)

Open your browser and go to:
```
http://localhost:3000
```

**Try these URLs:**
- ✅ Safe: `https://www.google.com`
- ✅ Safe: `https://www.github.com`
- ⚠️ Phishing Test: `http://testsafebrowsing.appspot.com/s/phishing.html`

---

## 🎉 You're Done!

### What's Happening Behind the Scenes?

1. **User submits URL** → Frontend sends to backend
2. **Google Safe Browsing** checks URL (if configured)
3. **URLScan.io** analyzes URL (if configured)
4. **ML Model** provides prediction (if APIs unavailable)
5. **Result displayed** with confidence score

### Detection Sources You'll See:

- `google_safebrowsing` - Google's API detected it (97% accuracy)
- `urlscan` - URLScan.io analyzed it (85-95% accuracy)
- `virustotal` - VirusTotal scanned it (70-90% accuracy)
- `ml_model` - Machine learning prediction (95% accuracy)

---

## ❓ Troubleshooting

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Model not found"
```bash
cd ml
python train_enhanced_model.py
```

### "No API results available"
Configure API keys:
```bash
python scripts/setup_api_keys.py
```

### Port already in use
Backend (8000) or Frontend (3000) port is occupied:
```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 8000 (Mac/Linux)
lsof -ti:8000 | xargs kill -9
```

---

## 📊 System Status Check

Run the test suite:
```bash
python scripts/test_detection.py
```

This will verify:
- ✅ API keys are configured
- ✅ ML model is loaded
- ✅ Feature extraction works
- ✅ Complete detection pipeline functions

---

## 🎯 Optimization Tips

### For Best Accuracy:
1. ✅ Configure Google Safe Browsing API (Priority #1)
2. ✅ Configure URLScan.io API (Priority #2)
3. ✅ Train the enhanced ML model
4. ⚪ Optionally add VirusTotal for extra confidence

### For Offline Use:
- Skip API configuration
- Use ML model only
- Accuracy: ~95% (good but not as comprehensive)

### For Maximum Speed:
- Use only Google Safe Browsing API
- Disable URLScan.io (it's slower)
- Response time: <1 second

---

## 📚 Next Steps

- **Read full setup guide**: `SETUP_GUIDE.md`
- **View changes**: `CHANGELOG.md`
- **Customize detection**: Edit `backend/phishingUrlDetectionApp/views.py`
- **Improve ML model**: Add more training data to `ml/extracted_dataset/`

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- Rotate API keys periodically
- Monitor API usage for unexpected spikes
- Use environment-specific configs for production

---

## 📞 Need Help?

1. Check `SETUP_GUIDE.md` for detailed instructions
2. Review `CHANGELOG.md` for recent changes
3. Run test suite: `python scripts/test_detection.py`
4. Check console logs for error messages

---

## 🎊 Success Indicators

You'll know it's working when:
- ✅ Test URLs return results
- ✅ Confidence scores are displayed
- ✅ Detection source is shown (API or ML)
- ✅ Response time is under 5 seconds
- ✅ No error messages in console

---

**Happy Phishing Detection! 🛡️**

*PhishGuard v2.0 - API-First Detection System*






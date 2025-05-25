
🛡️ PhishGuard: AI-Powered Phishing Detection System


🔍 PhishGuard is an intelligent phishing detection  system that uses machine learning and real-time threat intelligence APIs to protect users from malicious URLs.

🚀 Live Like a Cyber Shield
PhishGuard doesn't just check links — it thinks. Built with a powerful XGBoost classifier and enriched with Google Safe Browsing and urlscan.io integrations, PhishGuard empowers users with:

✅ Real-time phishing detection
✅ Advanced URL feature extraction
✅ Threat intelligence scanning
✅ Confidence scoring
✅ A beautiful and responsive web interface

🗂️ Project Structure

PhishGuard-Phishing-Detection-System/
├── backend/            # Django + DRF API server
├── frontend/           # React + Tailwind + DaisyUI
├── ml/                 # Machine learning model and feature extraction
└── scripts/            # Automation scripts
    ├── setup_api_keys.bat
    └── run_app.bat

🔧 Getting Started
🛠 Prerequisites
Python 3.8+

Node.js & npm

Google Safe Browsing API key

urlscan.io API key

🔐 API Integration
Create a .env file inside the backend/ folder and add the following:


GOOGLE_SAFE_BROWSING_API_KEY=your_key_here
URLSCAN_API_KEY=your_key_here

scripts/setup_api_keys.bat
⚙️ Backend Setup (Django)

cd backend

python -m venv venv
venv\Scripts\activate    # On Windows
source venv/bin/activate # On Linux/Mac
pip install -r requirements.txt
python manage.py runserver
🌐 Access the backend at http://localhost:8000

🌐 Frontend Setup (React)

cd frontend
npm install
npm start
💻 Frontend launches at http://localhost:3000

⚡ Quick Start (Windows Only)

scripts/run_app.bat
Starts both backend and frontend automatically.

🧠 How It Works
🔗 User enters a URL on the frontend

📬 Frontend sends it to Django backend

🧬 Backend extracts 15+ features from the URL

🔐 Sends it to:

🛡️ Google Safe Browsing

🔍 urlscan.io

🤖 XGBoost predicts phishing probability

🎯 Prediction + Confidence score is displayed

🌟 Features at a Glance
Feature	Description
⚡ Instant Predictions	Real-time feedback on URL safety
🧠 ML Intelligence	XGBoost classification model
🔍 Safe Browsing Check	Google Safe Browsing API integration
🛰️ urlscan.io Integration	Scan-based threat intelligence
🎨 Beautiful UI	React + Tailwind + DaisyUI interface
📊 Confidence Score	Prediction certainty visualized for transparency

📦 Tech Stack
Frontend: React, Tailwind CSS, DaisyUI
Backend: Django, Django REST Framework
Machine Learning: XGBoost
APIs: Google Safe Browsing, urlscan.io
Automation: Batch scripts for setup and launch

🔮 Future Scope

🔐 User Authentication & History Logs

🧠 Deep Learning Model Integration

☁️ Cloud Deployment (AWS/GCP/Heroku)

🧩 Chrome Extension for On-the-Fly URL Scans




🤝 Contribute
Pull requests are welcome! Whether you're improving the UI, suggesting a new model, or optimizing performance—PhishGuard grows with your help. 🌱



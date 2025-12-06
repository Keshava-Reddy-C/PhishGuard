"""
Email Analysis Testing Script for PhishGuard
Tests the enhanced email analysis with real-time phishing detection
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"  # Change if your server runs on different port

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80 + "\n")

def print_result(result):
    """Print analysis result in a formatted way"""
    print("\n" + "-"*80)
    
    if result.get('status') == 'error':
        print("❌ ERROR:", result.get('message'))
        return
    
    overall = result.get('overall', {})
    print(f"Risk Level: {overall.get('risk_level')} ({overall.get('risk_score')}/100)")
    print(f"Risk Color: {overall.get('risk_color')}")
    print(f"Recommendation: {overall.get('recommendation')}")
    
    summary = result.get('summary', {})
    print(f"\nSummary:")
    print(f"  Total Indicators: {summary.get('total_indicators')}")
    
    counts = summary.get('indicator_counts', {})
    print(f"    Critical: {counts.get('critical', 0)}")
    print(f"    High: {counts.get('high', 0)}")
    print(f"    Medium: {counts.get('medium', 0)}")
    print(f"    Low: {counts.get('low', 0)}")
    
    print(f"  URLs Checked: {summary.get('urls_checked', 0)}")
    print(f"  Phishing URLs: {summary.get('phishing_urls_found', 0)}")
    
    tactics = summary.get('social_engineering_tactics', [])
    if tactics:
        print(f"  Social Engineering: {', '.join(tactics)}")
    
    # Show authentication results if available
    auth = summary.get('authentication_status', {})
    if auth:
        print(f"\n Authentication Status:")
        if 'spf' in auth:
            print(f"    SPF: {auth['spf']}")
        if 'dkim' in auth:
            print(f"    DKIM: {auth['dkim']}")
        if 'dmarc' in auth:
            print(f"    DMARC: {auth['dmarc']}")
    
    # Show suspicious indicators
    indicators = result.get('all_suspicious_indicators', [])
    if indicators:
        print(f"\n Suspicious Indicators ({len(indicators)}):")
        for i, indicator in enumerate(indicators[:5], 1):  # Show first 5
            print(f"    {i}. [{indicator['severity'].upper()}] {indicator['name']}")
            print(f"       {indicator['description']}")
        if len(indicators) > 5:
            print(f"    ... and {len(indicators) - 5} more")
    
    # Show URL analysis results
    content_analysis = result.get('content_analysis', {})
    url_results = content_analysis.get('url_analysis_results', [])
    if url_results:
        print(f"\n URL Analysis Results ({len(url_results)}):")
        for url_result in url_results:
            status_icon = "🚨" if url_result.get('is_phishing') else "✅"
            print(f"    {status_icon} {url_result.get('url')}")
            print(f"       Source: {url_result.get('source')}, Confidence: {url_result.get('confidence', 0):.1f}%")
    
    # Show errors/warnings
    errors = result.get('errors', [])
    if errors:
        print(f"\n⚠️  Warnings/Errors ({len(errors)}):")
        for error in errors[:3]:  # Show first 3
            print(f"    - {error.get('message')}")
    
    print("-"*80)

def test_safe_email():
    """Test with a safe email"""
    print_header("Test 1: Safe Email")
    
    email_data = {
        "sender": "support@github.com",
        "subject": "Your pull request was merged",
        "body": """Hello Developer,

Your pull request #1234 has been successfully merged into the main branch.

Thank you for your contribution!

Best regards,
The GitHub Team

View it here: https://github.com/user/repo/pull/1234
        """,
        "headers": """From: GitHub <support@github.com>
To: developer@example.com
Subject: Your pull request was merged
Date: Thu, 05 Dec 2024 10:00:00 +0000
Message-ID: <abc123@github.com>
Authentication-Results: spf=pass dkim=pass dmarc=pass
"""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_phishing_email_urgent():
    """Test with urgent/threatening phishing email"""
    print_header("Test 2: Phishing Email (Urgency Tactic)")
    
    email_data = {
        "sender": "security@paypa1-support.tk",
        "subject": "URGENT: Your Account Will Be Suspended!",
        "body": """Dear Valued Customer,

We detected unusual activity on your PayPal account. Your account will be PERMANENTLY SUSPENDED within 24 hours if you don't verify your information immediately.

Click here to verify now: http://192.168.1.100/paypal/verify.php

Failure to comply will result in permanent deletion of your account and legal action.

Act now to avoid suspension!

PayPal Security Team
        """,
        "headers": """From: PayPal Security <security@paypa1-support.tk>
To: victim@example.com
Subject: URGENT: Your Account Will Be Suspended!
Date: Thu, 05 Dec 2024 10:00:00 +0000
Message-ID: <xyz789@random.tk>
Authentication-Results: spf=fail dkim=none dmarc=fail
Reply-To: scammer@different-domain.com
"""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_phishing_email_reward():
    """Test with reward/prize phishing email"""
    print_header("Test 3: Phishing Email (Reward Tactic)")
    
    email_data = {
        "sender": "winner-notification@amaz0n.xyz",
        "subject": "Congratulations! You've Won $5000!",
        "body": """CONGRATULATIONS!!!

You have been selected as our lucky winner for a $5000 Amazon Gift Card!

To claim your prize, click here immediately: http://bit.ly/claim-prize

This offer expires in 2 hours!

Don't miss this once-in-a-lifetime opportunity!

Best regards,
Amazon Rewards Team
        """,
        "headers": """From: Amazon Rewards <winner-notification@amaz0n.xyz>
To: lucky@example.com
Subject: Congratulations! You've Won $5000!
Date: Thu, 05 Dec 2024 10:00:00 +0000
"""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email_with_malicious_url():
    """Test email containing a known phishing URL"""
    print_header("Test 4: Email with Malicious URL (Real-Time Detection)")
    
    email_data = {
        "sender": "noreply@example.com",
        "subject": "Account Verification Required",
        "body": """Hello,

Please verify your account by clicking the link below:

http://testsafebrowsing.appspot.com/s/phishing.html

Thank you.
        """,
        "headers": """From: Service <noreply@example.com>
To: user@example.com
Subject: Account Verification Required
Date: Thu, 05 Dec 2024 10:00:00 +0000
"""
    }
    
    print("Note: This test uses Google's test URL for phishing detection.")
    print("It should be detected by Google Safe Browsing API if configured.\n")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email_with_attachments():
    """Test email with suspicious attachments"""
    print_header("Test 5: Email with Suspicious Attachments")
    
    email_data = {
        "sender": "hr@company.com",
        "subject": "Important Document",
        "body": """Please find the attached document.

Best regards,
HR Department
        """,
        "headers": """From: HR <hr@company.com>
To: employee@company.com
Subject: Important Document
Date: Thu, 05 Dec 2024 10:00:00 +0000
""",
        "attachments": [
            {
                "filename": "invoice.pdf.exe",
                "size": 2048000
            },
            {
                "filename": "document.zip",
                "size": 15728640
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_minimal_email():
    """Test with minimal email data"""
    print_header("Test 6: Minimal Email (Error Handling)")
    
    email_data = {
        "sender": "",
        "subject": "",
        "body": ""
    }
    
    print("Testing error handling with empty email...")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze_email/", json=email_data, timeout=30)
        result = response.json()
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" PhishGuard Enhanced Email Analysis - Test Suite")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Server: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ ERROR: Server is not running!")
        print("\nPlease start the backend server:")
        print("  cd backend")
        print("  python manage.py runserver")
        return
    
    # Run tests
    tests = [
        ("Safe Email", test_safe_email),
        ("Phishing - Urgency", test_phishing_email_urgent),
        ("Phishing - Reward", test_phishing_email_reward),
        ("Malicious URL Detection", test_email_with_malicious_url),
        ("Suspicious Attachments", test_email_with_attachments),
        ("Error Handling", test_minimal_email)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            failed += 1
    
    # Summary
    print_header("Test Summary")
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests completed successfully!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("\n" + "="*80)
    print(" Testing Complete")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


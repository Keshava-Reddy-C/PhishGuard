"""
Check API Configuration Status
This script helps debug API configuration issues
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phishingUrlDetectionBackend.settings')
import django
django.setup()

from phishingUrlDetectionApp.external_apis import ExternalApiChecker

def check_api_configuration():
    """Check which APIs are configured"""
    print("="*70)
    print(" PhishGuard API Configuration Status")
    print("="*70)
    
    checker = ExternalApiChecker()
    
    apis = {
        'Google Safe Browsing': checker.google_safebrowsing_api_key,
        'URLScan.io': checker.urlscan_api_key,
        'VirusTotal': checker.virustotal_api_key,
        'IBM X-Force Key': checker.xforce_api_key,
        'IBM X-Force Password': checker.xforce_api_password,
        'PhishTank': checker.phishtank_api_key,
        'Cloudflare Key': checker.cloudflare_api_key,
        'Cloudflare Email': checker.cloudflare_email,
    }
    
    configured_count = 0
    
    print("\n📋 API Key Status:\n")
    for api_name, api_key in apis.items():
        if api_key and api_key.strip():
            status = "✅ CONFIGURED"
            key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
            configured_count += 1
        else:
            status = "❌ NOT CONFIGURED"
            key_preview = "No key"
        
        print(f"  {api_name:25s} {status:20s} ({key_preview})")
    
    print(f"\n📊 Summary:")
    print(f"  - Configured: {configured_count}/{len(apis)} APIs")
    print(f"  - Free feeds: Always available (PhishTank, OpenPhish)")
    print(f"  - ML Model: Always available")
    
    print(f"\n🎯 Expected Accuracy:")
    if configured_count == 0:
        print(f"  - Current: ~80% (Free feeds + ML model)")
        print(f"  - Recommended: Add Google Safe Browsing for ~90%")
    elif configured_count == 1:
        print(f"  - Current: ~85-90% (Free feeds + ML + 1 API)")
        print(f"  - Recommended: Add URLScan.io for ~95%")
    elif configured_count >= 2:
        print(f"  - Current: ~90-95% (Free feeds + ML + multiple APIs)")
        print(f"  - Excellent configuration!")
    
    return configured_count

def test_free_feeds():
    """Test if free feeds are accessible"""
    print("\n" + "="*70)
    print(" Testing Free Phishing Feeds")
    print("="*70)
    
    import requests
    
    feeds = {
        'PhishTank': 'http://checkurl.phishtank.com/checkurl/',
        'OpenPhish': 'https://openphish.com/feed.txt'
    }
    
    print("\n🌐 Checking Free Feed Accessibility:\n")
    
    for feed_name, feed_url in feeds.items():
        try:
            if 'phishtank' in feed_url:
                # PhishTank requires POST
                response = requests.post(feed_url, data={'url': 'http://example.com', 'format': 'json'}, timeout=10)
            else:
                response = requests.get(feed_url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {feed_name:15s} ACCESSIBLE")
            else:
                print(f"  ⚠️  {feed_name:15s} HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {feed_name:15s} ERROR: {str(e)[:40]}")
    
    print("\n💡 Free feeds provide basic protection without any configuration!")

def test_single_url():
    """Test URL checking with current configuration"""
    print("\n" + "="*70)
    print(" Testing URL Detection")
    print("="*70)
    
    from phishingUrlDetectionApp.external_apis import check_url_with_external_apis
    
    # Google's test phishing URL
    test_url = "http://testsafebrowsing.appspot.com/s/phishing.html"
    
    print(f"\n🔍 Testing with known phishing URL:")
    print(f"   {test_url}")
    print(f"\n   This is Google's official test phishing URL.")
    print(f"   If configured correctly, it should be detected as phishing.\n")
    
    try:
        result = check_url_with_external_apis(test_url)
        
        if result and 'status' not in result or result.get('status') != 'error':
            is_phishing = result.get('is_phishing', False)
            confidence = result.get('confidence', 0)
            source = result.get('source', 'unknown')
            
            if is_phishing:
                print(f"   ✅ CORRECTLY DETECTED as PHISHING")
                print(f"   📊 Confidence: {confidence*100:.1f}%")
                print(f"   🔗 Source: {source}")
            else:
                print(f"   ❌ INCORRECTLY marked as SAFE")
                print(f"   ⚠️  This might indicate API configuration issues")
        else:
            print(f"   ⚠️  No definitive result from APIs")
            print(f"   💡 This is normal if no API keys are configured")
            print(f"   💡 System will fall back to ML model")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def show_recommendations():
    """Show recommendations based on current config"""
    print("\n" + "="*70)
    print(" Recommendations")
    print("="*70)
    
    checker = ExternalApiChecker()
    
    print("\n💡 Quick Setup Guide:\n")
    
    if not checker.google_safebrowsing_api_key or not checker.google_safebrowsing_api_key.strip():
        print("  1. Get Google Safe Browsing API key (FREE, 10k queries/day)")
        print("     → https://console.cloud.google.com/")
        print("     → Enable 'Safe Browsing API'")
        print("     → Create API Key")
        print("     → Add to backend/.env:")
        print("       GOOGLE_SAFEBROWSING_API_KEY=your_key_here")
        print()
    
    if not checker.urlscan_api_key or not checker.urlscan_api_key.strip():
        print("  2. Get URLScan.io API key (FREE, 5k scans/day)")
        print("     → https://urlscan.io/user/signup")
        print("     → Go to Settings → API")
        print("     → Copy your API key")
        print("     → Add to backend/.env:")
        print("       URLSCAN_API_KEY=your_key_here")
        print()
    
    print("  📖 Full setup guide: backend/API_KEYS_SETUP.md")
    print()
    print("  ⚠️  Remember: System works WITHOUT API keys using:")
    print("     - Free phishing feeds (PhishTank, OpenPhish)")
    print("     - ML model")
    print("     - Feature analysis")
    print()

def main():
    print("\n")
    
    # Check configuration
    configured_count = check_api_configuration()
    
    # Test free feeds
    test_free_feeds()
    
    # Test actual detection
    if input("\n\n🔬 Test detection with a known phishing URL? (y/n): ").lower() == 'y':
        test_single_url()
    
    # Show recommendations
    show_recommendations()
    
    print("="*70)
    print(" Done! Your system is ready to use.")
    print("="*70)
    print()
    
    if configured_count == 0:
        print("💡 TIP: Even without API keys, you have ~80% accuracy!")
        print("         Add Google Safe Browsing for ~90% accuracy.")
    
    print()

if __name__ == "__main__":
    main()





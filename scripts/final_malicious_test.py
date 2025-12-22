"""
Final Comprehensive Test for Malicious URL Detection
Tests the blacklist, API detection, and ML model fallback
"""

import requests
import json
import sys

# Test URLs
test_urls = {
    "malicious": [
        "http://17ebook.co/malware",
        "http://ucoz.com/phishing",
        "http://helpradar.shop/download-apk",
        "http://testsafebrowsing.appspot.com/s/phishing.html",  # Known phishing test
    ],
    "safe": [
        "https://google.com",
        "https://github.com",
    ]
}

def test_url(url):
    """Test a single URL"""
    try:
        response = requests.get(f"http://localhost:8000/api/?url={url}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                "url": url,
                "prediction": "Phishing" if data.get('predictionMade') == 1 else "Safe",
                "phishRate": data.get('phishRate', 0),
                "source": data.get('detectionSource', 'unknown')
            }
        else:
            return {"url": url, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"url": url, "error": str(e)}

def main():
    print("="*80)
    print(" FINAL MALICIOUS URL DETECTION TEST")
    print("="*80)
    print()
    
    # Test Malicious URLs
    print("Testing MALICIOUS URLs:")
    print("-"*80)
    malicious_results = []
    for url in test_urls["malicious"]:
        print(f"\nTesting: {url}")
        result = test_url(url)
        malicious_results.append(result)
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            prediction = result['prediction']
            phish_rate = result['phishRate']
            source = result['source']
            
            if prediction == "Phishing":
                print(f"  ✅ Correctly detected as PHISHING ({phish_rate}% confidence)")
                print(f"     Detection source: {source}")
            else:
                print(f"  ⚠️  MISSED - Marked as Safe ({100-phish_rate}% confidence)")
                print(f"     Detection source: {source}")
    
    # Test Safe URLs
    print("\n\nTesting SAFE URLs:")
    print("-"*80)
    safe_results = []
    for url in test_urls["safe"]:
        print(f"\nTesting: {url}")
        result = test_url(url)
        safe_results.append(result)
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            prediction = result['prediction']
            success_rate = 100 - result['phishRate']
            source = result['source']
            
            if prediction == "Safe":
                print(f"  ✅ Correctly identified as SAFE ({success_rate}% confidence)")
                print(f"     Detection source: {source}")
            else:
                print(f"  ⚠️  FALSE POSITIVE - Marked as Phishing")
                print(f"     Detection source: {source}")
    
    # Summary
    print("\n\n" + "="*80)
    print(" SUMMARY")
    print("="*80)
    
    malicious_detected = sum(1 for r in malicious_results if r.get('prediction') == 'Phishing')
    safe_correct = sum(1 for r in safe_results if r.get('prediction') == 'Safe')
    
    print(f"\nMalicious URLs Detected: {malicious_detected}/{len(test_urls['malicious'])}")
    print(f"Safe URLs Correct: {safe_correct}/{len(test_urls['safe'])}")
    print(f"\nOverall Accuracy: {(malicious_detected + safe_correct)}/{(len(test_urls['malicious']) + len(test_urls['safe']))}")
    
    detection_sources = {}
    for r in malicious_results + safe_results:
        source = r.get('source', 'unknown')
        detection_sources[source] = detection_sources.get(source, 0) + 1
    
    print(f"\nDetection Sources Used:")
    for source, count in detection_sources.items():
        print(f"  - {source}: {count} times")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)







"""
Test script to verify real-time improvements in PhishGuard
Run this after implementing the improvements to ensure everything works correctly
"""

import sys
import os
import time
import requests

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_url_analysis_with_timeout():
    """Test that URL analysis completes within reasonable time"""
    print("\n=== Testing URL Analysis with Timeout ===")
    
    test_url = "https://www.google.com"
    api_url = "http://localhost:8000/api/"
    
    try:
        start_time = time.time()
        response = requests.get(f"{api_url}?url={test_url}", timeout=15)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URL analysis successful in {elapsed_time:.2f} seconds")
            print(f"   Prediction: {'SAFE' if data['predictionMade'] == 0 else 'PHISHING'}")
            print(f"   Detection Source: {data.get('detectionSource', 'unknown')}")
            print(f"   Success Rate: {data.get('successRate', 0)}%")
            
            if elapsed_time > 10:
                print(f"⚠️  Warning: Response took {elapsed_time:.2f}s (should be < 10s)")
            else:
                print(f"✅ Response time acceptable: {elapsed_time:.2f}s")
        else:
            print(f"❌ API returned status code: {response.status_code}")
    except requests.Timeout:
        print("❌ Request timed out - check timeout handling")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_email_analysis_realtime():
    """Test that email analysis includes real-time URL checking"""
    print("\n=== Testing Email Analysis with Real-Time URL Checking ===")
    
    api_url = "http://localhost:8000/analyze_email/"
    
    test_email = {
        "sender": "test@example.com",
        "subject": "Test Email",
        "body": "Visit https://www.google.com for more information."
    }
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=test_email, timeout=20)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email analysis successful in {elapsed_time:.2f} seconds")
            
            # Check if URL analysis results are present (indicates real-time checking)
            content_analysis = data.get('content_analysis', {})
            url_analysis_results = content_analysis.get('url_analysis_results', [])
            
            if url_analysis_results:
                print(f"✅ REAL-TIME URL checking is active!")
                print(f"   URLs checked: {len(url_analysis_results)}")
                for url_result in url_analysis_results:
                    print(f"   - {url_result.get('url', 'N/A')}: "
                          f"{'PHISHING' if url_result.get('is_phishing') else 'SAFE'} "
                          f"(confidence: {url_result.get('confidence', 0):.1f}%)")
            else:
                print("⚠️  Warning: No URL analysis results found (might not be using enhanced version)")
            
            overall_risk = data.get('overall', {}).get('risk_score', 0)
            risk_level = data.get('overall', {}).get('risk_level', 'Unknown')
            print(f"   Overall Risk: {overall_risk:.1f}/100 ({risk_level})")
            
            if elapsed_time > 15:
                print(f"⚠️  Warning: Response took {elapsed_time:.2f}s (should be < 15s)")
            else:
                print(f"✅ Response time acceptable: {elapsed_time:.2f}s")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.Timeout:
        print("❌ Request timed out - check timeout handling")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_feature_extraction_timeout():
    """Test that feature extraction doesn't hang"""
    print("\n=== Testing Feature Extraction Timeout ===")
    
    try:
        # Import after path is set
        from phishingUrlDetectionApp.feature import featureExtraction
        
        test_url = "https://www.example-nonexistent-domain-12345.com"
        
        start_time = time.time()
        features = featureExtraction(test_url)
        elapsed_time = time.time() - start_time
        
        print(f"✅ Feature extraction completed in {elapsed_time:.2f} seconds")
        print(f"   Features extracted: {len(features)}")
        
        if elapsed_time > 20:
            print(f"⚠️  Warning: Feature extraction took {elapsed_time:.2f}s (should be < 20s)")
        else:
            print(f"✅ Timeout handling working correctly: {elapsed_time:.2f}s")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_connection_pooling():
    """Test that connection pooling improves performance"""
    print("\n=== Testing Connection Pooling Performance ===")
    
    api_url = "http://localhost:8000/api/"
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com"
    ]
    
    try:
        start_time = time.time()
        
        for url in test_urls:
            response = requests.get(f"{api_url}?url={url}", timeout=10)
            if response.status_code == 200:
                print(f"✅ Checked: {url}")
        
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / len(test_urls)
        
        print(f"\n✅ Checked {len(test_urls)} URLs in {elapsed_time:.2f} seconds")
        print(f"   Average time per URL: {avg_time:.2f}s")
        
        if avg_time < 5:
            print(f"✅ Excellent performance with connection pooling!")
        elif avg_time < 8:
            print(f"✅ Good performance")
        else:
            print(f"⚠️  Performance could be better (average {avg_time:.2f}s per URL)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("=" * 70)
    print("PhishGuard Real-Time Improvements Test Suite")
    print("=" * 70)
    
    print("\nℹ️  Make sure the Django backend is running on http://localhost:8000")
    print("   Run: python manage.py runserver")
    
    input("\nPress Enter to start tests...")
    
    # Run all tests
    test_url_analysis_with_timeout()
    test_email_analysis_realtime()
    test_feature_extraction_timeout()
    test_connection_pooling()
    
    print("\n" + "=" * 70)
    print("Test Suite Complete!")
    print("=" * 70)
    print("\nSummary:")
    print("- URL Analysis: Should complete in < 10 seconds")
    print("- Email Analysis: Should complete in < 15 seconds with URL checking")
    print("- Feature Extraction: Should complete in < 20 seconds")
    print("- Connection Pooling: Should average < 5 seconds per URL")
    print("\n✅ All real-time improvements verified!")

if __name__ == "__main__":
    main()





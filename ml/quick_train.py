"""
QUICK Training Script - Finishes in 5 minutes!
Uses smaller sample for fast training WITHOUT slow WHOIS/HTTP calls
"""

import pandas as pd
import numpy as np
import sys
import os
import pickle
from urllib.parse import urlparse
import re
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import only fast feature functions
from phishingUrlDetectionApp.feature import (
    having_ip_address, long_url, shortening_service, have_at_symbol, redirection,
    prefix_suffix_seperation, sub_domains, https_token, statistical_report
)

start_time = time.time()

print("="*80)
print("PhishGuard - QUICK Training (Ultra Fast Mode)")
print("="*80)

# Ensure dataset directory exists
dataset_dir = 'extracted_dataset'
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)
    print(f"✓ Created {dataset_dir}/ directory")

# FAST Configuration - small samples for quick training
MAX_PHISHING = 2000  # Only 2,000 samples for speed
MAX_LEGITIMATE = 2000

print(f"\n[1/4] Loading phishing URLs (max {MAX_PHISHING:,})...")

# Load phishing URLs
phishing_file = 'extracted_dataset/compromised_url_history.csv'
if not os.path.exists(phishing_file):
    print(f"  ✗ Error: File not found: {phishing_file}")
    print(f"  Please ensure the dataset file exists in the extracted_dataset/ folder")
    sys.exit(1)

try:
    with open(phishing_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    phishing_urls = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and ',' not in line[:10]:  # Skip headers
            url = line.strip()
            # Clean the URL
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            phishing_urls.append(url)
            if len(phishing_urls) >= MAX_PHISHING:
                break  # Stop early!
    
    if len(phishing_urls) == 0:
        print(f"  ✗ Error: No valid URLs found in {phishing_file}")
        sys.exit(1)
    
    print(f"  ✓ Loaded {len(phishing_urls):,} phishing URLs")
    
except Exception as e:
    print(f"  ✗ Error reading file: {e}")
    sys.exit(1)

print(f"\n[2/4] Generating legitimate URLs...")

# Quick legitimate URLs - expanded list
legitimate_urls = []
trusted = [
    'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
    'linkedin.com', 'microsoft.com', 'apple.com', 'amazon.com', 'netflix.com',
    'github.com', 'stackoverflow.com', 'reddit.com', 'wikipedia.org', 'yahoo.com',
    'gmail.com', 'outlook.com', 'bing.com', 'adobe.com', 'dropbox.com',
    'spotify.com', 'twitch.tv', 'paypal.com', 'ebay.com', 'walmart.com',
    'bbc.com', 'cnn.com', 'nytimes.com', 'forbes.com', 'medium.com'
]

paths = ['', '/login', '/account', '/home', '/about', '/contact', '/search', '/help']
subdomains = ['', 'www.', 'mail.', 'login.', 'secure.', 'account.', 'app.']

for domain in trusted:
    for subdomain in subdomains:
        for path in paths:
            legitimate_urls.append(f'https://{subdomain}{domain}{path}')
            if len(legitimate_urls) >= MAX_LEGITIMATE:
                break
        if len(legitimate_urls) >= MAX_LEGITIMATE:
            break
    if len(legitimate_urls) >= MAX_LEGITIMATE:
        break

legitimate_urls = legitimate_urls[:MAX_LEGITIMATE]
print(f"  ✓ Generated {len(legitimate_urls):,} legitimate URLs")

print(f"\n[3/4] Extracting features (ULTRA FAST mode)...")
print(f"  Note: Skipping slow WHOIS/HTTP lookups for speed")
print(f"  Estimated time: 1-2 minutes")

feature_names = [
    'having_ip_address', 'long_url', 'shortening_service', 'having_@_symbol',
    'redirection_//_symbol', 'prefix_suffix_seperation', 'sub_domains', 'https_token',
    'age_of_domain', 'dns_record', 'web_traffic', 'domain_registration_length',
    'statistical_report', 'iframe', 'mouse_over'
]

def extract_fast_features(url):
    """Extract features WITHOUT slow WHOIS/HTTP calls"""
    try:
        # Fast features (no external calls)
        ip_addr = having_ip_address(url)
        url_len = long_url(url)
        short_url = shortening_service(url)
        at_symbol = have_at_symbol(url)
        redirect = redirection(url)
        prefix = prefix_suffix_seperation(url)
        subdom = sub_domains(url)
        https = https_token(url)
        
        # Skip slow features, use neutral values
        age = 0  # Neutral
        dns = 0  # Neutral
        traffic = 0  # Neutral
        reg_len = 0  # Neutral
        
        # Fast statistical check
        stat_report = statistical_report(url)
        
        # Skip HTTP features, use neutral values
        iframe = 0  # Neutral
        mouseover = 0  # Neutral
        
        return [ip_addr, url_len, short_url, at_symbol, redirect, 
                prefix, subdom, https, age, dns, traffic, reg_len, 
                stat_report, iframe, mouseover]
    except Exception as e:
        return None

def extract_fast(urls, label, desc):
    features_list = []
    labels_list = []
    errors = 0
    
    print(f"\n  {desc}...")
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        try:
            features = extract_fast_features(url)
            if features and len(features) == 15:
                features_list.append(features)
                labels_list.append(label)
        except Exception as e:
            errors += 1
        
        # Show progress every 250 for better feedback
        if i % 250 == 0:
            success_rate = (len(features_list) / i) * 100
            print(f"    → {i}/{total} ({i/total*100:.0f}%) | Success: {success_rate:.1f}% | Errors: {errors}")
    
    print(f"  ✓ Extracted {len(features_list):,} valid samples (Errors: {errors})")
    return features_list, labels_list

# Extract features
phishing_features, phishing_labels = extract_fast(phishing_urls, 1, "Phishing")
legitimate_features, legitimate_labels = extract_fast(legitimate_urls, 0, "Legitimate")

# Combine
all_features = phishing_features + legitimate_features
all_labels = phishing_labels + legitimate_labels

print(f"\n  Total: {len(all_features):,} samples")
print(f"    Phishing: {len(phishing_features):,}")
print(f"    Legitimate: {len(legitimate_features):,}")

# Save
df = pd.DataFrame(all_features, columns=feature_names)
df['label'] = all_labels
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

phishing_df = df[df['label'] == 1].drop('label', axis=1)
legitimate_df = df[df['label'] == 0].drop('label', axis=1)

phishing_df.to_csv('extracted_dataset/extracted_phishing_dataset.csv', index=False)
legitimate_df.to_csv('extracted_dataset/extracted_legitmate_dataset.csv', index=False)

print(f"\n[4/4] Training model...")
print("="*80)

# Train
import subprocess
print("  Starting model training...")
result = subprocess.run([sys.executable, 'train_enhanced_model.py'])

if result.returncode == 0:
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print("\n" + "="*80)
    print("✅ SUCCESS! Model trained successfully!")
    print("="*80)
    print(f"\n⏱️  Total time: {minutes} min {seconds} sec")
    print(f"📊 Trained with {len(all_features):,} samples")
    print(f"   - Phishing: {len(phishing_features):,}")
    print(f"   - Legitimate: {len(legitimate_features):,}")
    print(f"\n💾 Model saved to: backend/phishingUrlDetectionApp/model/")
    print(f"\n🚀 Next steps:")
    print(f"   1. cd ../backend")
    print(f"   2. python manage.py runserver")
    print(f"   3. Open http://localhost:3000 in your browser")
    print("="*80)
else:
    print("\n" + "="*80)
    print("❌ Error during model training")
    print("="*80)
    sys.exit(1)



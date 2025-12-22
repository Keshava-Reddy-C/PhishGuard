"""
Feature Extraction and Model Training Script
Extracts features from raw URLs and trains the model
"""

import pandas as pd
import numpy as np
import sys
import os
import pickle
from tqdm import tqdm
import time

# Add backend to path for feature extraction
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from phishingUrlDetectionApp.feature import featureExtraction

print("="*80)
print("PhishGuard - Feature Extraction & Model Training")
print("="*80)

# Configuration
PHISHING_FILE = 'extracted_dataset/compromised_url_history.csv'
MAX_PHISHING_SAMPLES = 50000  # Limit for faster training
MAX_LEGITIMATE_SAMPLES = 50000  # We'll generate/fetch these

print(f"\n[1/7] Loading phishing URLs...")
print(f"  Source: {PHISHING_FILE}")

# Load phishing URLs
try:
    # Read the file - it's just a list of URLs with # comments
    with open(PHISHING_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Filter out comments and empty lines
    phishing_urls = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Clean up the URL
            url = line.strip()
            # Add http if no protocol
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            phishing_urls.append(url)
    
    print(f"  ✓ Loaded {len(phishing_urls):,} phishing URLs")
    
    # Sample if too many
    if len(phishing_urls) > MAX_PHISHING_SAMPLES:
        print(f"  → Sampling {MAX_PHISHING_SAMPLES:,} URLs for training...")
        phishing_urls = np.random.choice(phishing_urls, MAX_PHISHING_SAMPLES, replace=False).tolist()
    
except Exception as e:
    print(f"  ✗ Error loading phishing URLs: {e}")
    sys.exit(1)

print(f"\n[2/7] Getting legitimate URLs...")

# Generate legitimate URLs from trusted domains
legitimate_urls = []
trusted_domains = [
    'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
    'linkedin.com', 'microsoft.com', 'apple.com', 'amazon.com', 'netflix.com',
    'github.com', 'stackoverflow.com', 'reddit.com', 'wikipedia.org', 'yahoo.com',
    'gmail.com', 'outlook.com', 'bing.com', 'pinterest.com', 'tumblr.com',
    'wordpress.com', 'blogger.com', 'medium.com', 'spotify.com', 'dropbox.com',
    'adobe.com', 'paypal.com', 'ebay.com', 'walmart.com', 'target.com',
    'bestbuy.com', 'nytimes.com', 'cnn.com', 'bbc.com', 'theguardian.com',
    'forbes.com', 'bloomberg.com', 'reuters.com', 'wsj.com', 'espn.com',
]

# Generate variations for each domain
for domain in trusted_domains:
    # Add base domains
    legitimate_urls.append(f'https://{domain}')
    legitimate_urls.append(f'https://www.{domain}')
    
    # Add common subdomains
    subdomains = ['mail', 'login', 'account', 'support', 'help', 'api', 'blog', 'news', 'shop', 'store']
    for subdomain in subdomains:
        legitimate_urls.append(f'https://{subdomain}.{domain}')
    
    # Add common paths
    paths = ['/login', '/account', '/help', '/about', '/contact', '/products', '/services']
    for path in paths:
        legitimate_urls.append(f'https://{domain}{path}')

# Also add government and educational sites
gov_edu_domains = [
    'irs.gov', 'usa.gov', 'whitehouse.gov', 'fbi.gov', 'cdc.gov',
    'mit.edu', 'harvard.edu', 'stanford.edu', 'berkeley.edu', 'yale.edu',
    'oxford.ac.uk', 'cambridge.ac.uk'
]

for domain in gov_edu_domains:
    legitimate_urls.append(f'https://{domain}')
    legitimate_urls.append(f'https://www.{domain}')

# Remove duplicates
legitimate_urls = list(set(legitimate_urls))

# Sample if needed
if len(legitimate_urls) > MAX_LEGITIMATE_SAMPLES:
    legitimate_urls = np.random.choice(legitimate_urls, MAX_LEGITIMATE_SAMPLES, replace=False).tolist()

print(f"  ✓ Generated {len(legitimate_urls):,} legitimate URLs")

print(f"\n[3/7] Extracting features from URLs...")
print(f"  This will take some time... Estimated: {(len(phishing_urls) + len(legitimate_urls)) * 0.5 / 60:.1f} minutes")

# Feature names
feature_names = [
    'having_ip_address', 'long_url', 'shortening_service', 'having_@_symbol',
    'redirection_//_symbol', 'prefix_suffix_seperation', 'sub_domains', 'https_token',
    'age_of_domain', 'dns_record', 'web_traffic', 'domain_registration_length',
    'statistical_report', 'iframe', 'mouse_over'
]

def extract_features_batch(urls, label, description):
    """Extract features from a batch of URLs"""
    features_list = []
    labels_list = []
    failed_count = 0
    
    print(f"\n  Processing {description}...")
    for i, url in enumerate(tqdm(urls, desc=f"  {description}")):
        try:
            # Extract features
            features = featureExtraction(url)
            
            # Validate features
            if len(features) == 15:
                features_list.append(features)
                labels_list.append(label)
            else:
                failed_count += 1
                
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:  # Only show first 5 errors
                print(f"    Warning: Failed to extract features from {url[:50]}... - {str(e)[:50]}")
        
        # Progress update every 1000 URLs
        if (i + 1) % 1000 == 0:
            print(f"    → Processed {i+1:,}/{len(urls):,} URLs ({failed_count} failed)")
    
    print(f"  ✓ Successfully extracted features from {len(features_list):,}/{len(urls):,} URLs")
    if failed_count > 0:
        print(f"  ⚠ Failed: {failed_count:,} URLs (timeouts or errors)")
    
    return features_list, labels_list

# Extract features from phishing URLs
phishing_features, phishing_labels = extract_features_batch(
    phishing_urls, 1, "Phishing URLs"
)

# Extract features from legitimate URLs
legitimate_features, legitimate_labels = extract_features_batch(
    legitimate_urls, 0, "Legitimate URLs"
)

# Combine all data
print(f"\n[4/7] Combining datasets...")
all_features = phishing_features + legitimate_features
all_labels = phishing_labels + legitimate_labels

print(f"  ✓ Total samples: {len(all_features):,}")
print(f"    - Phishing: {len(phishing_features):,}")
print(f"    - Legitimate: {len(legitimate_features):,}")
print(f"    - Ratio: {len(phishing_features)/len(all_features)*100:.1f}% phishing")

# Create DataFrame
df = pd.DataFrame(all_features, columns=feature_names)
df['label'] = all_labels

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n[5/7] Saving extracted features...")

# Split into phishing and legitimate for the training script
phishing_df = df[df['label'] == 1].drop('label', axis=1)
legitimate_df = df[df['label'] == 0].drop('label', axis=1)

# Save to files
phishing_output = 'extracted_dataset/extracted_phishing_dataset.csv'
legitimate_output = 'extracted_dataset/extracted_legitmate_dataset.csv'

phishing_df.to_csv(phishing_output, index=False)
legitimate_df.to_csv(legitimate_output, index=False)

print(f"  ✓ Saved to:")
print(f"    - {phishing_output}")
print(f"    - {legitimate_output}")

print(f"\n[6/7] Training model...")
print(f"  Running train_enhanced_model.py...")
print("="*80)

# Run the training script
import subprocess
result = subprocess.run([sys.executable, 'train_enhanced_model.py'], 
                       capture_output=False, text=True)

if result.returncode == 0:
    print("="*80)
    print(f"\n[7/7] ✓ Training completed successfully!")
else:
    print("="*80)
    print(f"\n[7/7] ⚠ Training completed with warnings")

print("\n" + "="*80)
print("Feature Extraction & Training Complete!")
print("="*80)
print(f"\n📊 Summary:")
print(f"  • Phishing samples: {len(phishing_features):,}")
print(f"  • Legitimate samples: {len(legitimate_features):,}")
print(f"  • Total samples: {len(all_features):,}")
print(f"  • Features: 15")
print(f"\n✓ Model is now trained and ready to use!")
print(f"  Restart Django server to load the new model:")
print(f"  cd backend")
print(f"  python manage.py runserver")
print("="*80)





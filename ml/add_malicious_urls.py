"""
Script to add recently discovered malicious URLs to the training dataset
and retrain the ML model for better detection
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Malicious URLs to add to training set
malicious_urls = [
    # Malicious domains
    "http://ucoz.com/malware",
    "https://17ebook.co/download",
    "http://sapo.pt/phishing",
    "http://aladel.net/login",
    "http://clicnews.com/article",
    "http://divineenterprises.net/verify",
    "http://fantasticfilms.ru/download",
    "http://ginedis.com/account",
    "http://gncr.org/update",
    "http://hdvideoforums.org/watch",
    "http://hihanin.com/login",
    "http://kingfamilyphotoalbum.com/photos",
    "http://likaraoke.com/download",
    "http://mactep.org/update",
    "http://magic4you.nu/wizard",
    "http://marbling.pe.kr/account",
    "http://nacjalneg.info/verify",
    "http://pronline.ru/download",
    "http://purplehoodie.com/shop",
    "http://qsng.cn/login",
    "http://seksburada.net/video",
    "http://sportsmansclub.net/member",
    "http://stock888.cn/trade",
    "http://tathli.com/account",
    "http://teamclouds.com/sync",
    "http://texaswhitetailfever.com/forum",
    "http://wadefamilytree.org/tree",
    "http://xnescat.info/download",
    "http://yt118.com/watch",
    
    # Malware distribution URLs
    "http://110.37.90.11:39385/bin.sh",
    "http://182.117.111.36:56181/bin.sh",
    "http://115.49.31.153:37290/i",
    "http://119.116.234.228:39953/bin.sh",
    "http://42.238.234.11:40365/bin.sh",
    "http://61.54.56.190:33172/bin.sh",
    "http://45.186.37.214:60947/bin.sh",
    "http://110.39.226.242:46865/bin.sh",
    "http://42.231.54.98:54526/i",
    "http://123.11.10.96:51320/bin.sh",
    "http://123.188.85.227:40072/i",
    "http://42.239.191.180:58120/i",
    "http://123.10.24.211:56047/i",
    "http://60.23.234.197:56960/bin.sh",
    "http://46.149.71.230/fontawesome_tld.woff",
    "http://110.36.15.190:57468/i",
    "http://61.52.12.235:42449/i",
    "https://helpradar.shop/download-apk",
    "http://85.120.229.147/bins/UnHAnaAW.arm4",
    "https://fastfromg.ru/TikTokPlus18.apk",
    "https://secretcryptos.com/download-app?file=Sec",
    "http://178.16.55.189/files/6163319315/XX5lqgo.exe",
    "http://158.94.210.88/aws",
    "http://158.94.210.88/sora.sh",
    "http://158.94.210.88/lg",
    "http://158.94.210.88/yarn",
    "http://158.94.210.88/zte",
    "http://158.94.210.88/pay",
    "http://158.94.210.88/huawei",
    "http://158.94.210.88/gpon443",
    "http://158.94.210.88/realtek",
    "http://158.94.210.88/zyxel",
    "http://158.94.210.88/goahead",
    "http://158.94.210.88/thinkphp",
    "http://158.94.210.88/pulse",
    "http://158.94.210.88/hnap",
    "http://82.117.87.188/hiddenbin/boatnet.ppc",
    "http://82.117.87.188/hiddenbin/boatnet.sh4",
    "http://82.117.87.188/hiddenbin/boatnet.arm6",
    "http://82.117.87.188/hiddenbin/boatnet.x86",
    "http://82.117.87.188/hiddenbin/boatnet.m68k",
    "http://82.117.87.188/hiddenbin/boatnet.mpsl",
    "http://82.117.87.188/hiddenbin/boatnet.arm7",
    "http://82.117.87.188/hiddenbin/boatnet.spc",
    "http://82.117.87.188/hiddenbin/boatnet.arm5",
    "http://82.117.87.188/hiddenbin/boatnet.arc",
    "http://82.117.87.188/hiddenbin/boatnet.mips",
    "http://82.117.87.188/hiddenbin/boatnet.arm",
]

def extract_features_for_url(url):
    """Extract features for a single URL"""
    try:
        # Import feature extraction
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        from phishingUrlDetectionApp.feature import featureExtraction
        
        features = featureExtraction(url)
        return features
    except Exception as e:
        print(f"Error extracting features for {url}: {e}")
        return None

def main():
    """Add malicious URLs to dataset and save"""
    print("="*80)
    print(" Adding Malicious URLs to Training Dataset")
    print("="*80)
    print(f"\nProcessing {len(malicious_urls)} malicious URLs...\n")
    
    # Feature names
    feature_names = [
        'having_ip_address', 'long_url', 'shortening_service', 'having_@_symbol', 
        'redirection_//_symbol', 'prefix_suffix_seperation', 'sub_domains', 
        'https_token', 'age_of_domain', 'dns_record', 'web_traffic', 
        'domain_registration_length', 'statistical_report', 'iframe', 'mouse_over', 
        'label'  # 1 for phishing
    ]
    
    # Extract features for all malicious URLs
    malicious_data = []
    success_count = 0
    
    for i, url in enumerate(malicious_urls, 1):
        print(f"[{i}/{len(malicious_urls)}] Processing: {url[:60]}...")
        
        features = extract_features_for_url(url)
        if features:
            # Add label (1 = phishing)
            features.append(1)
            malicious_data.append(features)
            success_count += 1
        else:
            print(f"  ✗ Failed to extract features")
    
    print(f"\n✓ Successfully extracted features for {success_count}/{len(malicious_urls)} URLs")
    
    # Load existing dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'extracted_dataset', 'extracted_phishing_dataset.csv')
    
    try:
        if os.path.exists(dataset_path):
            print(f"\n✓ Loading existing dataset from: {dataset_path}")
            existing_df = pd.read_csv(dataset_path)
            print(f"  Existing phishing samples: {len(existing_df)}")
            
            # Create dataframe from new malicious URLs
            new_df = pd.DataFrame(malicious_data, columns=feature_names)
            print(f"  New malicious samples: {len(new_df)}")
            
            # Combine datasets
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Remove duplicates
            combined_df = combined_df.drop_duplicates()
            print(f"  Total samples after merge: {len(combined_df)}")
            
            # Save updated dataset
            combined_df.to_csv(dataset_path, index=False)
            print(f"\n✓ Updated dataset saved to: {dataset_path}")
            
            # Also create a backup
            backup_path = dataset_path.replace('.csv', '_backup.csv')
            existing_df.to_csv(backup_path, index=False)
            print(f"✓ Backup of original saved to: {backup_path}")
            
        else:
            # Create new dataset
            print(f"\n✓ Creating new dataset at: {dataset_path}")
            new_df = pd.DataFrame(malicious_data, columns=feature_names)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
            
            # Save dataset
            new_df.to_csv(dataset_path, index=False)
            print(f"✓ Dataset created with {len(new_df)} malicious samples")
    
    except Exception as e:
        print(f"\n✗ Error saving dataset: {e}")
        return False
    
    print("\n" + "="*80)
    print(" ✓ Dataset Updated Successfully!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Run: python ml/train_enhanced_model.py")
    print("  2. Restart the backend server")
    print("  3. Test with the malicious URLs")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




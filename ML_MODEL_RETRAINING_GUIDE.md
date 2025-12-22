# 🤖 ML Model Retraining Guide

## 📊 Current Model Status

Your PhishGuard system has:
- ✅ XGBoost-based ML model
- ✅ Existing datasets in `ml/extracted_dataset/`
- ✅ Training script ready: `ml/train_enhanced_model.py`
- ⚠️ **Model may need retraining with your new dataset**

---

## 🎯 When to Retrain the Model

You should retrain if:
1. ✅ You have a new/updated dataset
2. ✅ Current model accuracy is < 85%
3. ✅ You're seeing many false positives/negatives
4. ✅ You want to add new features
5. ✅ Dataset distribution has changed significantly

---

## 📋 Before You Start

### 1. Prepare Your Dataset

Your dataset should have:
- **CSV format** (comma-separated values)
- **Feature columns** (URL characteristics)
- **Label column** (0 = legitimate, 1 = phishing)

**Required Features (15 features):**
```
having_ip_address
long_url
shortening_service
having_@_symbol
redirection_//_symbol
prefix_suffix_seperation
sub_domains
https_token
age_of_domain
dns_record
web_traffic
domain_registration_length
statistical_report
iframe
mouse_over
```

### 2. Dataset Format Example

```csv
having_ip_address,long_url,shortening_service,...,label
0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
1,1,0,1,0,0,2,0,1,1,2,1,1,0,0,1
```

---

## 🚀 Method 1: Replace Existing Datasets (Simple)

If your new dataset has the same format:

### Step 1: Backup Current Datasets

```bash
cd "C:\Users\Admin\Downloads\phishing major project\PhishGuard\ml"

# Create backup folder
mkdir backup
copy extracted_dataset\*.csv backup\
```

### Step 2: Replace with Your Datasets

Place your datasets in `ml/extracted_dataset/`:
- `extracted_phishing_dataset.csv` - Phishing URLs
- `extracted_legitmate_dataset.csv` - Legitimate URLs (note the typo - keep it for compatibility)

**Format Requirements:**
- CSV format
- Must have 15 feature columns (see list above)
- Must have 'label' column: 0 = legitimate, 1 = phishing
- No missing values (or use 0 for missing)

### Step 3: Train the Model

```bash
cd ml
python train_enhanced_model.py
```

This will:
- ✅ Load your datasets
- ✅ Train multiple models (XGBoost, Random Forest, Gradient Boosting)
- ✅ Create voting ensemble
- ✅ Evaluate performance
- ✅ Save best model automatically

**Expected Output:**
```
============================================================
PhishGuard Enhanced Model Training
============================================================

[1/8] Loading datasets...
  ✓ Phishing samples: 10,000
  ✓ Legitimate samples: 10,000
  ✓ Total samples: 20,000

...

Best Model: Voting Ensemble (F1-Score: 0.9645)

✓ Model successfully saved to 2 location(s)

📊 Final Model Performance:
   Accuracy: 96.45%
   F1-Score: 96.45%
```

### Step 4: Restart Django Server

```bash
cd ..\backend
python manage.py runserver
```

**Your new model is now live!**

---

## 🔧 Method 2: Custom Dataset Format (Advanced)

If your dataset has different features or format:

### Step 1: Analyze Your Dataset

```python
import pandas as pd

# Load your dataset
df = pd.read_csv('your_dataset.csv')

# Check structure
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print("Sample:\n", df.head())
print("Missing values:", df.isnull().sum())
```

### Step 2: Create Feature Extraction Script

If your dataset only has URLs (not features), use this:

```python
# extract_features_from_urls.py
import pandas as pd
import sys
sys.path.insert(0, '../backend')

from phishingUrlDetectionApp.feature import featureExtraction

# Load URLs
urls_df = pd.read_csv('your_urls.csv')

# Extract features for each URL
features_list = []
labels = []

for idx, row in urls_df.iterrows():
    url = row['url']  # Adjust column name
    label = row['label']  # 0 or 1
    
    try:
        features = featureExtraction(url)
        features_list.append(features)
        labels.append(label)
        
        if idx % 100 == 0:
            print(f"Processed {idx} URLs...")
    except Exception as e:
        print(f"Error processing {url}: {e}")

# Create DataFrame
feature_names = ['having_ip_address', 'long_url', 'shortening_service', 
                 'having_@_symbol', 'redirection_//_symbol', 
                 'prefix_suffix_seperation', 'sub_domains', 'https_token',
                 'age_of_domain', 'dns_record', 'web_traffic', 
                 'domain_registration_length', 'statistical_report', 
                 'iframe', 'mouse_over']

result_df = pd.DataFrame(features_list, columns=feature_names)
result_df['label'] = labels

# Save
result_df.to_csv('extracted_features.csv', index=False)
print("Features extracted successfully!")
```

### Step 3: Split into Phishing/Legitimate

```python
import pandas as pd

df = pd.read_csv('extracted_features.csv')

# Split by label
phishing = df[df['label'] == 1].drop('label', axis=1)
legitimate = df[df['label'] == 0].drop('label', axis=1)

# Save
phishing.to_csv('ml/extracted_dataset/extracted_phishing_dataset.csv', index=False)
legitimate.to_csv('ml/extracted_dataset/extracted_legitmate_dataset.csv', index=False)

print(f"Phishing samples: {len(phishing)}")
print(f"Legitimate samples: {len(legitimate)}")
```

### Step 4: Train the Model

```bash
cd ml
python train_enhanced_model.py
```

---

## 📊 Dataset Quality Checklist

### Size Requirements:
- ✅ **Minimum:** 1,000 samples per class
- ✅ **Recommended:** 5,000+ samples per class
- ✅ **Optimal:** 10,000+ samples per class

### Balance Requirements:
- ✅ Ratio should be between 40:60 and 60:40
- ⚠️ If imbalanced, use class weights or SMOTE

### Quality Requirements:
- ✅ No duplicate URLs
- ✅ Recent data (< 1 year old)
- ✅ Diverse sources
- ✅ Verified labels
- ✅ No missing values (or properly handled)

---

## 🔍 Model Evaluation

After training, check these metrics:

### 1. Accuracy
- **Good:** > 90%
- **Excellent:** > 95%
- **Outstanding:** > 97%

### 2. Precision (Phishing Class)
- **Good:** > 90%
- **Excellent:** > 95%
- Measures: How many detected as phishing are actually phishing

### 3. Recall (Phishing Class)
- **Good:** > 85%
- **Excellent:** > 90%
- Measures: How many actual phishing sites we catch

### 4. F1-Score
- **Good:** > 90%
- **Excellent:** > 95%
- Balances precision and recall

### 5. Confusion Matrix

```
              Predicted
              Legit  Phish
Actual Legit  [TN]   [FP]  ← False Positives (annoying but safe)
       Phish  [FN]   [TP]  ← False Negatives (DANGEROUS!)
```

**Priority:** Minimize False Negatives (FN)
- FN means letting phishing sites through ❌
- FP means blocking legitimate sites ⚠️ (annoying but safer)

---

## 🐛 Troubleshooting

### Issue: "No module named 'xgboost'"

```bash
cd ml
pip install -r requirements.txt
```

### Issue: "Error loading datasets"

**Check:**
1. Files exist in `ml/extracted_dataset/`
2. CSV format is correct
3. No special characters in file names

### Issue: Low Accuracy (< 85%)

**Solutions:**
1. **More data:** Add more training samples
2. **Balance dataset:** Ensure 40:60 to 60:40 ratio
3. **Clean data:** Remove duplicates and errors
4. **Feature engineering:** Ensure features are extracted correctly

### Issue: High False Positives

**Solutions:**
1. **Adjust threshold:** Modify prediction threshold in code
2. **More legitimate samples:** Add diverse legitimate URLs
3. **Better features:** Ensure features are discriminative

### Issue: High False Negatives

**Solutions:**
1. **More phishing samples:** Add diverse phishing patterns
2. **Recent data:** Use recent phishing examples
3. **Class weights:** Penalize false negatives more

---

## 🎓 Advanced: Custom Training

### Modify Training Script

Edit `ml/train_enhanced_model.py`:

**1. Change Model Hyperparameters:**
```python
# Around line 104
xgb_model = xgb.XGBClassifier(
    n_estimators=300,        # Increase for more trees
    max_depth=8,             # Increase for more complex patterns
    learning_rate=0.03,      # Decrease for better learning
    ...
)
```

**2. Add Feature Engineering:**
```python
# Around line 69
# Add new features
X['combined_feature'] = X['having_ip_address'] + X['long_url']
```

**3. Adjust Class Weights:**
```python
# Around line 104
xgb_model = xgb.XGBClassifier(
    ...
    scale_pos_weight=2,      # Penalize false negatives more
    ...
)
```

### Custom Evaluation Script

Create `ml/evaluate_model.py`:

```python
import pickle
import pandas as pd
from sklearn.metrics import classification_report

# Load model
model = pickle.load(open('../backend/phishingUrlDetectionBackend/model/XGBoostClassifier.sav', 'rb'))

# Load test data
test_data = pd.read_csv('your_test_data.csv')
X_test = test_data.drop('label', axis=1)
y_test = test_data['label']

# Predict
y_pred = model.predict(X_test)

# Evaluate
print(classification_report(y_test, y_pred))
```

---

## 📈 Monitoring Model Performance

### Create Test Script

```python
# test_model_accuracy.py
import requests
import pandas as pd

# Test known phishing URLs
phishing_urls = [
    "http://testsafebrowsing.appspot.com/s/phishing.html",
    # Add more known phishing URLs
]

# Test known legitimate URLs
legitimate_urls = [
    "https://www.google.com",
    "https://www.github.com",
    # Add more known legitimate URLs
]

correct = 0
total = 0

# Test phishing URLs
for url in phishing_urls:
    response = requests.get(f"http://localhost:8000/api/?url={url}")
    data = response.json()
    if data['predictionMade'] == 1:  # Should be phishing
        correct += 1
    total += 1

# Test legitimate URLs
for url in legitimate_urls:
    response = requests.get(f"http://localhost:8000/api/?url={url}")
    data = response.json()
    if data['predictionMade'] == 0:  # Should be legitimate
        correct += 1
    total += 1

accuracy = (correct / total) * 100
print(f"Live accuracy: {accuracy:.2f}%")
```

---

## ✅ Quick Start Checklist

- [ ] Backup existing datasets
- [ ] Prepare your new dataset (CSV format)
- [ ] Check dataset has 15 features + label column
- [ ] Verify no missing values
- [ ] Check class balance (40:60 to 60:40)
- [ ] Place datasets in `ml/extracted_dataset/`
- [ ] Run training script: `python train_enhanced_model.py`
- [ ] Check model performance (> 90% accuracy)
- [ ] Restart Django server
- [ ] Test with known URLs
- [ ] Monitor for false positives/negatives

---

## 🆘 Ready to Provide Your Dataset

**What I need from you:**

1. **Dataset format:**
   - Do you have URLs only, or features already extracted?
   - What format? (CSV, JSON, Excel, etc.)
   - How many samples?

2. **Label information:**
   - How are phishing/legitimate labeled? (0/1, true/false, etc.)
   - Are labels verified?

3. **Dataset characteristics:**
   - Time period of data
   - Source of data
   - Any specific phishing types (banking, social media, etc.)

**Share your dataset and I'll:**
- ✅ Analyze the format
- ✅ Create extraction script if needed
- ✅ Train optimized model
- ✅ Evaluate performance
- ✅ Provide accuracy report

---

## 🎯 Expected Results

With good dataset (10k+ samples per class):
- **Accuracy:** 95-98%
- **Precision:** 94-97%
- **Recall:** 93-96%
- **F1-Score:** 94-97%
- **False Positive Rate:** < 3%
- **False Negative Rate:** < 4%

**Your model will be production-ready!**

---

**Ready to retrain? Share your dataset details or run the training script if you have data in the correct format!**





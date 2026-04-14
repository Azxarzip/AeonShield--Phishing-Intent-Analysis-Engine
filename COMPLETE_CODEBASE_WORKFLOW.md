# AeonShield: Complete Codebase Workflow & Integration Guide
## BEC & Phishing Detection System

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Complete Workflow (3 Phases)](#complete-workflow-3-phases)
3. [File Integration Map](#file-integration-map)
4. [Detailed Component Breakdown](#detailed-component-breakdown)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Execution Timeline](#execution-timeline)

---

## System Architecture Overview

**AeonShield** is a 3-phase machine learning system that detects **Business Email Compromise (BEC)** attacks through:
- **Phase 1**: Feature Engineering + ML-based Threat Detection
- **Phase 2**: Stylometry Analysis + Account Takeover Detection
- **Phase 3**: Organizational Graph Analysis + Interactive Dashboard

### Key Innovation
By combining **technical features** (urgency, domain spoofing) + **linguistic analysis** (writing style) + **organizational structure**, the system detects both:
- **External Attackers** (completely new sender)
- **Account Compromises** (known sender with unusual behavior)

---

## Complete Workflow (3 Phases)

### PHASE 1: BASELINE MODEL TRAINING

#### Step 1: Data Generation
**File: `data_simulator.py`**
```
Purpose: Generate synthetic BEC/phishing dataset
Output: simulated_emails.csv (2000 records)
```

**What it does:**
- Creates 2000 synthetic email records with labels
- Generates 6 numerical features:
  - `urgency_score`: 0-1 (how urgent the email sounds)
  - `domain_similarity_score`: 0-1 (how closely domain matches legitimate)
  - `financial_keyword_count`: Count of money-related words
  - `request_type`: 0=None, 1=Info, 2=Wire Transfer
  - `sender_anomaly`: 0=Known sender, 1=Unknown sender
  - `label`: 0=Legitimate, 1=Malicious

**Logic:**
```
Malicious Probability = 
    0.2 (base)
    + 0.5 × urgency_score
    + 0.3 × (domain_sim > 0.7)
    + 0.2 × (request_type > 0)
    + 0.4 × sender_anomaly
    + 0.2 × (financial_keywords > 3)
```

#### Step 2: Feature Engineering & Model Training
**File: `train_model.py`**
```
Dependencies: data_simulator.py (must run first)
Inputs: simulated_emails.csv
Outputs: model.pkl, feature_names.pkl, confusion_matrix.png
```

**What it does:**
1. Loads synthetic data from CSV
2. Calls `feature_engineer.py` to preprocess features
3. Splits data: 80% train, 20% test
4. Trains **Random Forest Classifier** with class weights
5. Generates confusion matrix visualization

**Process:**
```
simulated_emails.csv
    ↓
preprocess_features() [feature_engineer.py]
    ↓
X (features), y (labels)
    ↓
train_test_split(80/20)
    ↓
RandomForestClassifier(weighted)
    ↓
model.pkl ✓
confustion_matrix.png ✓
feature_names.pkl ✓
```

**Class Weighting:**
- Legitimate emails: weight=1 (baseline)
- Malicious emails: weight=5 (5x importance)
- Ensures model catches more threats despite class imbalance

---

### PHASE 2: STYLOMETRY & ATO DETECTION

#### Step 1: Enhanced Data Generation with Email Text
**File: `data_simulator_enhanced.py`**
```
Dependencies: None (standalone)
Output: simulated_emails_enhanced.csv (includes email_body column)
```

**What it does:**
- Generates same structured features as Phase 1
- **ADDS** `email_body` column with realistic email text
- Uses sender profiles to create style-consistent emails:
  - CEO_Formal: Polite, formal, low punctuation
  - Manager_Casual: Casual, uses exclamations, contractions
  - Attacker_Generic: Urgent, poor grammar, excessive punctuation
  - ATO_Compromised: Baseline style with subtle variations

**Sender Profiles in `EmailTemplate.SENDER_PROFILES`:**
```python
{
    'CEO_Formal': {
        'urgency_words': ['kindly', 'appreciate', 'require'],
        'punctuation_freq': {'!': 0.02, '.': 0.95, ',': 0.20},
        'exclamations': False,
        'contractions': False
    },
    'Manager_Casual': {
        'urgency_words': ['need', 'asap', 'urgent'],
        'punctuation_freq': {'!': 0.15, '.': 0.70, ',': 0.15},
        'exclamations': True,
        'contractions': True
    },
    ...
}
```

#### Step 2: Stylometric Feature Extraction
**File: `stylometry_analyzer.py`**
```
Classes: StylometryAnalyzer, BaselineProfileBuilder
Purpose: Extract 17 linguistic features from email text
```

**StylometryAnalyzer - 17 Features Extracted:**

1. **Punctuation Features (5):**
   - `punctuation_exclamation_freq`: ! frequency
   - `punctuation_question_freq`: ? frequency
   - `punctuation_ellipsis_freq`: ... frequency
   - `punctuation_comma_freq`: , frequency
   - `punctuation_density`: Overall punctuation density

2. **Sentence Structure (2):**
   - `avg_sentence_length`: Words per sentence (0-1 normalized)
   - `sentence_length_variance`: Consistency of sentence lengths

3. **Vocabulary (3):**
   - `vocabulary_richness`: Type-Token Ratio (unique/total words)
   - `corporate_jargon_freq`: Use of business jargon
   - `rare_words_freq`: Use of formal/rare words

4. **Word Patterns (2):**
   - `avg_word_length`: Average character per word
   - `word_length_variance`: Variation in word lengths

5. **Linguistic Markers (4):**
   - `contraction_freq`: I'm, don't, won't, etc.
   - `pronoun_freq`: I, we, you, they usage
   - `urgency_words_freq`: urgent, ASAP, critical
   - `capitalization_freq`: ALL CAPS words

6. **Composite (1):**
   - `formality_score`: Composite measure (30% rare words + 20% jargon - 20% contractions, etc.)

**Example Analysis:**
```
Email Text: "Hi team! I need $250K ASAP!!! Wire to account ****5678. Confirm ASAP!!!"

Features extracted:
- punctuation_exclamation_freq: 0.35 (3 exclamations in short text)
- formality_score: 0.15 (low formality due to casual tone)
- urgency_words_freq: 0.45 ("ASAP" appears twice)
- capitalization_freq: 0.25 (multiple CAPS words)
- avg_sentence_length: 0.20 (short, choppy sentences)
```

**BaselineProfileBuilder:**
- Builds individual sender profiles from their historical emails
- Calculates mean and std-dev for each feature
- Stores in `baseline_profiles.pkl` for later ATO detection

#### Step 3: Enhanced Model Training with Stylometry
**File: `train_model_stylometry.py`**
```
Dependencies: data_simulator_enhanced.py (must generate data first)
Inputs: simulated_emails_enhanced.csv
Outputs: 
  - model_stylometry.pkl
  - feature_names_stylometry.pkl
  - baseline_profiles.pkl
  - profile_builder.pkl
  - confusion_matrix_stylometry.png
  - roc_curve_stylometry.png
  - feature_importance_stylometry.csv
```

**What it does:**
1. Loads enhanced data (with email text)
2. Calls `preprocess_features()` which:
   - Extracts 17 stylometry features from each email_body
   - Combines with 5 technical features
   - One-hot encodes request_type (3 columns)
   - **Total: 25 features**
3. Trains Random Forest with improved hyperparameters
4. Builds baseline profiles for ATO detection
5. Generates visualizations (confusion matrix, ROC curve, feature importance)

**Feature List (25 total):**
```
Technical (5):        is_ato, urgency_score, domain_similarity_score, 
                      financial_keyword_count, sender_anomaly
Stylometry (17):      punctuation_*, sentence_*, vocabulary_*, 
                      avg_word_length, word_length_variance, 
                      contraction_freq, pronoun_freq, urgency_words_freq, 
                      capitalization_freq, formality_score
One-Hot Encoded (3):  req_type_0, req_type_1, req_type_2
```

**Model Improvements in Phase 2:**
```python
RandomForestClassifier(
    n_estimators=150,        # Deeper ensemble
    max_depth=15,            # Taller trees
    min_samples_split=5,     # Better regularization
    class_weight={0:1, 1:5}  # Weighted for rare class
)
```

---

### PHASE 2B: ACCOUNT TAKEOVER (ATO) DETECTION

#### File: `ato_detector.py`
```
Classes: ATODetector
Dependencies: train_model_stylometry.py output files
Purpose: Detect if known sender's account is compromised
```

**How ATO Detection Works:**

When an email arrives from a KNOWN sender:

1. **Extract Stylometry Features** (StylometryAnalyzer)
   - Get 17 stylometry features from email text

2. **Compare to Baseline** (BaselineProfileBuilder.detect_style_drift)
   - Calculate Z-score for each feature against sender's profile
   - Formula: `Z = (feature_value - sender_mean) / sender_std`
   - If |Z| > 2.0 → anomaly detected

3. **Get ML Prediction** (Random Forest)
   - Feed all 25 features to trained model
   - Get probability of "malicious"

4. **Calculate ATO Confidence** (Weighted Combination)
   ```
   ATO_Confidence = 
       40% × (anomaly_score/3.0)           [style drift weight]
       + 40% × model.predict_proba[1]      [ML probability]
       + 20% × sender_anomaly_flag         [new sender factor]
   ```

5. **Classify Threat Type:**
   ```
   If (style_drift AND ml_predicts_malicious AND confidence > 0.6):
       → ACCOUNT_TAKEOVER (known sender, unusual behavior)
   Else if (NOT style_drift AND ml_predicts_malicious):
       → EXTERNAL_ATTACKER (new sender, malicious)
   Else if (style_drift ONLY):
       → STYLE_VARIATION (false positive)
   Else:
       → LEGITIMATE
   ```

**Example Scenario:**
```
CEO's account compromised:
- Sender: "John Executive" (known = 0 anomaly)
- Email: "URGENT!!! Wire $250K ASAP!!!"
- Z-score analysis: Formality 3.2σ lower, Exclamation 4.1σ higher
- Is_anomaly: TRUE
- ML Confidence: 0.92
- ATO_Confidence = 0.4×(2.5/3) + 0.4×0.92 + 0.2×0 = 0.33 + 0.37 = 0.70
- **Result: ACCOUNT_TAKEOVER (70% confidence)**
```

---

### PHASE 2C: EXPLAINABLE AI (XAI)

#### File: `xai_explainer.py`
```
Class: BECExplainer
Purpose: Explain predictions using SHAP (SHapley Additive exPlanations)
```

**What it does:**
- Uses SHAP TreeExplainer on Random Forest model
- For each prediction, shows:
  - Top 5 features driving the decision
  - How much each feature contributed (%)
  - Risk level categorization
  - Reason codes with high-level explanations

**Example Output:**
```
Prediction: MALICIOUS (92% confidence)
Risk Level: 🔴 CRITICAL

Feature Contributions:
1. urgency_score: 35% (high urgency increases risk)
2. punctuation_exclamation_freq: 28% (excessive ! increases risk)
3. financial_keyword_count: 18% (money language increases risk)
4. formality_score: 15% (low formality increases risk)
5. capitalization_freq: 4% (CAPS words increase risk)

Reason Codes:
- URG_HIGH: High urgency score (0.95)
- FIN_KEYWORDS: 5 financial keywords found
- DOM_SPOOF: Domain similarity 0.92 (typosquatting detected)
```

**SHAP Value Explanation:**
- SHAP "allocates credit" for the prediction among features
- +SHAP value = feature pushes prediction toward malicious
- -SHAP value = feature pushes toward legitimate
- Magnitude = strength of influence

---

### PHASE 3: ORGANIZATIONAL GRAPH & DASHBOARD

#### File: `org_graph_analyzer.py`
```
Class: OrganizationalGraph
Purpose: Model communication patterns and detect structural anomalies
```

**What it stores:**
```
Nodes (People):
  - Name, Role (CEO, Manager, Employee), Department
  - Communication count (how many they emailed)
  - Contacted count (how many emailed them)

Edges (Communications):
  - From sender → To recipient
  - Weight = frequency
  - Attributes = date, count, context
```

**Structural Anomaly Detection:**

When someone emails someone else, system checks:

1. **First Contact?** (+0.2 anomaly score)
   - Has sender never emailed this person before?

2. **Hierarchy Violation?** (+0.15 score)
   - CEO directly emailing junior employee (skipping managers)?

3. **Communication Degree?** (+0.1 score)
   - Person suddenly contacting many new people?

4. **Department Crossing?** (+0.15 score)
   - Crossing departments for first time?

5. **Unusual Target Contact?** (+0.1 score)
   - Low-visibility person contacting high-visibility person?

**Example:**
```
CEO sends email to Finance Junior for first time
- First Contact: YES → +0.2
- Hierarchy: CEO to Employee → +0.15
- Dept Crossing: C-level to Junior Finance → +0.15
- Total Anomaly: 0.50

With stylometric anomalies + ML detection → Strong ATO signal
```

#### File: `dashboard.py`
```
Framework: Streamlit (Python web framework)
Purpose: Interactive real-time threat analysis dashboard
Features:
  - Dark neon theme ("cyber-forensic terminal" aesthetic)
  - Real-time email analysis input
  - Multi-phase threat detection results
  - SHAP explanations visualization
  - Organizational graph visualization
  - Threat timeline & logs
  - KPI metrics (threat pulse, spoofing counts)
```

**Dashboard Workflow:**
```
User Input: sender_name, email_text, technical features
       ↓
Call all 3 phases:
  - Phase 1: ML prediction
  - Phase 2: ATO detection + stylometry
  - Phase 3: Org graph anomalies
       ↓
Combine Results & Generate Report
       ↓
Display:
  - Risk level indicator
  - Confidence scores
  - SHAP feature contributions
  - Recommendation (block/verify/safe)
  - Organizational context
```

---

## File Integration Map

### Dependency Graph

```
DATA GENERATION LAYER:
├── data_simulator.py
│   └──→ simulated_emails.csv (2000 records, 5 technical features)
│
├── data_simulator_enhanced.py
│   └──→ simulated_emails_enhanced.csv (2000 records + email_body text)
│
└── (Optional) email_metadata.json, synthetic_emails.csv, etc.


FEATURE ENGINEERING LAYER:
├── feature_engineer.py
│   ├── preprocess_features()
│   │   ├─ Takes: DataFrame with urgency, domain_sim, etc.
│   │   ├─ Calls: create_stylometry_features_df() if email_body present
│   │   └─ Returns: X (25 features), y (labels)
│   │
│   └── preprocess_features_for_prediction()
│       ├─ Takes: Single email (sender_name, email_text, technical features)
│       ├─ Extracts stylometry features
│       └─ Returns: DataFrame ready for model prediction
│
└── stylometry_analyzer.py
    ├── StylometryAnalyzer
    │   ├── extract_features(email_text)
    │   │   └─ Returns: Dict of 17 features (0-1 normalized)
    │   └── Methods:
    │       ├─ _count_punctuation()
    │       ├─ _avg_sentence_length()
    │       ├─ _vocabulary_richness()
    │       └─ etc.
    │
    └── BaselineProfileBuilder
        ├── build_profile(sender_name, email_texts)
        │   └─ Calculates mean/std of features for sender
        │
        └── detect_style_drift(sender_name, email_text)
            └─ Calculates Z-scores vs baseline


MODEL TRAINING LAYER:
├── train_model.py (Phase 1)
│   ├─ Input: simulated_emails.csv
│   ├─ Uses: feature_engineer.preprocess_features()
│   ├─ Trains: RandomForestClassifier (100 estimators)
│   └─ Output:
│       ├── model.pkl
│       ├── feature_names.pkl
│       └── confusion_matrix.png
│
└── train_model_stylometry.py (Phase 2)
    ├─ Input: simulated_emails_enhanced.csv
    ├─ Uses: feature_engineer.preprocess_features()
    ├─ Uses: stylometry_analyzer.StylometryAnalyzer
    ├─ Trains: RandomForestClassifier (150 estimators, depth 15)
    └─ Output:
        ├── model_stylometry.pkl
        ├── feature_names_stylometry.pkl
        ├── baseline_profiles.pkl
        ├── profile_builder.pkl
        ├── confusion_matrix_stylometry.png
        ├── roc_curve_stylometry.png
        └── feature_importance_stylometry.csv


XAI LAYER:
└── xai_explainer.py
    └── BECExplainer
        ├─ Created with: model, feature_names
        ├─ Method: explain_prediction(X_pred)
        │   ├─ Uses: SHAP TreeExplainer
        │   └─ Returns: Dict with SHAP values, feature contributions, risk level
        │
        └── Generates:
            ├─ Risk categorization (CRITICAL/HIGH/MEDIUM/LOW)
            ├─ Feature breakdown (top 5 influencers)
            └─ Reason codes (URG_HIGH, DOM_SPOOF, etc.)


ATO DETECTION LAYER:
└── ato_detector.py
    └── ATODetector
        ├─ Initialized with: profile_builder, model, feature_names
        ├─ Method: detect_ato(sender_name, email_text, technical_features)
        │   ├─ Step 1: detect_style_drift()
        │   ├─ Step 2: ML prediction
        │   ├─ Step 3: XAI explanation
        │   ├─ Step 4: Calculate ATO confidence
        │   └─ Step 5: Classify threat type
        │
        └── Returns: Dict with:
            ├─ is_ato_suspected: Boolean
            ├─ ato_confidence: 0-1 score
            ├─ style_drift_details: Feature deviations
            ├─ ml_probability: Malicious probability
            ├─ xai_explanation: SHAP breakdown
            ├─ threat_type: ACCOUNT_TAKEOVER/EXTERNAL_ATTACKER/etc.
            └─ recommendation: Action to take


ORGANIZATIONAL LAYER:
└── org_graph_analyzer.py
    └── OrganizationalGraph
        ├─ Method: add_communication(sender, recipient, role, dept)
        ├─ Method: detect_structural_anomalies(sender, recipient)
        │   └─ Returns: anomaly_score, anomaly_list
        │
        └── Used by: train_phase3.py


PHASE 3 INTEGRATION:
└── train_phase3.py
    ├─ Loads: simulated_emails_enhanced.csv
    ├─ Calls: build_org_graph_from_data()
    ├─ Creates: OrganizationalGraph
    └─ Output: org_graph.pkl


PREDICTION & INFERENCE:
├── predict_email.py
│   └── predict_new_email_modern(sender_name, email_text, urgency, ...)
│       ├─ Calls: analyze_incoming_email_for_ato()
│       │   └─ Loads: model_stylometry.pkl, feature_names_stylometry.pkl, profile_builder.pkl
│       │   └─ Creates: ATODetector instance
│       │   └─ Runs: detect_ato()
│       │   └─ Returns: Full analysis result
│       │
│       ├─ Calls: generate_ato_report()
│       │   └─ Formats analysis into readable report
│       │
│       └─ Optional: Load org_graph.pkl for Phase 3 analysis
│


DASHBOARD & UI:
├── dashboard.py
│   ├─ Framework: Streamlit
│   ├─ Loads: model_stylometry.pkl, profile_builder.pkl, org_graph.pkl
│   ├─ On user input:
│   │   ├─ Calls: preprocess_features_for_prediction()
│   │   ├─ Calls: analyze_incoming_email_for_ato()
│   │   ├─ Calls: explainer.explain_prediction()
│   │   ├─ Calls: org_graph.detect_structural_anomalies()
│   │   └─ Renders: Interactive threat report
│   │
│   ├── Directory: web/
│   │   └── index.html (optional frontend)
│   │
│   └── Uses: stitch_integration.py (for AI design assistant)
│
└── stitch_integration.py
    └─ Helpers for Google Stitch (UI design tool)


TEST FILES:
├── test_phase2.py
│   └─ Tests stylometry extraction and ATO detection
│
└── train_phase3.py
    └─ Builds organizational graph and tests Phase 3
```

---

## Detailed Component Breakdown

### 1. DATA SIMULATOR (`data_simulator.py`)

**Purpose:** Generate synthetic BEC dataset for training

**Key Outputs:**
```python
simulated_emails.csv
├── urgency_score (0-1): Beta distribution biased toward low
├── domain_similarity_score (0-1): Beta distribution biased toward high (typosquatting)
├── financial_keyword_count (0-10): Poisson distribution
├── request_type (0/1/2): Random integer (None/Info/Wire)
├── sender_anomaly (0/1): 70% normal senders, 30% unknown
└── label (0/1): Determined by weighted probability formula
```

**Why Beta Distribution?**
- Beta(a=3, b=5): Pushes values toward lower (legitimate)
- Beta(a=5, b=2): Pushes values toward higher (suspicious)
- Allows realistic skewed distribution (most emails legitimate)

---

### 2. FEATURE ENGINEER (`feature_engineer.py`)

**Two Key Functions:**

#### `preprocess_features(df)` - For Training
```python
Input: DataFrame with email_body column
Process:
  1. Extract 17 stylometry features from email_body
  2. Keep 5 technical features
  3. One-hot encode request_type (3 columns)
  4. Return: X (25 features), y (labels)
Output: Ready for model.fit(X, y)
```

#### `preprocess_features_for_prediction(email_text, urgency, ...)` - For Inference
```python
Input: Single new email + technical features
Process:
  1. Create StylometryAnalyzer() instance
  2. Extract 17 features from email text
  3. Combine with 5 technical features
  4. One-hot encode request_type
  5. Ensure feature column order matches training
Output: DataFrame with 25 features, ready for model.predict()
```

**Why Column Order Matters:**
```python
# Training used columns in this order:
X.columns = [
    'is_ato', 'urgency_score', ..., 'req_type_0', 'req_type_1', 'req_type_2'
]

# Prediction must use SAME order
X_pred_aligned = X_pred.reindex(columns=feature_names, fill_value=0)

# Otherwise: features misaligned → wrong predictions
```

---

### 3. STYLOMETRY ANALYZER (`stylometry_analyzer.py`)

#### **StylometryAnalyzer.extract_features()**

**Punctuation Category (5 features):**
```python
def _count_punctuation(text, mark):
    return (text.count(mark) / (len(text) / 100)) clipped to [0,1]

Features:
- punctuation_exclamation_freq: Occurrences of '!'
- punctuation_question_freq: Occurrences of '?'
- punctuation_ellipsis_freq: Occurrences of '...'
- punctuation_comma_freq: Occurrences of ','
- punctuation_density: All punctuation combined
```

**Sentence Structure (2 features):**
```python
def _avg_sentence_length(sentences, words):
    avg = total_words / num_sentences
    return min(avg / 30, 1.0)  # Normalize to typical range

def _sentence_length_variance(sentences, words):
    variance = np.var([len(s.split()) for s in sentences])
    return min(variance / 100, 1.0)
```

**Vocabulary Complexity (3 features):**
```python
def _vocabulary_richness(words):
    # Type-Token Ratio
    return unique_words / total_words  # 0-1

def _corporate_jargon_freq(text):
    count = text.count('synergy') + text.count('leverage') + ...
    return normalized_count

def _rare_words_freq(text):
    count = text.count('pursuant') + text.count('aforementioned') + ...
    return normalized_count
```

**Word Patterns (2 features):**
```python
def _avg_word_length(words):
    avg = mean([len(w) for w in words])
    return min(avg / 15, 1.0)

def _word_length_variance(words):
    variance = np.var([len(w) for w in words])
    return min(variance / 20, 1.0)
```

**Linguistic Markers (4 features):**
```python
def _contraction_freq(text):
    contractions = ["i'm", "don't", "can't", ...]
    count = sum(text.count(c) for c in contractions)
    return normalized_count

def _pronoun_freq(text):
    pronouns = ['i ', 'me ', 'we ', 'you ', ...]
    count = sum(text.count(p) for p in pronouns)
    return normalized_count

def _urgency_words_freq(text):
    urgency = ['urgent', 'asap', 'immediate', ...]
    count = sum(text.count(u) for u in urgency)
    return normalized_count

def _capitalization_freq(text):
    caps_words = len([w for w in text.split() if w.isupper()])
    return caps_words / (total_words / 10)
```

**Composite (1 feature):**
```python
def _calculate_formality(features):
    formality = (
        0.3 × rare_words_freq +
        0.2 × corporate_jargon +
        0.2 × (1 - contraction_freq) +
        0.15 × (1 - exclamation_freq) +
        0.15 × (1 - capitalization_freq)
    )
    return min(formality, 1.0)
```

**All 17 features normalized to [0, 1] with:** `np.clip(v, 0, 1)`

#### **BaselineProfileBuilder**

Builds sender-specific profile:
```python
def build_profile(sender_name, email_texts):
    """
    Input: sender_name (string) + list of their past emails
    Process:
      1. For each email, extract 17 stylometry features
      2. Calculate mean for each feature
      3. Calculate std-dev for each feature
    Output: Dict
      {
        'sender': 'John Executive',
        'mean': {...},
        'std': {...},
        'num_emails': 10
      }
    """
```

**Z-score Calculation:**
```python
def detect_style_drift(sender_name, new_email_text, threshold=2.0):
    """
    For each feature:
      z_score = (new_value - mean) / std
    
    If |z_score| > threshold → anomaly detected
    Returns: is_anomaly (bool), anomaly_score (float), z_scores (dict)
    """
```

**Example:**
```
Sender "John Executive" baseline:
- formality_score = 0.78 ± 0.05
- punctuation_exclamation_freq = 0.02 ± 0.01

New email from John:
- formality_score = 0.15 → Z = (0.15-0.78)/0.05 = -12.6 ← VERY anomalous
- punctuation_exclamation_freq = 0.35 → Z = (0.35-0.02)/0.01 = 33.0 ← VERY anomalous

is_anomaly = TRUE, anomaly_score = 2.8 (mean absolute Z-scores)
```

---

### 4. MODEL TRAINING (`train_model.py` & `train_model_stylometry.py`)

#### **Phase 1: Basic Model**

```python
# Load data
df = pd.read_csv('simulated_emails.csv')
X, y = preprocess_features(df)  # 5 technical features only

# Split: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train: Weighted to catch more malicious emails
model = RandomForestClassifier(
    n_estimators=100,
    class_weight={0: 1, 1: 5},  # Malicious = 5x importance
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))  # Precision, Recall, F1-score

# Save
joblib.dump(model, 'model.pkl')
joblib.dump(X.columns.tolist(), 'feature_names.pkl')
```

**Why Class Weights?**
- Without weights: Model may predict everything as "Legitimate" (majority class)
- With weights: Misclassifying malicious email = 5x penalty
- Results in: Higher recall for malicious (catches more threats)

#### **Phase 2: Enhanced Model with Stylometry**

```python
# Load enhanced data
df = pd.read_csv('simulated_emails_enhanced.csv')
X, y = preprocess_features(df)  # 25 features: technical + stylometry + OHE

# Split (same as Phase 1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, ...)

# Train: Deeper forest
model = RandomForestClassifier(
    n_estimators=150,         # More trees
    max_depth=15,             # Taller trees (capture more patterns)
    min_samples_split=5,      # Regularization (prevent overfitting)
    class_weight={0: 1, 1: 5},
    random_state=42,
    n_jobs=-1                 # Parallel processing
)
model.fit(X_train, y_train)

# Evaluate with metrics
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]
auc_score = roc_auc_score(y_test, y_pred_proba)

# Save model artifacts
joblib.dump(model, 'model_stylometry.pkl')
joblib.dump(X.columns.tolist(), 'feature_names_stylometry.pkl')

# Build baseline profiles for ATO detection
analyzer = StylometryAnalyzer()
profile_builder = BaselineProfileBuilder(analyzer)
for sender in df['sender_name'].unique():
    sender_emails = df[df['sender_name'] == sender]['email_body'].tolist()
    if len(sender_emails) >= 3:
        profile = profile_builder.build_profile(sender, sender_emails)
joblib.dump(profile_builder, 'profile_builder.pkl')
```

**Visualization Outputs:**
```
confusion_matrix_stylometry.png
  ├─ Predicted Legitimate vs Legitimate (TN)
  ├─ Predicted Legitimate vs Malicious (FN) ← Should be small
  ├─ Predicted Malicious vs Legitimate (FP) ← May be larger (catch threats)
  └─ Predicted Malicious vs Malicious (TP) ← Should be large

roc_curve_stylometry.png
  └─ AUC score (area under curve) → 1.0 = perfect, 0.5 = random

feature_importance_stylometry.csv
  └─ Top 15: urgency_score, domain_similarity_score, 
     punctuation_exclamation_freq, formality_score, ...
```

---

### 5. ATO DETECTOR (`ato_detector.py`)

#### **ATODetector Class**

**Initialization:**
```python
def __init__(self, profile_builder, model, feature_names):
    self.profile_builder = profile_builder  # Sender baselines
    self.model = model                       # Trained RF classifier
    self.feature_names = feature_names       # Column names
    self.analyzer = StylometryAnalyzer()
    self.explainer = BECExplainer(model, feature_names)
```

**Main Method: `detect_ato()`**

```python
def detect_ato(sender_name, email_text, technical_features, threshold=2.0):
    """
    3-Step Detection Process:
    """
    
    # STEP 1: Check if baseline profile exists
    if sender_name not in profile_builder.profiles:
        return {
            'is_ato_suspected': False,
            'confidence': 0.0,
            'reason': 'No baseline profile (unknown sender)'
        }
    
    # STEP 2: Stylometric deviation detection
    is_anomaly, anomaly_score, z_scores = (
        profile_builder.detect_style_drift(
            sender_name, email_text, threshold=2.0
        )
    )
    # is_anomaly: Boolean (any |z| > 2.0?)
    # anomaly_score: Float (mean |z|)
    # z_scores: Dict {feature: z_value}
    
    # STEP 3: ML prediction
    X_pred = preprocess_features_for_prediction(
        email_text, urgency_score, domain_similarity, 
        financial_keyword_count, request_type, sender_anomaly
    )
    X_pred_aligned = X_pred.reindex(columns=feature_names, fill_value=0)
    
    ml_pred = model.predict(X_pred_aligned)[0]  # 0 or 1
    ml_prob = model.predict_proba(X_pred_aligned)[0][1]  # 0-1
    
    # STEP 4: XAI explanation
    explanation = explainer.explain_prediction(X_pred_aligned)
    
    # STEP 5: Calculate ATO confidence
    ato_confidence = (
        0.4 × min(anomaly_score / 3.0, 1.0) +  # 40% style drift weight
        0.4 × ml_prob +                         # 40% ML weight
        0.2 × sender_anomaly                    # 20% sender history weight
    )
    
    # STEP 6: Classify threat type
    if is_anomaly and ml_pred == 1 and ato_confidence > 0.6:
        threat_type = "ACCOUNT_TAKEOVER"
    elif is_anomaly and ml_pred == 0:
        threat_type = "STYLE_VARIATION"
    elif not is_anomaly and ml_pred == 1:
        threat_type = "EXTERNAL_ATTACKER"
    else:
        threat_type = "LEGITIMATE"
    
    # STEP 7: Generate recommendation
    if threat_type == "ACCOUNT_TAKEOVER" and ato_confidence > 0.7:
        recommendation = "🔴 IMMEDIATE: Verify sender via phone"
    elif threat_type == "ACCOUNT_TAKEOVER":
        recommendation = "🟠 HIGH: Contact sender urgently"
    elif threat_type == "EXTERNAL_ATTACKER":
        recommendation = "🟠 BLOCK: Move to quarantine"
    elif threat_type == "STYLE_VARIATION":
        recommendation = "🟡 CAUTION: Monitor for additional signals"
    else:
        recommendation = "🟢 SAFE: No threats detected"
    
    return {
        'is_ato_suspected': (is_anomaly and ml_pred == 1 and ato_confidence > 0.6),
        'ato_confidence': ato_confidence,
        'anomaly_score': anomaly_score,
        'style_drift_detected': is_anomaly,
        'style_drift_details': z_scores,
        'ml_prediction': 'MALICIOUS' if ml_pred == 1 else 'LEGITIMATE',
        'ml_probability': ml_prob,
        'xai_explanation': explanation,
        'threat_type': threat_type,
        'recommendation': recommendation
    }
```

#### **Helper Methods:**

```python
def _calculate_ato_confidence(is_anomaly, anomaly_score, ml_prob, sender_anomaly):
    """Weighted combination of signals"""
    confidence = 0.0
    if is_anomaly:
        style_signal = min(anomaly_score / 3.0, 1.0) * 0.4
        confidence += style_signal
    confidence += ml_prob * 0.4
    if sender_anomaly == 0 and is_anomaly:  # Known sender, unusual style
        confidence += 0.2
    return min(confidence, 1.0)

def _format_style_drift(z_scores):
    """Convert z-scores to readable descriptions"""
    # Find top 5 deviations
    # For each: if |z| > 2.5 → "DRAMATIC", > 2.0 → "SIGNIFICANT"
    # Return: {'feature': 'DRAMATIC less formality', ...}

def _classify_threat(is_anomaly, ml_pred, technical_features):
    """Threat type classification logic"""
    # Returns: ACCOUNT_TAKEOVER, COMPROMISED_ACCOUNT, 
    #          EXTERNAL_ATTACKER, STYLE_VARIATION, LEGITIMATE

def _generate_recommendation(is_anomaly, ml_pred, confidence):
    """Security action recommendation"""
    # Returns: 🔴 IMMEDIATE / 🟠 HIGH / 🟡 CAUTION / 🟢 SAFE
```

---

### 6. XAI EXPLAINER (`xai_explainer.py`)

#### **BECExplainer Class**

**Initialization:**
```python
def __init__(self, model, feature_names, background_data=None):
    self.model = model
    self.feature_names = feature_names
    # TreeExplainer: Uses Random Forest structure for fast SHAP calculation
    self.explainer = shap.TreeExplainer(model)
```

**Main Method: `explain_prediction()`**

```python
def explain_prediction(X_pred):
    """
    Input: Single row DataFrame (25 features)
    
    Process:
      1. Get SHAP values for malicious class
      2. Calculate feature importance (|SHAP|)
      3. Get top 5 features
      4. Format contributions as percentages
      5. Generate reason codes
      6. Assign risk level
    
    Output: Dict with:
      - prediction: 'MALICIOUS' or 'LEGITIMATE'
      - confidence_score: Probability (0-1)
      - risk_level: 'CRITICAL' / 'HIGH' / 'MEDIUM' / 'LOW'
      - base_score: SHAP expected value
      - feature_contributions: {
          'urgency_score': {
            'value': 0.95,
            'contribution_pct': 35.2,
            'shap_value': 0.42,
            'direction': 'increases risk'
          },
          ...
        }
      - reason_codes: [
          {
            'code': 'URG_HIGH',
            'reason': 'High urgency score detected (0.95)',
            'severity': 'HIGH'
          },
          ...
        ]
    """
    
    # Get probability
    probability = model.predict_proba(X_pred)[0][1]
    
    # Get SHAP values (contribution of each feature)
    shap_values = explainer.shap_values(X_pred)  # Shape: (1, 25) for class 1
    
    # Calculate |SHAP| = importance
    feature_importance = np.abs(shap_values[0])
    
    # Sort by importance, get top 5
    top_indices = np.argsort(feature_importance)[::-1][:5]
    
    # Build feature contributions
    contributions = {}
    total_abs_shap = np.sum(feature_importance)
    
    for idx in top_indices:
        feature_name = feature_names[idx]
        feature_value = X_pred.iloc[0, idx]
        shap_val = shap_values[0, idx]
        
        contribution_pct = (
            (abs(shap_val) / total_abs_shap) * probability * 100
        )
        
        contributions[feature_name] = {
            'value': feature_value,
            'contribution_pct': contribution_pct,
            'shap_value': shap_val,
            'direction': 'increases risk' if shap_val > 0 else 'decreases risk'
        }
    
    return {
        'prediction': 'MALICIOUS' if prediction == 1 else 'LEGITIMATE',
        'confidence_score': probability,
        'risk_level': self._calculate_risk_level(probability),
        'feature_contributions': contributions,
        'reason_codes': self._generate_reason_codes(X_pred, probability)
    }
```

**Risk Level Calculation:**
```python
def _calculate_risk_level(confidence):
    if confidence >= 0.8: return "🔴 CRITICAL"
    elif confidence >= 0.6: return "🟠 HIGH"
    elif confidence >= 0.4: return "🟡 MEDIUM"
    else: return "🟢 LOW"
```

**Reason Codes:**
```python
def _generate_reason_codes(X_pred, probability):
    """Rule-based high-level explanations"""
    codes = []
    
    # Rule 1: High urgency
    if urgency_score > 0.7:
        codes.append({
            'code': 'URG_HIGH',
            'reason': f'High urgency score detected ({urgency_score:.2f})',
            'severity': 'HIGH' if urgency > 0.85 else 'MEDIUM'
        })
    
    # Rule 2: Domain spoofing
    if domain_similarity > 0.75:
        codes.append({
            'code': 'DOM_SPOOF',
            'reason': f'Domain appears spoofed ({domain_similarity:.2f})',
            'severity': 'HIGH'
        })
    
    # Rule 3: Financial keywords
    if financial_keywords > 3:
        codes.append({
            'code': 'FIN_KEYWORDS',
            'reason': f'{financial_keywords} financial keywords detected',
            'severity': 'MEDIUM'
        })
    
    # Rule 4: Sender anomaly
    if sender_anomaly == 1:
        codes.append({
            'code': 'SENDER_ANOMALY',
            'reason': 'Sender exhibits anomalous behavior',
            'severity': 'MEDIUM'
        })
    
    # Rule 5: Wire transfer
    if request_type == 2:  # Wire transfer
        codes.append({
            'code': 'WIRE_REQUEST',
            'reason': 'Wire transfer request detected (high-value target)',
            'severity': 'HIGH'
        })
    
    return codes
```

---

### 7. ORGANIZATIONAL GRAPH (`org_graph_analyzer.py`)

#### **OrganizationalGraph Class**

**Data Structures:**
```python
self.graph = nx.DiGraph()  # NetworkX directed graph
self.sender_history = {}   # sender → set of recipients
self.recipient_history = {} # recipient → set of senders
self.hierarchy = {}        # sender → role (CEO/Manager/Employee)
self.departments = {}      # sender → department (Finance/HR/etc.)
```

**Key Method: `add_communication()`**

```python
def add_communication(sender, recipient, weight=1.0, role=None, dept=None):
    """
    Register a communication in the organizational graph
    
    Stores:
      - Nodes: sender, recipient (with attributes: role, dept)
      - Edge: sender → recipient (with weight = frequency)
      - History: Who has sender contacted before?
    """
    # Add/update nodes
    if not graph.has_node(sender):
        graph.add_node(sender, role=role, department=dept, ...)
    if not graph.has_node(recipient):
        graph.add_node(recipient, role=None, department=None, ...)
    
    # Add/update edge
    if graph.has_edge(sender, recipient):
        graph[sender][recipient]['weight'] += weight
    else:
        graph.add_edge(sender, recipient, weight=weight)
    
    # Track history
    sender_history[sender].add(recipient)
    recipient_history[recipient].add(sender)
```

**Key Method: `detect_structural_anomalies()`**

```python
def detect_structural_anomalies(sender, recipient):
    """
    Detect if sender→recipient communication is unusual
    
    Returns:
      anomaly_score: 0-1 (how unusual)
      anomalies_detected: List of violation types
    """
    
    anomaly_score = 0.0
    anomalies = []
    
    # CHECK 1: First contact?
    if recipient not in sender_history[sender]:
        anomaly_score += 0.2
        anomalies.append("FIRST_CONTACT")
    
    # CHECK 2: Hierarchy violation?
    sender_level = hierarchy_map.get(hierarchy[sender], 0)
    recipient_level = hierarchy_map.get(hierarchy[recipient], 0)
    
    if sender_level == 3 and recipient_level == 1:  # CEO to Employee
        anomaly_score += 0.15
        anomalies.append("HIERARCHY_BYPASS")
    
    # CHECK 3: Communication degree spike?
    out_degree = graph.out_degree(sender)
    avg_degree = mean([d for n, d in graph.out_degree()])
    
    if out_degree > avg_degree * 2:
        anomaly_score += 0.1
        anomalies.append("HIGH_COMMUNICATION_DEGREE")
    
    # CHECK 4: Department crossing?
    sender_dept = departments[sender]
    recipient_dept = departments[recipient]
    
    if sender_dept != recipient_dept:
        # Check if sender has ever crossed departments
        dept_crossings = sum(
            1 for (s, r) in communication_counts
            if s == sender and departments[r] != sender_dept
        )
        if dept_crossings == 0:
            anomaly_score += 0.15
            anomalies.append("UNUSUAL_DEPT_CROSSING")
    
    # CHECK 5: Unusual target contact?
    # If low-betweenness person (isolated) suddenly contacting high-betweenness
    # (central) person
    sender_centrality = betweenness_centrality(sender)
    recipient_centrality = betweenness_centrality(recipient)
    avg_centrality = mean(betweenness_centrality.values())
    
    if sender_centrality < avg_centrality * 0.5:
        if recipient_centrality > avg_centrality * 1.5:
            anomaly_score += 0.1
            anomalies.append("UNUSUAL_TARGET_CONTACT")
    
    return {
        'anomaly_score': min(anomaly_score, 1.0),
        'anomalies_detected': anomalies,
        'sender_role': hierarchy[sender],
        'recipient_role': hierarchy[recipient],
        ...
    }
```

---

### 8. DASHBOARD (`dashboard.py`)

**Framework:** Streamlit (Python web framework for interactive dashboards)

**Architecture:**
```
User Input Form (Sidebar)
    ↓
[sender_name, email_text, urgency, domain_sim, financial_keywords, request_type, sender_anomaly]
    ↓
Process All 3 Phases
    ├─ Phase 1: model_stylometry.predict()
    ├─ Phase 2: ato_detector.detect_ato()
    └─ Phase 3: org_graph.detect_structural_anomalies()
    ↓
Combine Results
    ↓
Display Components:
    ├─ KPI Cards (Threat Level, Confidence, etc.)
    ├─ Risk Gauge (visual indicator)
    ├─ SHAP Feature Contributions (bar chart)
    ├─ Stylometric Deviations (table)
    ├─ Organizational Context (graph visualization)
    ├─ Recommendations (action items)
    └─ Threat Timeline (history)
```

**Key Components:**

```python
# Page Configuration
st.set_page_config(
    page_title="AeonShield: Phishing & Intent Analysis Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme CSS (Neon Cyber-Forensic)
theme = {
    'bg_main': '#000000',              # Black background
    'text_main': '#ffffff',             # White text
    'accent_blue': '#00d4ff',           # Neon cyan
    'accent_red': '#ff3131',            # Alert red
    'accent_green': '#39ff14'           # Nano green
}

# Sidebar Input
with st.sidebar:
    st.header("📨 Email Analysis Input")
    sender_name = st.text_input("Sender Name")
    email_text = st.text_area("Email Body")
    urgency = st.slider("Urgency Score", 0.0, 1.0)
    domain_sim = st.slider("Domain Similarity", 0.0, 1.0)
    financial_keywords = st.number_input("Financial Keywords", 0, 10)
    request_type = st.selectbox("Request Type", [0, 1, 2])
    sender_anomaly = st.checkbox("Unknown Sender?")
    
    if st.button("Analyze Email"):
        # Call analysis pipeline
        result = analyze_incoming_email_for_ato(...)
        
        # Display results in main area
        display_threat_report(result)
        display_feature_contributions(result['xai_explanation'])
        display_org_context(org_graph.detect_structural_anomalies(...))

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Threat Level", result['threat_type'], 
              delta=f"{result['ato_confidence']:.1%}")
with col2:
    st.metric("ML Confidence", f"{result['ml_probability']:.1%}")
with col3:
    st.metric("Style Drift Score", f"{result['anomaly_score']:.2f}")
with col4:
    st.metric("Org Anomalies", len(org_anomalies['anomalies_detected']))

# Feature Contributions (Bar Chart)
contributions = result['xai_explanation']['feature_contributions']
st.bar_chart({
    feature: data['contribution_pct'] 
    for feature, data in contributions.items()
})

# Recommendation
if result['threat_type'] == 'ACCOUNT_TAKEOVER':
    st.error(result['recommendation'])
elif result['threat_type'] == 'EXTERNAL_ATTACKER':
    st.error(result['recommendation'])
else:
    st.success(result['recommendation'])
```

**Theme Constants:**
```python
dark_theme_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
    
    # Neon cyber aesthetic
    html, body {{ background-color: #000000; }}
    h1, h2 {{ 
        font-family: 'Space Grotesk', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .neon-border {{
        border: 1px solid #00d4ff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.15);
    }}
    
    .threat-critical {{
        border: 1px solid #ff3131;
        box-shadow: 0 0 10px rgba(255, 49, 49, 0.3);
    }}
    
    .threat-safe {{
        border: 1px solid #39ff14;
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.2);
    }}
    </style>
"""
```

---

## Data Flow Diagrams

### **Diagram 1: Training Pipeline (Phase 2)**

```
┌─────────────────────────────────────────────────────────────┐
│ DATA GENERATION: data_simulator_enhanced.py                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 2000 emails with:                                            │
│ ├─ Technical features (5)                                   │
│ ├─ Email body text                                          │
│ └─ Labels (0/1)                                             │
│                                                              │
│ Output: simulated_emails_enhanced.csv                        │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│ PREPROCESSING: feature_engineer.py                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ For each email:                                              │
│ 1. Extract 17 stylometry features  (stylometry_analyzer.py) │
│ 2. Keep 5 technical features                                │
│ 3. One-hot encode request_type (3 columns)                  │
│ 4. X shape: (2000, 25), y shape: (2000,)                    │
│                                                              │
│ Output: X, y (ready for training)                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│ TRAINING: train_model_stylometry.py                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. train_test_split(X, y, 0.2)                              │
│    ├─ X_train: (1600, 25)                                   │
│    └─ X_test: (400, 25)                                     │
│                                                              │
│ 2. RandomForestClassifier(150 trees, max_depth=15)          │
│    ├─ class_weight={0:1, 1:5}                               │
│    └─ model.fit(X_train, y_train)                           │
│                                                              │
│ 3. Evaluate:                                                │
│    ├─ Accuracy, Precision, Recall, F1                       │
│    ├─ ROC-AUC score                                         │
│    └─ Feature importance ranking                            │
│                                                              │
│ Outputs:                                                    │
│ ├─ model_stylometry.pkl (155 KB)                            │
│ ├─ feature_names_stylometry.pkl (1 KB)                      │
│ ├─ baseline_profiles.pkl (sender baselines)                 │
│ ├─ profile_builder.pkl (baseline builder)                   │
│ ├─ confusion_matrix_stylometry.png                          │
│ ├─ roc_curve_stylometry.png                                 │
│ └─ feature_importance_stylometry.csv                        │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
       ✅ Training Complete
       (Ready for inference)
```

### **Diagram 2: Inference Pipeline (Real Email Analysis)**

```
┌─────────────────────────────────────────────────────────────┐
│ NEW EMAIL INPUT                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ sender_name = "John Executive"                               │
│ email_text = "Hi, I need a wire transfer of $250K..."        │
│ urgency_score = 0.95                                         │
│ domain_similarity_score = 0.85                               │
│ financial_keyword_count = 3                                  │
│ request_type = 2 (Wire)                                      │
│ sender_anomaly = 0 (known sender)                            │
│                                                              │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2A: Extract Features (feature_engineer.py)            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. Create StylometryAnalyzer()                              │
│ 2. Extract 17 features from email_text                       │
│    ├─ punctuation_exclamation_freq = 0.35                   │
│    ├─ formality_score = 0.15                                │
│    ├─ urgency_words_freq = 0.45                             │
│    └─ ... (14 more)                                         │
│                                                              │
│ 3. Combine with technical features + OHE                    │
│ 4. Output: X_pred shape (1, 25)                             │
│ 5. Align with model's expected columns                      │
│                                                              │
│ Output: X_pred (ready for model)                             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────────┐
             │                                                  │
             ↓                                                  ↓
    ┌───────────────────┐              ┌──────────────────────┐
    │ PHASE 2B: ATO     │              │ PHASE 1: Basic ML    │
    │ Detection         │              │ Prediction           │
    └───────────────────┘              └──────────────────────┘
             │                                  │
             │ Loads:                           │ Loads:
             │ - profile_builder.pkl            │ - model_stylometry.pkl
             │ - baseline profiles              │ - feature_names*.pkl
             │                                  │ - XAI explainer
             │                                  │
             ↓                                  ↓
    ┌───────────────────────────────────┐ ┌───────────────────┐
    │ 1. Extract baseline profile for    │ │ ML Prediction:    │
    │    "John Executive"                │ │ model.predict     │
    │    ├─ mean features                │ │ (0 or 1)          │
    │    └─ std features                 │ │                   │
    │                                    │ │ ML Confidence:    │
    │ 2. Detect style drift:             │ │ predict_proba     │
    │    ├─ For each feature:            │ │ (0.0-1.0)         │
    │    │  Z = (value - mean) / std     │ │                   │
    │    └─ If |Z| > 2.0 → anomaly      │ │ Output: {          │
    │                                    │ │   'ml_pred': 1,   │
    │ 3. Calculate anomaly_score         │ │   'ml_prob': 0.92 │
    │    (mean absolute Z-scores)        │ │ }                 │
    │                                    │ │                   │
    │    is_anomaly: TRUE                │ └───────────────────┘
    │    anomaly_score: 2.8              │
    │    z_scores: {...}                 │
    │                                    │
    │ Output: {                          │
    │   'is_anomaly': True,              │
    │   'anomaly_score': 2.8,            │
    │   'style_deviations': {...}        │
    │ }                                  │
    └───────────────────────────────────┘

             ↓
    ┌───────────────────────────────────────────────┐
    │ PHASE 3: XAI Explanation (xai_explainer.py)  │
    ├───────────────────────────────────────────────┤
    │                                               │
    │ 1. Load SHAP TreeExplainer                   │
    │ 2. shap_values = explainer.shap_values(X)    │
    │ 3. For top 5 features:                       │
    │    ├─ feature_importance = |SHAP|            │
    │    ├─ contribution_pct = (|SHAP|/total)*100  │
    │    └─ direction = +/- risk                   │
    │                                               │
    │ 4. Generate reason codes:                    │
    │    ├─ URG_HIGH (0.95)                        │
    │    ├─ DOM_SPOOF (0.85)                       │
    │    ├─ FIN_KEYWORDS (3 found)                 │
    │    └─ etc.                                   │
    │                                               │
    │ 5. Calculate risk_level:                     │
    │    >= 0.8 → CRITICAL                         │
    │    >= 0.6 → HIGH                             │
    │                                               │
    │ Output: {                                    │
    │   'features': {urgency: 35%, ...},           │
    │   'reason_codes': [...],                     │
    │   'risk_level': 'CRITICAL'                   │
    │ }                                            │
    └───┬───────────────────────────────────────────┘
        │
        ↓
    ┌─────────────────────────────────────────────────┐
    │ COMBINE ALL SIGNALS (ato_detector.py)           │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │ ATO_Confidence =                                │
    │   0.4 × (anomaly_score/3.0)                     │
    │   + 0.4 × ml_prob                              │
    │   + 0.2 × sender_anomaly                       │
    │                                                 │
    │ = 0.4×(2.8/3) + 0.4×0.92 + 0.2×0               │
    │ = 0.4×0.93 + 0.37                              │
    │ = 0.37 + 0.37 = 0.74                            │
    │                                                 │
    │ Classification:                                 │
    │ is_anomaly (TRUE) AND                           │
    │ ml_pred (1) AND                                 │
    │ confidence (0.74 > 0.6)                         │
    │ → ACCOUNT_TAKEOVER ✓                            │
    │                                                 │
    │ Recommendation:                                 │
    │ "🔴 IMMEDIATE: Verify sender via phone"        │
    │                                                 │
    │ Output: {                                       │
    │   'is_ato_suspected': True,                    │
    │   'ato_conf': 0.74,                            │
    │   'threat_type': 'ACCOUNT_TAKEOVER',           │
    │   'recommendation': '🔴 IMMEDIATE: ...'        │
    │ }                                               │
    └───┬─────────────────────────────────────────────┘
        │
        ↓ (Optional Phase 3)
    ┌─────────────────────────────────────────────────┐
    │ PHASE 4: Org Graph (org_graph_analyzer.py)     │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │ 1. Load org_graph.pkl                          │
    │ 2. Check structural anomalies:                 │
    │    ├─ First contact? NO                        │
    │    ├─ Hierarchy bypass? NO (both in Finance)   │
    │    ├─ Dept crossing? NO                        │
    │    └─ Other? NO                                │
    │                                                 │
    │ Result: Low structural anomaly (0.05)          │
    │                                                 │
    │ (Confirms: ATO likely, not org issue)          │
    │                                                 │
    │ Output: {                                       │
    │   'anomaly_score': 0.05,                       │
    │   'anomalies': []                              │
    │ }                                               │
    └───┬─────────────────────────────────────────────┘
        │
        ↓
    ┌─────────────────────────────────────────────────┐
    │ FINAL REPORT (combine all phases)               │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │ 👤 SENDER: John Executive                      │
    │ 🎯 THREAT: ACCOUNT_TAKEOVER                    │
    │                                                 │
    │ 📊 ATO CONFIDENCE: 74%                         │
    │    └─ Style Drift: 2.8σ                        │
    │    └─ ML Confidence: 92%                       │
    │                                                 │
    │ 🎭 STYLE DEVIATIONS:                           │
    │    • DRAMATIC higher exclamation               │
    │    • DRAMATIC lower formality                  │
    │    • SIGNIFICANT higher urgency words          │
    │                                                 │
    │ 🔗 ORG CONTEXT: No anomalies                   │
    │                                                 │
    │ ⚠️  RECOMMENDATION:                             │
    │    🔴 IMMEDIATE: Verify sender via phone       │
    │                                                 │
    │ 💰 Feature Breakdown (SHAP):                    │
    │    1. punctuation_exclamation: 28%             │
    │    2. formality_score: 25%                     │
    │    3. urgency_words_freq: 18%                  │
    │    4. urgency_score: 15%                       │
    │    5. capitalization_freq: 14%                 │
    │                                                 │
    └─────────────────────────────────────────────────┘
        │
        ↓
    Display in Dashboard / Log Report
```

---

## Execution Timeline

### **Full System Execution Order**

```
Step 1: DATA GENERATION (First Time Only)
├─ python data_simulator.py
│  └─ Creates: simulated_emails.csv (5 technical features)
│
└─ python data_simulator_enhanced.py
   └─ Creates: simulated_emails_enhanced.csv (+ email_body)

Step 2: PHASE 1 TRAINING
├─ python train_model.py
│  ├─ Loads: simulated_emails.csv
│  ├─ Creates:
│  │  ├─ model.pkl (baseline 100-tree RF)
│  │  ├─ feature_names.pkl
│  │  └─ confusion_matrix.png
│  │
│  └─ Result: Basic phishing detection (5 features)

Step 3: PHASE 2 TRAINING
├─ python train_model_stylometry.py
│  ├─ Loads: simulated_emails_enhanced.csv
│  ├─ Extracts: 17 stylometry features per email
│  ├─ Creates:
│  │  ├─ model_stylometry.pkl (150-tree RF, depth 15)
│  │  ├─ feature_names_stylometry.pkl (25 features)
│  │  ├─ baseline_profiles.pkl (sender profiles)
│  │  ├─ profile_builder.pkl (builder class)
│  │  ├─ confusion_matrix_stylometry.png
│  │  ├─ roc_curve_stylometry.png
│  │  └─ feature_importance_stylometry.csv
│  │
│  └─ Result: Enhanced detection + ATO capability (25 features)

Step 4: PHASE 3 TRAINING (Optional)
├─ python train_phase3.py
│  ├─ Loads: simulated_emails_enhanced.csv
│  ├─ Builds: OrganizationalGraph from sender/recipient pairs
│  ├─ Creates:
│  │  └─ org_graph.pkl
│  │
│  └─ Result: Structural anomaly detection

Step 5: TEST & DEMO
├─ python test_phase2.py
│  ├─ Tests: Stylometry extraction
│  ├─ Tests: ATO detection on sample emails
│  └─ Outputs: Test results
│
└─ python predict_email.py
   ├─ Runs: Full detection pipeline
   ├─ Tests: On hardcoded CEO spoof example
   └─ Outputs: Complete ATO report (CLI)

Step 6: INTERACTIVE DASHBOARD
├─ streamlit run dashboard.py
│  ├─ Launches: Web UI on http://localhost:8501
│  ├─ Features:
│  │  ├─ Real-time email input form
│  │  ├─ All 3 phases in real-time
│  │  ├─ SHAP visualizations
│  │  ├─ Org graph context
│  │  └─ Threat timeline
│  │
│  └─ Result: Interactive threat analysis interface

PRODUCTION DEPLOYMENT:
├─ All .pkl files in production
├─ ato_detector.py as inference engine
├─ Dashboard as monitoring interface
└─ Periodic retraining (quarterly/yearly)
```

---

## Summary

**AeonShield System Architecture:**

| Phase | Purpose | Input | Output | Key Algorithm |
|-------|---------|-------|--------|----------------|
| **Phase 1** | Baseline threat detection | 5 technical features | Binary prediction (0/1) | Random Forest (100 trees) |
| **Phase 2** | Stylometry + ATO | 5 tech + 17 linguistic | ATO confidence, threat type | Z-score drift + RF (150 trees) + SHAP |
| **Phase 3** | Org context | Sender/recipient pairs | Structural anomalies | NetworkX graph analysis |
| **XAI** | Explain predictions | 25 features + model | Feature contributions | SHAP TreeExplainer |
| **Dashboard** | Real-time analysis | Email + metadata | Interactive report | All of above combined |

**Key Innovation:**
- Combines **technical signals** (urgency, domain spoofing) + **linguistic fingerprints** (writing style) + **organizational structure** to detect both external attackers AND compromised internal accounts

---

**For Students:** This codebase demonstrates a complete ML end-to-end pipeline: data generation → feature engineering → model training → evaluation → explainability → production deployment. Use it as a reference for your own projects!


import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score, roc_curve
from feature_engineer import preprocess_features
from stylometry_analyzer import StylometryAnalyzer, BaselineProfileBuilder

def train_model_with_stylometry():
    print("--- BEC Phishing Detection Model Training (With Stylometry) ---\n")
    
    # 1. Load Enhanced Data with Email Text
    try:
        df = pd.read_csv('simulated_emails_enhanced.csv')
        print(f"✅ Loaded enhanced dataset: {len(df)} records")
    except FileNotFoundError:
        print("Error: 'simulated_emails_enhanced.csv' not found.")
        print("   Run: python data_simulator_enhanced.py first")
        return

    # 2. Extract Stylometry Features & Preprocess
    print("\n📝 Extracting stylometry features...")
    X, y = preprocess_features(df)
    
    feature_count = X.shape[1]
    print(f"✅ Created {feature_count} features")
    print(f"   - Technical: 5 (urgency, domain_sim, financial_keywords, sender_anomaly, is_ato)")
    print(f"   - Stylometry: 17 (punctuation, sentence structure, vocabulary, etc.)")
    print(f"   - One-Hot Encoded: 3 (request_type)")
    
    # 3. Split Data
    print("\n🔀 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   - Train: {len(X_train)} samples")
    print(f"   - Test: {len(X_test)} samples")

    # 4. Train Model with Class Weights
    print("\n🤖 Training Random Forest with stylometry...")
    model = RandomForestClassifier(
        n_estimators=150,  # Increased from 100
        max_depth=15,      # New parameter for deeper trees
        min_samples_split=5,  # New for regularization
        class_weight={0: 1, 1: 5},  # High weight for malicious
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("✅ Model trained successfully")

    # 5. Evaluate
    print("\n📊 Evaluating Model...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Malicious']))
    
    # ROC-AUC Score
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"\n📈 ROC-AUC Score: {auc_score:.4f}")

    # 6. Save Model & Features
    print("\n💾 Saving model and features...")
    joblib.dump(model, 'model_stylometry.pkl')
    print("✅ Model saved to 'model_stylometry.pkl'")
    
    feature_names = X.columns.tolist()
    joblib.dump(feature_names, 'feature_names_stylometry.pkl')
    print("✅ Feature names saved to 'feature_names_stylometry.pkl'")
    
    # Save feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    feature_importance.to_csv('feature_importance_stylometry.csv', index=False)
    print("✅ Feature importance saved to 'feature_importance_stylometry.csv'")
    
    # 7. Visualizations
    print("\n📊 Generating visualizations...")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Predicted Legitimate', 'Predicted Malicious'],
                yticklabels=['Actual Legitimate', 'Actual Malicious'])
    plt.title('Confusion Matrix: BEC Detection with Stylometry')
    plt.ylabel('Actual Category')
    plt.xlabel('Predicted Category')
    plt.savefig('confusion_matrix_stylometry.png', dpi=300, bbox_inches='tight')
    print("✅ Confusion matrix saved to 'confusion_matrix_stylometry.png'")
    plt.close()
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve: BEC Detection with Stylometry')
    plt.legend(loc="lower right")
    plt.savefig('roc_curve_stylometry.png', dpi=300, bbox_inches='tight')
    print("✅ ROC curve saved to 'roc_curve_stylometry.png'")
    plt.close()
    
    # Feature Importance Plot
    top_features = feature_importance.head(15)
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Feature Importance')
    plt.title('Top 15 Most Important Features for BEC Detection')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('feature_importance_stylometry.png', dpi=300, bbox_inches='tight')
    print("✅ Feature importance plot saved to 'feature_importance_stylometry.png'")
    plt.close()
    
    # 8. Baseline Profiles for ATO Detection
    print("\n🔍 Building baseline stylometry profiles for ATO detection...")
    analyzer = StylometryAnalyzer()
    profile_builder = BaselineProfileBuilder(analyzer)
    
    # Build profiles for each sender
    baseline_profiles = {}
    for sender in df['sender_name'].unique()[:3]:  # Top 3 senders
        sender_emails = df[df['sender_name'] == sender]['email_body'].tolist()
        if len(sender_emails) >= 3:
            try:
                profile = profile_builder.build_profile(sender, sender_emails)
                baseline_profiles[sender] = profile
                print(f"   ✅ Profile created for '{sender}' ({len(sender_emails)} emails)")
            except Exception as e:
                print(f"   ⚠️  Could not create profile for '{sender}': {e}")
    
    # Save profiles
    joblib.dump(baseline_profiles, 'baseline_profiles.pkl')
    joblib.dump(profile_builder, 'profile_builder.pkl')
    print("✅ Baseline profiles saved to 'baseline_profiles.pkl'")
    
    # 9. Summary
    print("\n" + "="*70)
    print("🎉 TRAINING COMPLETE WITH STYLOMETRY FEATURES")
    print("="*70)
    print(f"\nModel Performance:")
    print(f"  - Accuracy: {(y_pred == y_test).sum() / len(y_test):.2%}")
    print(f"  - ROC-AUC: {auc_score:.4f}")
    print(f"  - Malicious Recall: {(y_pred[y_test == 1] == 1).sum() / (y_test == 1).sum():.2%}")
    print(f"\nCapabilities Unlocked:")
    print(f"  ✅ Technical threat detection (urgency, domain spoofing, etc.)")
    print(f"  ✅ Linguistic fingerprinting (17 stylometry features)")
    print(f"  ✅ Account takeover (ATO) detection via style drift")
    print(f"  ✅ Baseline profile comparison for compromised accounts")

if __name__ == "__main__":
    train_model_with_stylometry()

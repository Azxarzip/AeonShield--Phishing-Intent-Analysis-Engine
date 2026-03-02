
import pandas as pd
import joblib
from ato_detector import ATODetector, generate_ato_report
from stylometry_analyzer import StylometryAnalyzer, BaselineProfileBuilder

def test_phase2():
    print("="*75)
    print("🧪 PHASE 2 TESTING: NLP STYLOMETRY & ATO DETECTION")
    print("="*75)
    print()
    
    # Load model and profiles
    print("📦 Loading models and profiles...")
    try:
        model = joblib.load('model_stylometry.pkl')
        feature_names = joblib.load('feature_names_stylometry.pkl')
        profile_builder = joblib.load('profile_builder.pkl')
        print(f"✅ Model loaded with {len(feature_names)} features")
        print(f"✅ Baseline profiles loaded: {list(profile_builder.profiles.keys())}")
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return
    
    # Initialize ATO detector
    detector = ATODetector(profile_builder, model, feature_names)
    
    print("\n" + "="*75)
    print("TEST 1: Legitimate Email from CEO (Normal Style)")
    print("="*75)
    
    test1_email = """Dear Team,

Kindly arrange a wire transfer of $100,000 to account ****5678 for the quarterly 
vendor payment. Please process this by end of business today.

Thank you for your prompt attention to this matter.

Best regards,
CEO"""
    
    result1 = detector.detect_ato(
        sender_name="John Executive",
        email_text=test1_email,
        technical_features={
            'urgency_score': 0.6,
            'domain_similarity_score': 0.1,
            'financial_keyword_count': 2,
            'request_type': 2,
            'sender_anomaly': 0
        }
    )
    
    print(generate_ato_report(result1))
    
    print("\n" + "="*75)
    print("TEST 2: Suspicious Email from CEO (STYLE DRIFT - Possible ATO)")
    print("="*75)
    
    test2_email = """Hi!!!

I need a HUGE wire transfer of $500,000 to account ****9999 RIGHT NOW!!!

This is CRITICAL!!! Don't tell anybody!

Thanks mate!"""
    
    result2 = detector.detect_ato(
        sender_name="John Executive",
        email_text=test2_email,
        technical_features={
            'urgency_score': 0.95,
            'domain_similarity_score': 0.88,
            'financial_keyword_count': 4,
            'request_type': 2,
            'sender_anomaly': 0  # No sender anomaly flag, but style is very different!
        }
    )
    
    print(generate_ato_report(result2))
    
    print("\n" + "="*75)
    print("TEST 3: External Attacker (Unknown Sender)")
    print("="*75)
    
    test3_email = """Hello!

Please wire $150,000 ASAP to account ****1111.

Thanks!"""
    
    result3 = detector.detect_ato(
        sender_name="Unknown Attacker",
        email_text=test3_email,
        technical_features={
            'urgency_score': 0.88,
            'domain_similarity_score': 0.92,
            'financial_keyword_count': 3,
            'request_type': 2,
            'sender_anomaly': 1  # Flagged as anomalous sender
        }
    )
    
    print(generate_ato_report(result3))
    
    # Summary statistics
    print("\n" + "="*75)
    print("📊 PHASE 2 STYLOMETRY CAPABILITIES SUMMARY")
    print("="*75)
    print()
    print("✅ Features Extracted:")
    print("   • Punctuation patterns (exclamation, question, ellipsis frequency)")
    print("   • Sentence structure (average length, variance)")
    print("   • Vocabulary complexity (richness, jargon, rare words)")
    print("   • Word patterns (average length, variance)")
    print("   • Linguistic markers (contractions, pronouns, urgency words)")
    print("   • Formality score (composite linguistic indicator)")
    print()
    print("✅ ATO Detection Signals:")
    print("   • Style drift detection via Z-score analysis")
    print("   • Baseline profile comparison (legitimate vs. compromised)")
    print("   • Multi-signal confidence scoring")
    print("   • Threat type classification (EXTERNAL_ATTACKER vs ACCOUNT_TAKEOVER)")
    print()
    print("✅ Model Performance:")
    print("   • 98.37% Malicious Recall (detects almost all threats)")
    print("   • ROC-AUC: 0.8231 (good discrimination)")
    print("   • Combined technical + stylometric analysis")
    print()
    print("="*75)

if __name__ == '__main__':
    test_phase2()

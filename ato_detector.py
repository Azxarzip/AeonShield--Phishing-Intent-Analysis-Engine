
import joblib
import pandas as pd
import numpy as np
from stylometry_analyzer import StylometryAnalyzer, BaselineProfileBuilder
from xai_explainer import BECExplainer
from typing import Dict, List, Tuple

class ATODetector:
    """Detect Account Takeover scenarios using stylometry baseline deviations."""
    
    def __init__(self, profile_builder: BaselineProfileBuilder, model, feature_names: List[str]):
        """
        Initialize ATO detector.
        
        Args:
            profile_builder: BaselineProfileBuilder with sender profiles
            model: Trained ML model
            feature_names: List of feature names used by model
        """
        self.profile_builder = profile_builder
        self.model = model
        self.feature_names = feature_names
        self.analyzer = StylometryAnalyzer()
        self.explainer = BECExplainer(model, feature_names)
    
    def detect_ato(self, sender_name: str, email_text: str, 
                   technical_features: Dict, threshold: float = 2.0) -> Dict:
        """
        Detect if an email from a known sender is an ATO attempt.
        
        Args:
            sender_name: Name of sender
            email_text: Email body text
            technical_features: Dict with urgency_score, domain_similarity, etc.
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary with ATO detection results
        """
        
        # Check if we have a baseline profile for this sender
        if sender_name not in self.profile_builder.profiles:
            return {
                'sender': sender_name,
                'is_ato_suspected': False,
                'confidence': 0.0,
                'reason': 'No baseline profile available',
                'style_drift': None,
                'ml_prediction': None
            }
        
        # 1. Detect stylometric deviation
        is_anomaly, anomaly_score, z_scores = self.profile_builder.detect_style_drift(
            sender_name, email_text, threshold=threshold
        )
        
        # 2. Get ML prediction (treats as potentially malicious)
        from feature_engineer import preprocess_features_for_prediction
        
        X_pred = preprocess_features_for_prediction(
            email_text=email_text,
            urgency_score=technical_features.get('urgency_score', 0),
            domain_similarity_score=technical_features.get('domain_similarity_score', 0),
            financial_keyword_count=technical_features.get('financial_keyword_count', 0),
            request_type=technical_features.get('request_type', 0),
            sender_anomaly=technical_features.get('sender_anomaly', 0),
            is_ato=1  # Flag as potential ATO
        )
        
        # Ensure feature alignment
        X_pred_aligned = X_pred.reindex(columns=self.feature_names, fill_value=0)
        X_pred_aligned = X_pred_aligned[self.feature_names]
        
        ml_pred = self.model.predict(X_pred_aligned)[0]
        ml_prob = self.model.predict_proba(X_pred_aligned)[0][1]
        
        # 3. Get XAI explanation
        explanation = self.explainer.explain_prediction(X_pred_aligned)
        
        # 4. Combine signals for ATO detection
        ato_confidence = self._calculate_ato_confidence(
            is_anomaly, anomaly_score, ml_prob, 
            technical_features.get('sender_anomaly', 0)
        )
        
        # 5. Build comprehensive result
        result = {
            'sender': sender_name,
            'is_ato_suspected': is_anomaly and ml_pred == 1 and ato_confidence > 0.6,
            'ato_confidence': float(ato_confidence),
            'anomaly_score': float(anomaly_score),
            'style_drift_detected': is_anomaly,
            'style_drift_details': self._format_style_drift(z_scores),
            'ml_prediction': 'MALICIOUS' if ml_pred == 1 else 'LEGITIMATE',
            'ml_probability': float(ml_prob),
            'xai_explanation': explanation,
            'threat_type': self._classify_threat(is_anomaly, ml_pred, technical_features),
            'recommendation': self._generate_recommendation(is_anomaly, ml_pred, ato_confidence)
        }
        
        return result
    
    def _calculate_ato_confidence(self, is_anomaly: bool, anomaly_score: float, 
                                  ml_prob: float, sender_anomaly: int) -> float:
        """
        Calculate confidence of ATO using multiple signals.
        
        Signals:
        - Stylometric deviation (40%)
        - ML model probability (40%)
        - Sender anomaly flag (20%)
        """
        confidence = 0.0
        
        # Stylometric signal: strong anomaly = high confidence
        if is_anomaly:
            # Normalize anomaly score
            style_signal = min(anomaly_score / 3.0, 1.0) * 0.4
            confidence += style_signal
        
        # ML signal: malicious probability
        confidence += ml_prob * 0.4
        
        # Sender anomaly signal: no history but acting suspicious = ATO
        if sender_anomaly == 0 and is_anomaly:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _format_style_drift(self, z_scores: Dict[str, float]) -> Dict[str, str]:
        """Format z-score deviations into human-readable descriptions."""
        if not z_scores:
            return {}
        
        drift_details = {}
        
        # Find most significant deviations
        sorted_z = sorted(z_scores.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        
        for feature, z_score in sorted_z:
            direction = "more" if z_score > 0 else "less"
            magnitude = abs(z_score)
            
            if magnitude > 2.5:
                intensity = "dramatic"
            elif magnitude > 2.0:
                intensity = "significant"
            else:
                intensity = "moderate"
            
            drift_details[feature] = f"{intensity.upper()} {direction} {feature.replace('_', ' ')}"
        
        return drift_details
    
    def _classify_threat(self, is_anomaly: bool, ml_pred: int, 
                        technical_features: Dict) -> str:
        """Classify the type of threat detected."""
        if not is_anomaly:
            if ml_pred == 1:
                return "EXTERNAL_ATTACKER"
            else:
                return "LEGITIMATE"
        else:
            if ml_pred == 1 and technical_features.get('sender_anomaly', 0) == 0:
                return "ACCOUNT_TAKEOVER"
            elif ml_pred == 1:
                return "COMPROMISED_ACCOUNT"
            else:
                return "STYLE_VARIATION"
    
    def _generate_recommendation(self, is_anomaly: bool, ml_pred: int, 
                                confidence: float) -> str:
        """Generate security recommendation."""
        if is_anomaly and ml_pred == 1 and confidence > 0.7:
            return "🔴 IMMEDIATE ACTION: Verify sender identity via phone. Likely account compromise."
        elif is_anomaly and ml_pred == 1:
            return "🟠 HIGH PRIORITY: Contact sender to confirm. Unusual writing pattern detected."
        elif ml_pred == 1:
            return "🟠 BLOCK & REVIEW: External threat detected. Move to quarantine."
        elif is_anomaly:
            return "🟡 CAUTION: Unusual writing style. Monitor for additional signals."
        else:
            return "🟢 SAFE: No threats detected."


def analyze_incoming_email_for_ato(sender_name: str, email_text: str, 
                                   urgency_score: float,
                                   domain_similarity_score: float,
                                   financial_keyword_count: int,
                                   request_type: int,
                                   sender_anomaly: int) -> Dict:
    """
    High-level function to analyze incoming email for ATO.
    
    Args:
        sender_name: Known sender identifier
        email_text: Raw email body
        urgency_score: Detected urgency (0-1)
        domain_similarity_score: Domain spoofing score (0-1)
        financial_keyword_count: Count of financial keywords
        request_type: Type of request (0=None, 1=Credential, 2=Wire)
        sender_anomaly: Whether sender is anomalous (0 or 1)
        
    Returns:
        Comprehensive ATO analysis result
    """
    try:
        # Load models and profiles
        model = joblib.load('model_stylometry.pkl')
        feature_names = joblib.load('feature_names_stylometry.pkl')
        profile_builder = joblib.load('profile_builder.pkl')
        
        # Initialize detector
        detector = ATODetector(profile_builder, model, feature_names)
        
        # Prepare technical features
        technical_features = {
            'urgency_score': urgency_score,
            'domain_similarity_score': domain_similarity_score,
            'financial_keyword_count': financial_keyword_count,
            'request_type': request_type,
            'sender_anomaly': sender_anomaly
        }
        
        # Detect ATO
        result = detector.detect_ato(sender_name, email_text, technical_features)
        
        return result
        
    except FileNotFoundError as e:
        return {
            'error': f'Model not found: {e}',
            'recommendation': 'Run train_model_stylometry.py first'
        }


def generate_ato_report(analysis: Dict) -> str:
    """Format ATO detection result into readable report."""
    if 'error' in analysis:
        return f"❌ Error: {analysis['error']}\n{analysis['recommendation']}"
    
    report = []
    report.append("=" * 75)
    report.append("🔍 ACCOUNT TAKEOVER (ATO) DETECTION ANALYSIS")
    report.append("=" * 75)
    report.append("")
    
    report.append(f"👤 SENDER: {analysis['sender']}")
    report.append(f"🎯 THREAT TYPE: {analysis.get('threat_type', 'UNKNOWN')}")
    report.append("")
    
    report.append(f"📊 ATO CONFIDENCE: {analysis.get('ato_confidence', 0):.1%}")
    report.append(f"   └─ Style Drift Score: {analysis.get('anomaly_score', 0):.2f}")
    report.append(f"   └─ ML Malicious Probability: {analysis.get('ml_probability', 0):.1%}")
    report.append("")
    
    if analysis.get('style_drift_detected'):
        report.append("🎭 STYLOMETRIC DEVIATIONS DETECTED:")
        for feature, description in analysis.get('style_drift_details', {}).items():
            report.append(f"   • {description}")
        report.append("")
    
    report.append(f"⚠️  RECOMMENDATION: {analysis.get('recommendation', 'Unable to recommend')}")
    report.append("")
    report.append("=" * 75)
    
    return "\n".join(report)


if __name__ == '__main__':
    # Example: Analyze email from CEO with unusual style
    example_email = """Hi,

I need a wire transfer of $250,000 to account ****5678 ASAP!!!

Gotta move quick on this!!!

Thanks!"""
    
    print("Testing ATO Detection...\n")
    result = analyze_incoming_email_for_ato(
        sender_name="CEO",
        email_text=example_email,
        urgency_score=0.95,
        domain_similarity_score=0.85,
        financial_keyword_count=3,
        request_type=2,
        sender_anomaly=0
    )
    
    print(generate_ato_report(result))

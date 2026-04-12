
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from typing import Dict, Tuple, Any


class BECExplainer:
    """
    Explainable AI wrapper for BEC detection model.
    Uses SHAP to provide transparent reasoning for predictions.
    """
    
    def __init__(self, model, feature_names: list, background_data=None):
        """
        Initialize the explainer.
        
        Args:
            model: Trained RandomForest model
            feature_names: List of feature column names
            background_data: Background dataset for SHAP (if None, uses synthetic data)
        """
        self.model = model
        self.feature_names = feature_names
        self.background_data = background_data
        
        # Initialize SHAP explainer (TreeExplainer for RandomForest)
        self.explainer = shap.TreeExplainer(model)

    def _shap_values_malicious_row(self, X_pred: pd.DataFrame) -> np.ndarray:
        """Normalize SHAP outputs across shap versions (list vs ndarray, binary layout)."""
        shap_values = self.explainer.shap_values(X_pred)
        if isinstance(shap_values, list):
            # Binary TreeExplainer: [class0, class1], each (n_samples, n_features)
            pos = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            arr = np.asarray(pos)
            return np.asarray(arr[0]).ravel() if arr.ndim >= 2 else arr.ravel()
        arr = np.asarray(shap_values)
        if arr.ndim == 3:
            return np.asarray(arr[0, :, 1]).ravel()
        if arr.ndim == 2:
            return np.asarray(arr[0]).ravel()
        return arr.ravel()

    def _expected_value_malicious(self) -> float:
        ev = self.explainer.expected_value
        if isinstance(ev, (list, tuple, np.ndarray)):
            flat = np.atleast_1d(np.asarray(ev, dtype=float))
            if flat.size > 1:
                return float(flat[1])
            return float(flat[0])
        return float(ev)
        
    def explain_prediction(self, X_pred: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a single prediction.
        
        Args:
            X_pred: DataFrame with single row (features must match training features)
            
        Returns:
            Dictionary with prediction, confidence, and detailed explanations
        """
        # Get prediction and probability
        prediction = self.model.predict(X_pred)[0]
        probability = self.model.predict_proba(X_pred)[0][1]  # Prob of Malicious (class 1)
        
        shap_class_1 = self._shap_values_malicious_row(X_pred)
        n = min(len(shap_class_1), len(self.feature_names))
        shap_class_1 = np.asarray(shap_class_1[:n], dtype=float)
        base_value = self._expected_value_malicious()
        
        # Calculate feature contributions (absolute SHAP values)
        feature_importance = np.abs(shap_class_1)
        
        # Sort features by importance
        sorted_indices = np.argsort(feature_importance)[::-1]
        
        # Create detailed explanation
        explanation = {
            'prediction': 'MALICIOUS' if int(prediction) == 1 else 'LEGITIMATE',
            'confidence_score': float(probability),
            'risk_level': self._calculate_risk_level(probability),
            'base_score': float(base_value),
            'feature_contributions': self._get_feature_breakdown(
                shap_class_1, 
                sorted_indices, 
                X_pred, 
                probability
            ),
            'reason_codes': self._generate_reason_codes(
                shap_class_1, 
                sorted_indices, 
                X_pred,
                prediction
            )
        }
        
        return explanation
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Categorize risk level based on confidence score."""
        if confidence >= 0.8:
            return "🔴 CRITICAL"
        elif confidence >= 0.6:
            return "🟠 HIGH"
        elif confidence >= 0.4:
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"
    
    def _get_feature_breakdown(self, shap_vals, sorted_indices, X_pred, total_confidence):
        """
        Create a percentage breakdown of feature contributions.
        """
        # Ensure shap_vals is 1D
        if len(shap_vals.shape) > 1 and shap_vals.shape[0] > 1:
            shap_vals = shap_vals[0]
        
        # Normalize SHAP values to represent contribution percentages
        total_abs_shap = np.sum(np.abs(shap_vals))
        
        if total_abs_shap == 0:
            total_abs_shap = 1  # Avoid division by zero
        
        contributions = {}
        n = min(len(shap_vals), len(self.feature_names), X_pred.shape[1])
        
        for idx in sorted_indices[:5]:  # Top 5 features
            if idx >= n:
                continue
            feature_name = self.feature_names[idx]
            feature_value = X_pred.iloc[0, idx]
            shap_value = float(shap_vals[idx])
            
            # Calculate percentage contribution to the malicious probability
            contribution_pct = (np.abs(shap_value) / total_abs_shap) * total_confidence * 100
            
            contributions[feature_name] = {
                'value': float(feature_value),
                'contribution_pct': float(contribution_pct),
                'shap_value': shap_value,
                'direction': 'increases risk' if shap_value > 0 else 'decreases risk'
            }
        
        return contributions
    
    def _generate_reason_codes(self, shap_vals, sorted_indices, X_pred, prediction):
        """
        Generate human-readable reason codes for the prediction.
        """
        reason_codes = []
        
        # Rule 1: High urgency score
        if 'urgency_score' in self.feature_names:
            urg_idx = self.feature_names.index('urgency_score')
            urg_val = X_pred.iloc[0, urg_idx]
            if urg_val > 0.7:
                reason_codes.append({
                    'code': 'URG_HIGH',
                    'reason': f'High urgency score detected ({urg_val:.2f})',
                    'severity': 'HIGH' if urg_val > 0.85 else 'MEDIUM'
                })
        
        # Rule 2: Domain similarity (typosquatting)
        if 'domain_similarity_score' in self.feature_names:
            dom_idx = self.feature_names.index('domain_similarity_score')
            dom_val = X_pred.iloc[0, dom_idx]
            if dom_val > 0.75:
                reason_codes.append({
                    'code': 'DOM_SPOOF',
                    'reason': f'Domain appears spoofed/similar ({dom_val:.2f})',
                    'severity': 'HIGH'
                })
        
        # Rule 3: Financial keywords
        if 'financial_keyword_count' in self.feature_names:
            fin_idx = self.feature_names.index('financial_keyword_count')
            fin_val = X_pred.iloc[0, fin_idx]
            if fin_val > 3:
                reason_codes.append({
                    'code': 'FIN_KEYWORDS',
                    'reason': f'Multiple financial keywords detected ({int(fin_val)} found)',
                    'severity': 'MEDIUM'
                })
        
        # Rule 4: Sender anomaly
        if 'sender_anomaly' in self.feature_names:
            sen_idx = self.feature_names.index('sender_anomaly')
            sen_val = X_pred.iloc[0, sen_idx]
            if sen_val == 1:
                reason_codes.append({
                    'code': 'SENDER_ANOMALY',
                    'reason': 'Sender exhibits anomalous behavior',
                    'severity': 'MEDIUM'
                })
        
        # Rule 5: Wire transfer request
        for i, fname in enumerate(self.feature_names):
            if 'req_type_' in fname:
                if X_pred.iloc[0, i] == 1 and 'req_type_2' in fname:
                    reason_codes.append({
                        'code': 'WIRE_REQUEST',
                        'reason': 'Wire transfer request detected',
                        'severity': 'HIGH'
                    })

        # Rule 6: Stylometry - Extreme Exclamations
        if 'punctuation_exclamation_freq' in self.feature_names:
            idx = self.feature_names.index('punctuation_exclamation_freq')
            val = X_pred.iloc[0, idx]
            if val > 0.6:
                reason_codes.append({
                    'code': 'STYLE_AGGRESSIVE',
                    'reason': f'Excessive punctuation/exclamations detected ({val:.2f})',
                    'severity': 'MEDIUM'
                })

        # Rule 7: Stylometry - Unusual Capitalization
        if 'capitalization_freq' in self.feature_names:
            idx = self.feature_names.index('capitalization_freq')
            val = X_pred.iloc[0, idx]
            if val > 0.5:
                reason_codes.append({
                    'code': 'STYLE_CAPS',
                    'reason': f'Unusual use of ALL CAPS detected ({val:.2f})',
                    'severity': 'MEDIUM'
                })

        # Rule 8: Stylometry - Linguistic Urgency
        if 'urgency_words_freq' in self.feature_names:
            idx = self.feature_names.index('urgency_words_freq')
            val = X_pred.iloc[0, idx]
            if val > 0.7:
                reason_codes.append({
                    'code': 'STYLE_URGENT_WORDS',
                    'reason': f'High frequency of linguistic urgency markers ({val:.2f})',
                    'severity': 'MEDIUM'
                })
        
        return reason_codes
    
    def create_visual_heatmap(self, X_pred: pd.DataFrame, save_path: str = None):
        """
        Generate SHAP waterfall plot and save as image.
        
        Args:
            X_pred: DataFrame with prediction
            save_path: Path to save the image (optional)
        """
        shap_class_1 = self._shap_values_malicious_row(X_pred)
        n = min(len(shap_class_1), len(self.feature_names))
        shap_class_1 = np.asarray(shap_class_1[:n], dtype=float)

        # Create figure with bar plot
        plt.figure(figsize=(12, 6))
        
        # Plot SHAP values as horizontal bar chart
        indices = np.argsort(np.abs(shap_class_1))[-10:]  # Top 10
        colors = ['red' if shap_class_1[i] > 0 else 'blue' for i in indices]
        plt.barh(range(len(indices)), shap_class_1[indices], color=colors)
        plt.yticks(range(len(indices)), [self.feature_names[i] for i in indices])
        plt.xlabel('SHAP Value (Impact on Prediction)')
        plt.title('SHAP Feature Importance: Top Factors in Prediction')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ SHAP visualization saved to '{save_path}'")
        
        plt.close()  # Close to avoid display issues
    
    @staticmethod
    def generate_report(explanation: Dict[str, Any]) -> str:
        """
        Format explanation into a readable report string.
        """
        report = []
        report.append("=" * 70)
        report.append("🔍 EXPLAINABLE AI ANALYSIS REPORT - BEC DETECTION")
        report.append("=" * 70)
        report.append("")
        
        report.append(f"📊 PREDICTION: {explanation['prediction']}")
        report.append(f"📈 CONFIDENCE SCORE: {explanation['confidence_score']:.2%}")
        report.append(f"⚠️  RISK LEVEL: {explanation['risk_level']}")
        report.append("")
        
        report.append("─" * 70)
        report.append("📋 FEATURE CONTRIBUTION BREAKDOWN:")
        report.append("─" * 70)
        
        for feature, data in explanation['feature_contributions'].items():
            report.append(f"\n  • {feature}:")
            report.append(f"      └─ Value: {data['value']:.4f}")
            report.append(f"      └─ Contribution: {data['contribution_pct']:.1f}%")
            report.append(f"      └─ Impact: {data['direction']}")
        
        if explanation['reason_codes']:
            report.append("\n" + "─" * 70)
            report.append("🚨 REASON CODES (Forensic Alerts):")
            report.append("─" * 70)
            
            for code in explanation['reason_codes']:
                severity_icon = "🔴" if code['severity'] == 'HIGH' else "🟠"
                report.append(f"\n  {severity_icon} [{code['code']}] {code['severity']}")
                report.append(f"      └─ {code['reason']}")
        else:
            report.append("\n✅ No specific reason codes triggered")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def load_and_initialize_explainer(model_path: str = 'model.pkl', 
                                   feature_names_path: str = 'feature_names.pkl'):
    """
    Utility function to load model and initialize explainer.
    
    Args:
        model_path: Path to saved model
        feature_names_path: Path to saved feature names
        
    Returns:
        Initialized BECExplainer instance
    """
    try:
        model = joblib.load(model_path)
        feature_names = joblib.load(feature_names_path)
        explainer = BECExplainer(model, feature_names)
        return explainer
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Could not load model or features: {e}")

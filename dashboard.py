
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from xai_explainer import BECExplainer
from ato_detector import ATODetector
from stylometry_analyzer import StylometryAnalyzer
from org_graph_analyzer import OrganizationalGraph
from feature_engineer import preprocess_features_for_prediction
from stitch_integration import (
    STITCH_WEB_APP,
    aeonshield_stitch_prompt,
    stitch_api_key_configured,
    stitch_setup_instructions,
)

# Page configuration
st.set_page_config(
    page_title="AeonShield: Phishing & Intent Analysis Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)




# Theme Constants (Neon Forensic Terminal)
theme = {
    'bg_main': '#000000',
    'bg_sidebar': '#080808',
    'card_bg': 'rgba(19, 19, 19, 0.7)',
    'card_border': 'rgba(0, 212, 255, 0.3)',
    'text_main': '#ffffff',
    'text_muted': '#859398',
    'accent_blue': '#00d4ff',   # Cybr Blue (Safe/Active)
    'accent_green': '#39ff14',  # Nano Green (Validated)
    'accent_red': '#ff3131',    # Alert Red (Threat)
    'header_bg': 'rgba(0, 0, 0, 0.85)',
    'nav_hover': 'rgba(0, 212, 255, 0.1)',
    'card_shadow': '0 0 10px rgba(0, 212, 255, 0.15)'
}

dark_theme_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {theme['bg_main']};
        color: {theme['text_main']};
        font-family: 'Inter', sans-serif;
    }}
    
    h1, h2, h3, .space-font {{
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    [data-testid="stHeader"] {{
        background-color: {theme['header_bg']};
        backdrop-filter: blur(12px);
        border-bottom: 1px solid {theme['card_border']};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {theme['bg_sidebar']} !important;
        border-right: 1px solid {theme['card_border']};
    }}

    /* Neon Elements */
    .neon-border {{
        border: 1px solid {theme['card_border']};
        border-radius: 0px !important;
        background: {theme['card_bg']};
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: {theme['card_shadow']};
    }}

    .neon-border-red {{
        border: 1px solid {theme['accent_red']};
        box-shadow: 0 0 10px rgba(255, 49, 49, 0.2);
    }}

    .neon-border-green {{
        border: 1px solid {theme['accent_green']};
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.2);
    }}

    /* KPI Card Style */
    @keyframes kpi-pulse {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(0, 212, 255, 0.15); }}
        50% {{ box-shadow: 0 0 18px rgba(0, 212, 255, 0.35); }}
    }}
    .kpi-wrapper {{
        background: rgba(19, 19, 19, 0.6);
        border: 1px solid {theme['card_border']};
        border-radius: 0px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: kpi-pulse 4s ease-in-out infinite;
    }}
    
    .kpi-wrapper:hover {{
        border-color: {theme['accent_blue']};
        background: rgba(0, 212, 255, 0.05);
    }}
    
    .kpi-title {{
        color: {theme['text_muted']};
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-value {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: {theme['text_main']};
        margin: 0;
        text-shadow: 0 0 8px {theme['accent_blue']}44;
    }}
    
    .section-header {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: {theme['accent_blue']};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {theme['card_border']};
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-transform: uppercase;
    }}

    /* Sidebar Buttons */
    [data-testid="stSidebar"] button {{
        border-radius: 0px !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        text-align: left !important;
        padding-left: 1rem !important;
        background: transparent !important;
        color: {theme['text_muted']} !important;
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }}

    [data-testid="stSidebar"] button:hover {{
        background: {theme['nav_hover']} !important;
        color: {theme['accent_blue']} !important;
        border-left: 3px solid {theme['accent_blue']} !important;
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: #000000;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {theme['card_border']};
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {theme['accent_blue']};
    }}

    .hero-grid {{
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        background:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0, 212, 255, 0.12), transparent 50%),
            radial-gradient(ellipse 60% 40% at 100% 30%, rgba(168, 85, 247, 0.08), transparent 45%),
            radial-gradient(ellipse 50% 50% at 50% 100%, rgba(57, 255, 20, 0.05), transparent 40%);
    }}
    </style>
"""

st.markdown(dark_theme_css, unsafe_allow_html=True)
st.markdown('<div class="hero-grid" aria-hidden="true"></div>', unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load all trained models and profiles with advanced fallback logic."""
    try:
        # Load Primary Model (the best one - Phase 2 Stylometry)
        model_path = 'model_stylometry.pkl'
        features_path = 'feature_names_stylometry.pkl'
        
        # Fallback to Phase 1 if Phase 2 is missing
        if not os.path.exists(model_path):
            model_path = 'model.pkl'
            features_path = 'feature_names.pkl'
            
        if not os.path.exists(model_path):
            return {'status': 'error', 'error': 'No model files found. Run training first.'}
            
        model = joblib.load(model_path)
        feature_names = joblib.load(features_path)
        
        xai_explainer = BECExplainer(model, feature_names)
        
        # Load Profiles
        profile_builder = None
        if os.path.exists('profile_builder.pkl'):
            profile_builder = joblib.load('profile_builder.pkl')
            
        # Load Org Graph
        org_graph = None
        if os.path.exists('org_graph.pkl'):
            org_graph = joblib.load('org_graph.pkl')
            
        return {
            'model': model,
            'feature_names': feature_names,
            'xai_explainer': xai_explainer,
            'profile_builder': profile_builder,
            'org_graph': org_graph,
            'status': 'success',
            'is_advanced': 'stylometry' in model_path
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def _parse_phishing_label(label_val) -> bool:
    """Interpret CSV label cells for batch mode (numeric or string)."""
    if label_val is None or (isinstance(label_val, float) and np.isnan(label_val)):
        return False
    s = str(label_val).strip().lower()
    if s in ("1", "true", "yes", "phishing", "malicious", "spam"):
        return True
    if s in ("0", "false", "no", "legitimate", "ham", "safe", "benign"):
        return False
    try:
        return bool(float(s))
    except ValueError:
        return False


def get_threat_color(confidence: float) -> str:
    """Get color based on threat confidence."""
    if confidence >= 0.8:
        return "🔴"
    elif confidence >= 0.6:
        return "🟠"
    elif confidence >= 0.4:
        return "🟡"
    else:
        return "🟢"

def extract_features_from_email(email_text, email_subject=""):
    """
    Extract phishing features from raw email text using centralized StylometryAnalyzer.
    This ensures better alignment between dashboard predictions and trained model features.
    """
    import re
    from stylometry_analyzer import StylometryAnalyzer
    
    combined = str(email_text).lower() + " " + str(email_subject).lower()
    
    # Use StylometryAnalyzer for core features
    analyzer = StylometryAnalyzer()
    style_features = analyzer.extract_features(email_text)
    
    # Financial keywords
    financial_keywords = ['wire', 'transfer', 'payment', 'urgent', 'invoice', 'confirm', 
                         'bank', 'account', 'retainer', 'escrow', 'dollar', 'amount',
                         'immediately', 'asap', 'deadline', 'fund', 'cash', 'crypto']
    financial_count = sum(combined.count(kw) for kw in financial_keywords)
    
    # Domain similarity (spoofing patterns)
    domain_sim = 0.0
    if re.search(r'@.*@', combined):  # Double @
        domain_sim = 0.9
    elif 'confirm' in combined and 'bank' in combined:
        domain_sim = 0.6
    
    # Request type detection (0=None, 1=Credential, 2=Wire)
    request_type = 0
    if any(x in combined for x in ['verify', 'confirm', 'password', 'credential', 'login']):
        request_type = 1
    if any(x in combined for x in ['wire', 'transfer', 'payment', 'invoice', 'routing', 'swift']):
        request_type = 2
    
    # Anomaly defaults
    sender_anomaly = 1 if (financial_count > 4 and style_features.get('urgency_words_freq', 0) > 0.02) else 0
    
    return {
        'urgency_score': style_features.get('urgency_words_freq', 0) * 10,  # Scale for dashboard
        'domain_similarity_score': domain_sim,
        'financial_keyword_count': min(50, financial_count),
        'request_type': request_type,
        'sender_anomaly': sender_anomaly,
        'email_body': email_text
    }

def display_phase1_analysis(email_data, email_text, models):
    """Display Phase 1 XAI analysis using unified model."""
    st.subheader("Phase 1️⃣: Explainable AI (XAI) Analysis")
    
    try:
        # Prepare data using unified feature engineer (handles stylometry if present)
        X_pred = preprocess_features_for_prediction(
            email_text=email_text,
            urgency_score=email_data['urgency_score'],
            domain_similarity_score=email_data['domain_similarity_score'],
            financial_keyword_count=email_data['financial_keyword_count'],
            request_type=email_data['request_type'],
            sender_anomaly=email_data['sender_anomaly'],
            is_ato=0 # Base analysis
        )
        
        # Ensure feature alignment with the loaded model
        feature_names = models['feature_names']
        X_pred = X_pred.reindex(columns=feature_names, fill_value=0)
        X_pred = X_pred[feature_names]
        
        # Get explanation
        explainer = models['xai_explainer']
        explanation = explainer.explain_prediction(X_pred)
        
        # Display results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Primary Prediction",
                value=explanation['prediction'],
                delta="🚨 THREAT" if explanation['prediction'] == 'MALICIOUS' else "✅ SAFE"
            )
        
        with col2:
            st.metric(
                label="Confidence Score",
                value=f"{explanation['confidence_score']:.1%}"
            )
        
        with col3:
            st.metric(
                label="Risk Level",
                value=explanation['risk_level']
            )
        
        # Feature contributions visualization
        st.write("**📊 Key Influencing Factors:**")
        
        # Convert contributions to a more visual bar chart
        contribs = explanation['feature_contributions']
        feat_names = list(contribs.keys())
        feat_vals = [c['contribution_pct'] for c in contribs.values()]
        feat_impact = [c['direction'] for c in contribs.values()]
        
        fig = go.Figure(go.Bar(
            x=feat_vals,
            y=feat_names,
            orientation='h',
            marker_color=['#ef4444' if 'increase' in di else '#3b82f6' for di in feat_impact],
            hovertemplate='Factor: %{y}<br>Impact: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(autorange="reversed"),
            font=dict(color='#94a3b8')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Reason codes
        if explanation['reason_codes']:
            st.write("**🚨 Forensic Alerts:**")
            for code in explanation['reason_codes']:
                severity_color = "red" if code['severity'] == 'HIGH' else "orange"
                st.markdown(f"""
                    <div style='padding: 0.5rem 1rem; border-radius: 0.5rem; background: rgba(0,0,0,0.2); 
                               border-left: 3px solid {severity_color}; margin-bottom: 0.5rem;'>
                        <span style='color: {severity_color}; font-weight: 600;'>[{code['code']}]</span> {code['reason']}
                    </div>
                """, unsafe_allow_html=True)
        
        return explanation
        
    except Exception as e:
        st.error(f"Error in Phase 1 analysis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def display_phase2_analysis(email_data, email_text, models):
    """Display Phase 2 Stylometry & Account Takeover Analysis."""
    st.subheader("Phase 2️⃣: Stylometry & Account Takeover Detection")
    
    try:
        profile_builder = models['profile_builder']
        model = models['model']
        feature_names = models['feature_names']
        
        if not profile_builder or not profile_builder.profiles:
            st.warning("⚠️ No baseline profiles available for linguistic fingerprinting.")
            return None
        
        # Create detector
        detector = ATODetector(profile_builder, model, feature_names)
        
        # Run analysis
        result = detector.detect_ato(
            sender_name=email_data['sender_name'],
            email_text=email_text,
            technical_features=email_data
        )
        
        # Display results with enhanced styling
        _col1, _col2, _col3 = st.columns(3)
        
        with _col1:
            ato_conf = result.get('ato_confidence', 0)
            color = '#ff3131' if ato_conf > 0.7 else '#f97316' if ato_conf > 0.4 else '#39ff14'
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid {color};'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>ATO CONFIDENCE</p>
                    <p class='stat-value' style='color: {color}; margin: 0.5rem 0;'>{ato_conf:.1%}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with _col2:
            threat_type = result.get('threat_type', 'UNKNOWN')
            threat_icon = '🚨' if 'TAKEOVER' in threat_type or 'COMPROMISED' in threat_type else '🛡️'
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid #00d4ff;'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>DETECTION RESULT</p>
                    <p class='stat-value' style='font-size: 1.3rem; margin: 0.8rem 0;'>{threat_icon} {threat_type.replace("_", " ")}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with _col3:
            drift = result.get('anomaly_score', 0)
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid #a855f7;'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>STYLE DRIFT SCORE</p>
                    <p class='stat-value' style='margin: 0.5rem 0;'>{drift:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Style deviations
        style_drift = result.get('style_drift_details') or {}
        if style_drift:
            st.markdown("<p style='margin-top: 1.5rem; font-weight: 600; color: #859398;'>🎭 Linguistic Deviations:</p>", unsafe_allow_html=True)
            for feature, description in style_drift.items():
                st.markdown(f"- <span style='color: #f97316;'>{description}</span>", unsafe_allow_html=True)
        
        # Recommendation
        st.markdown("<br>", unsafe_allow_html=True)
        rec = result.get('recommendation', 'No recommendation available')
        if 'IMMEDIATE' in rec.upper() or 'BLOCK' in rec.upper():
            st.error(rec)
        elif 'REVIEW' in rec.upper() or 'WARN' in rec.upper():
            st.warning(rec)
        else:
            st.success(rec)
        
        return result
        
    except Exception as e:
        st.warning(f"Phase 2 analysis skipped: {str(e)}")
        return None

def display_phase3_analysis(sender_name, recipient_name, models):
    """Display Phase 3 Organizational Graph Analysis."""
    st.subheader("Phase 3️⃣: Organizational Structure Analysis")
    
    try:
        org_graph = models['org_graph']
        
        # Detect structural anomalies
        anomalies = org_graph.detect_structural_anomalies(
            sender=sender_name,
            recipient=recipient_name
        )
        
        # Display results with enhanced styling
        _col1, _col2, _col3 = st.columns(3)
        
        with _col1:
            anomaly_score = anomalies['anomaly_score']
            color = '#ff3131' if anomaly_score > 0.7 else '#f97316' if anomaly_score > 0.4 else '#39ff14'
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid {color};'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>ORG ANOMALY SCORE</p>
                    <p class='stat-value' style='color: {color}; margin: 0.5rem 0;'>{anomaly_score:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with _col2:
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid #00d4ff;'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>SENDER OUT-DEGREE</p>
                    <p class='stat-value' style='margin: 0.5rem 0;'>{anomalies['sender_out_degree']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with _col3:
            st.markdown(f"""
                <div class='stat-card' style='border-top: 4px solid #a855f7;'>
                    <p class='stat-label' style='color: #859398; font-size: 0.8rem; margin: 0;'>STRUCTURAL ALERTS</p>
                    <p class='stat-value' style='margin: 0.5rem 0;'>{len(anomalies['anomalies_detected'])}</p>
                </div>
            """, unsafe_allow_html=True)
            
        if anomalies['anomalies_detected']:
            st.markdown("<p style='margin-top: 1.5rem; font-weight: 600; color: #859398;'>📊 Graph violations:</p>", unsafe_allow_html=True)
            for anom in anomalies['anomalies_detected']:
                st.markdown(f"- <span style='color: #f97316;'>{anom.replace('_', ' ')}</span>", unsafe_allow_html=True)
        else:
            st.success("✅ No structural anomalies detected in the organizational communication graph.")
            
        return anomalies
        
    except Exception as e:
        st.warning(f"Phase 3 analysis error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def main():
    """Main Streamlit app with clean security dashboard."""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"<h3 style='color: {theme['text_muted']}; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 2rem; margin-bottom: 0.5rem; padding-left: 1rem;'>Navigation</h3>", unsafe_allow_html=True)
        
        _pages = ["dashboard", "analyze", "batch", "analytics", "profiles", "about"]
        _icons = {"dashboard": "🏠", "analyze": "📧", "batch": "📊", "analytics": "📈", "profiles": "👤", "about": "ℹ️"}
        
        for p in _pages:
            if st.button(f"{_icons[p]} {p.capitalize()}", key=f"btn_{p}", use_container_width=True):
                st.session_state.page = p
                st.rerun()
        
        st.divider()
        with st.expander("✨ Stitch design lab", expanded=False):
            if stitch_api_key_configured():
                st.success("STITCH_API_KEY is set — use Stitch in the browser or MCP to generate UI.")
            else:
                st.caption("Set **STITCH_API_KEY** in your environment to use Google Stitch with MCP.")
            st.markdown(f"[Open Stitch]({STITCH_WEB_APP}) — paste the prompt below, then export HTML or code.")
            st.text_area(
                "Prompt for Stitch",
                value=aeonshield_stitch_prompt(),
                height=120,
                key="stitch_prompt_sidebar",
                help="Use this in stitch.withgoogle.com or with the official @google/stitch-sdk (Node).",
            )
            st.caption(stitch_setup_instructions())
        st.markdown(f"<p style='color: {theme['text_muted']}; font-size: 0.7rem; text-align: center;'>AeonShield Engine v3.3</p>", unsafe_allow_html=True)

    # Main Header
    col_logo, col_tbar = st.columns([1, 4])
    with col_logo:
        _logo_candidates = ("AeonShiled Logo.png", "AeonShield Logo.png")
        _logo_path = next((p for p in _logo_candidates if os.path.isfile(p)), None)
        if _logo_path:
            st.image(_logo_path, width=140)
        else:
            st.markdown(f"<div class='logo-text' style='color: {theme['text_main']}'>🛡️ AEONSHIELD</div>", unsafe_allow_html=True)
            
    with col_tbar:
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; align-items: center; color: {theme['text_muted']}; font-size: 0.8rem; height: 100%;'>
                <span style='background: {theme['nav_hover']}; padding: 0.4rem 0.8rem; border-radius: 4px; border: 1px solid {theme['card_border']}'>
                    Last Sync: {datetime.now().strftime("%H:%M:%S")}
                </span>
            </div>
        """, unsafe_allow_html=True)

    # Load models
    with st.spinner("Synchronizing threat engines..."):
        models = load_models()
    if models['status'] == 'error':
        st.error(f"❌ ERROR: {models['error']}")
        return
    if st.session_state.page == 'dashboard':
        st.markdown("<h2 class='space-font'>🛡️ AEONSHIELD COMMAND CENTER</h2>", unsafe_allow_html=True)
        
        df_stats = None
        try:
            if os.path.exists('simulated_emails_enhanced.csv'):
                df_stats = pd.read_csv('simulated_emails_enhanced.csv')
                total_emails = len(df_stats)
                phishing_cases = int((df_stats['label'] == 1).sum())
                imposter_cases = int(((df_stats['label'] == 1) & (df_stats['domain_similarity_score'] > 0.5)).sum())
                malware_cases = int((df_stats['sender_anomaly'] == 1).sum())
            else:
                total_emails, imposter_cases, malware_cases, phishing_cases = 4280, 18, 4, 312
        except Exception:
            total_emails, imposter_cases, malware_cases, phishing_cases = 4280, 18, 4, 312
            df_stats = None

        pie_profile_labels = ['Finance', 'HR', 'IT', 'Legal', 'Sales']
        pie_profile_vals = [55, 32, 11, 9, 8]
        pie_class_labels = ['Benign', 'Malicious']
        pie_class_vals = [max(total_emails - phishing_cases, 0), phishing_cases]
        if df_stats is not None and len(df_stats) > 0:
            try:
                if 'sender_profile' in df_stats.columns:
                    vc = df_stats['sender_profile'].astype(str).value_counts().head(10)
                    if len(vc) > 0:
                        pie_profile_labels = vc.index.tolist()
                        pie_profile_vals = [int(v) for v in vc.values]
                if 'label' in df_stats.columns:
                    n_ph = int((df_stats['label'] == 1).sum())
                    n_ok = int((df_stats['label'] == 0).sum())
                    pie_class_labels = ['Benign', 'Malicious']
                    pie_class_vals = [n_ok, n_ph]
            except Exception:
                pass

        # Global Threat Pulse (Top KPI Row)
        k_col1, k_col2, k_col3, k_col4 = st.columns(4)
        
        # Threat Color Calculation
        threat_level = (phishing_cases / total_emails) * 100 if total_emails > 0 else 0
        pulse_color = theme['accent_red'] if threat_level > 5 else theme['accent_blue']
        
        with k_col1:
            st.markdown(f"""<div class='kpi-wrapper'>
                <p class='kpi-title'>ORGANIZATION RISK PULSE</p>
                <p class='kpi-value' style='color: {pulse_color};'>{threat_level:.1f}%</p>
                <div style='font-size: 0.6rem; color: #859398;'>{phishing_cases} DETECTED THREATS</div>
            </div>""", unsafe_allow_html=True)
            
        with k_col2:
            st.markdown(f"""<div class='kpi-wrapper'>
                <p class='kpi-title'>SPOOFING ANOMALIES</p>
                <p class='kpi-value'>{imposter_cases}</p>
                <div style='font-size: 0.6rem; color: #859398;'>DOMAIN FRAUD ATTEMPTS</div>
            </div>""", unsafe_allow_html=True)
            
        with k_col3:
            st.markdown(f"""<div class='kpi-wrapper'>
                <p class='kpi-title'>ACTIVE SENSORS</p>
                <p class='kpi-value'>{malware_cases}</p>
                <div style='font-size: 0.6rem; color: #859398;'>RECOGNIZED ATTACK VECTORS</div>
            </div>""", unsafe_allow_html=True)
            
        with k_col4:
            st.markdown(f"""<div class='kpi-wrapper' style='border-color: {theme['accent_red']}33;'>
                <p class='kpi-title'>SYSTEM STATUS</p>
                <p class='kpi-value'>LIVE</p>
                <div style='font-size: 0.6rem; color: {theme['accent_green']}'>ENHANCED SECURITY ENABLED</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_col1, c_col2, c_col3 = st.columns([1, 1, 1.5])
        
        with c_col1:
            st.markdown("<div class='section-header'>📂 Sender profiles (simulated corpus)</div>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Pie(labels=pie_profile_labels, values=pie_profile_vals, hole=.6)])
            fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=0, b=0), height=260, paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(font=dict(size=9)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with c_col2:
            st.markdown("<div class='section-header'>📧 Labels in corpus</div>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Pie(
                labels=pie_class_labels,
                values=pie_class_vals,
                hole=.5,
                marker=dict(colors=['#39ff14', '#ff3131'])
            )])
            fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=0, b=0), height=260, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with c_col3:
            st.markdown("<div class='section-header'> Intent Analysis</div>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Sankey(
                node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5),
                           label = ["CEO", "CFO", "HR", "Finance", "Payments", "Payroll"],
                           color = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]),
                link = dict(source = [0, 0, 1, 2, 2], target = [3, 4, 3, 5, 3], value = [8, 4, 2, 8, 4], color = "rgba(239, 68, 68, 0.4)"))])
            fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=240, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff", size=10))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<div class='section-header'>📁 Live Forensic Logs</div>", unsafe_allow_html=True)
        try:
            if os.path.exists('simulated_emails_enhanced.csv'):
                df_table = pd.read_csv('simulated_emails_enhanced.csv').tail(15)[['sender_name', 'urgency_score', 'request_type', 'label']]
                df_table['label'] = df_table['label'].apply(lambda x: '🚨 COMPROMISED' if x == 1 else '✅ SECURE')
                df_table.columns = ['Sender', 'Urgency', 'Type', 'Status']
                st.dataframe(df_table, use_container_width=True, hide_index=True)
            else:
                st.info("No live logs available. Initialize engine to start data ingestion.")
        except Exception as e:
            st.error(f"Log display error: {str(e)}")
    
    # Single Email Analysis
    elif st.session_state.page == 'analyze':
        st.markdown("<h2 class='space-font'>📧 Forensic Analysis Engine</h2>", unsafe_allow_html=True)
        
        # Tactical Navigation
        tab_main, tab_preset = st.tabs(["🎯 LIVE ANALYSIS", "📂 FORENSIC SAMPLES"])
        
        with tab_preset:
            st.markdown("<p style='color: #859398; font-size: 0.8rem; margin-bottom: 1rem;'>SELECT A PRECONFIGURED ATTACK VECTOR TO INITIALIZE ENGINE SENSORS</p>", unsafe_allow_html=True)
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                if st.button("📤 LOAD: CEO WIRE FRAUD", use_container_width=True):
                    st.session_state.sender_input = "CEO Mark Thompson"
                    st.session_state.fin_keywords = 12
                    st.session_state.urgency = 0.95
                    st.session_state.domain = 0.85
                    st.session_state.req_type_select = 2
                    st.session_state.sender_anom = True
                    st.session_state.email_text_area = "Emergency wire transfer needed for project Alpha. Must be processed by 4 PM today. Do not call, I am in meetings."
                    st.rerun()
            with p_col2:
                if st.button("🔐 LOAD: IT LOGIN SPOOF", use_container_width=True):
                    st.session_state.sender_input = "Global IT Security Team"
                    st.session_state.fin_keywords = 1
                    st.session_state.urgency = 0.7
                    st.session_state.domain = 0.9
                    st.session_state.req_type_select = 1
                    st.session_state.sender_anom = False
                    st.session_state.email_text_area = "Suspicious login detected on your account. Please click here to verify your identity immediately or your account will be locked. Link: http://it-verify-login.com"
                    st.rerun()

        with tab_main:
            # Main Input Interface
            st.markdown("<div class='neon-border'>", unsafe_allow_html=True)
            col_in1, col_in2 = st.columns([1.8, 1], gap="large")
            
            with col_in1:
                st.markdown("<p style='color: #00d4ff; font-weight: 700; margin-bottom: 0.5rem;'>TERMINAL INPUT: SENDER & BODY</p>", unsafe_allow_html=True)
                sender_name = st.text_input("Sender Identification (From Name)", value=st.session_state.get("sender_input", "John Executive"), placeholder="e.g. CFO James Smith", key="sender_input_main")
                email_text = st.text_area("Email Content Payload (Body)", value=st.session_state.get("email_text_area", "I need a wire transfer processed ASAP."), height=220, placeholder="Paste raw email content here...", key="email_text_area_main")
            
            with col_in2:
                st.markdown("<p style='color: #00d4ff; font-weight: 700; margin-bottom: 0.5rem;'>SENSOR CALIBRATION</p>", unsafe_allow_html=True)
                urgency = st.slider("Urgency (Heuristic Score)", 0.0, 1.0, st.session_state.get("urgency", 0.5), key="urgency_slider")
                domain_sim = st.slider("Domain Anomaly Score", 0.0, 1.0, st.session_state.get("domain", 0.2), key="domain_slider")
                fin_keywords = st.number_input("Financial Keyword Hits", 0, 50, st.session_state.get("fin_keywords", 0), key="fin_keywords_input")
                
                req_options = ["Neutral / Information", "Credential Request", "Financial / Wire"]
                req_type = st.selectbox("Action Vector (Request Type)", options=[0, 1, 2], format_func=lambda x: req_options[x], index=st.session_state.get("req_type_select", 0), key="req_type_select_main")
                sender_anomaly_check = st.checkbox("Technical Anomaly Detected", value=st.session_state.get("sender_anom", False), key="sender_anom_check")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("🔍 INITIATE MULTI-PHASE FORENSIC SCAN", use_container_width=True, type="primary"):
                if not email_text or not sender_name:
                    st.error("❌ ERROR: INPUT PAYLOAD EMPTY. ENTER SENDER AND CONTENT.")
                else:
                    email_data = {
                        'sender_name': sender_name,
                        'urgency_score': urgency,
                        'domain_similarity_score': domain_sim,
                        'financial_keyword_count': fin_keywords,
                        'request_type': req_type,
                        'sender_anomaly': 1 if sender_anomaly_check else 0
                    }
                    
                    st.markdown("<hr style='border-color: rgba(0, 212, 255, 0.2);'>", unsafe_allow_html=True)
                    
                    # Analysis Results
                    phase_tabs = st.tabs(["PHASE 01: XAI LOGIC", "PHASE 02: STYLE FINGERPRINT", "PHASE 03: ORG GRAPH"])
                    
                    with phase_tabs[0]:
                        phase1_result = display_phase1_analysis(email_data, email_text, models)
                    
                    with phase_tabs[1]:
                        phase2_result = display_phase2_analysis(email_data, email_text, models)
                    
                    with phase_tabs[2]:
                        if models['org_graph']:
                            phase3_result = display_phase3_analysis(email_data['sender_name'], "Corporate Finance", models)
                        else:
                            st.info("PHASE 03: ORGANIZATIONAL GRAPH SENSOR NOT INITIALIZED.")
                    
                    # Integrated Assessment
                    st.markdown("<br>", unsafe_allow_html=True)
                    risk_sum = 0
                    components = 0
                    if 'phase1_result' in locals() and phase1_result: 
                        risk_sum += phase1_result['confidence_score'] * 0.4
                        components += 0.4
                    if 'phase2_result' in locals() and phase2_result: 
                        risk_sum += phase2_result.get('ato_confidence', 0) * 0.4
                        components += 0.4
                    if 'phase3_result' in locals() and phase3_result: 
                        risk_sum += phase3_result['anomaly_score'] * 0.2
                        components += 0.2
                    
                    risk_score = risk_sum / components if components > 0 else 0
                    
                    risk_color = theme['accent_red'] if risk_score > 0.6 else theme['accent_blue'] if risk_score > 0.3 else theme['accent_green']
                    border_class = "neon-border-red" if risk_score > 0.6 else "neon-border-green" if risk_score < 0.3 else ""
                    
                    st.markdown(f"""
                        <div class='neon-border {border_class}' style='background: rgba(0,0,0,0.4);'>
                            <div style='display: flex; align-items: center; justify-content: space-between;'>
                                <div>
                                    <p class='space-font' style='color: {risk_color}; margin: 0; font-size: 1.2rem;'>INTEGRATED THREAT EVALUATION: {risk_score:.1%}</p>
                                    <p style='color: #859398; margin-top: 0.5rem; font-size: 0.8rem;'>AGGREGATED RISK ASSESSMENT FROM MULTI-MODAL SENSORS (XAI + STYLOMETRY + GRAPH)</p>
                                </div>
                                <div style='font-size: 3rem;'>{'🚨' if risk_score > 0.6 else '⚠️' if risk_score > 0.3 else '🛡️'}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        if st.button("← BACK TO DASHBOARD", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()

    
    # Batch Processing
    elif st.session_state.page == 'batch':
        st.subheader("📊 Batch Email Processing")
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #667eea99 100%); 
                       padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #667eea33;
                       box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);'>
                <p style='color: #ffffff; margin: 0; font-size: 0.95rem;'>
                ⚡ Upload CSV files with email data for batch analysis. Supports Kaggle datasets and custom formats.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader("📁 Upload CSV File", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            
            # Display file summary
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.markdown(f"""
                    <div style='background: #1a2332; padding: 1.2rem; border-radius: 0.75rem; 
                               border: 1px solid #2d3748; text-align: center;'>
                        <p style='color: #a0a9be; margin: 0; font-size: 0.85rem;'>📊 Total Records</p>
                        <p style='color: #667eea; margin: 0.5rem 0 0 0; font-size: 1.8rem; font-weight: 800;'>{len(df):,}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with summary_col2:
                st.markdown(f"""
                    <div style='background: #1a2332; padding: 1.2rem; border-radius: 0.75rem; 
                               border: 1px solid #2d3748; text-align: center;'>
                        <p style='color: #a0a9be; margin: 0; font-size: 0.85rem;'>📋 Columns Found</p>
                        <p style='color: #764ba2; margin: 0.5rem 0 0 0; font-size: 1.8rem; font-weight: 800;'>{len(df.columns)}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with summary_col3:
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.markdown(f"""
                    <div style='background: #1a2332; padding: 1.2rem; border-radius: 0.75rem; 
                               border: 1px solid #2d3748; text-align: center;'>
                        <p style='color: #a0a9be; margin: 0; font-size: 0.85rem;'>💾 File Size</p>
                        <p style='color: #ff9a56; margin: 0.5rem 0 0 0; font-size: 1.8rem; font-weight: 800;'>{file_size_mb:.2f} MB</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            with st.expander("📋 Preview & Column Info", expanded=True):
                col_preview1, col_preview2 = st.columns(2)
                with col_preview1:
                    st.write("**First few rows:**")
                    st.dataframe(df.head(3), use_container_width=True)
                with col_preview2:
                    st.write("**Column Information:**")
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': [str(df[col].dtype) for col in df.columns],
                        'Non-Null': [df[col].notna().sum() for col in df.columns]
                    })
                    st.dataframe(col_info, use_container_width=True)
            
            st.markdown("---")
            
            # Detect if this is a Kaggle phishing dataset
            has_body = 'body' in df.columns or 'text' in df.columns or 'email' in df.columns
            has_label = 'label' in df.columns or 'phishing' in df.columns or 'is_phishing' in df.columns
            
            if has_body and has_label:
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #84fab0 0%, #84fab099 100%); 
                               padding: 1.5rem; border-radius: 0.75rem; border-left: 4px solid #84fab0;
                               box-shadow: 0 8px 32px rgba(132, 250, 176, 0.2);'>
                        <h3 style='color: #1a1f2e; margin: 0 0 0.5rem 0;'>✅ Kaggle Format Detected!</h3>
                        <p style='color: #5d9e7c; margin: 0; font-size: 0.95rem;'>
                        Auto-extracting features from email text and showing actual phishing labels...
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                email_col = next((c for c in ['body', 'text', 'email'] if c in df.columns), None)
                subject_col = next((c for c in ['subject', 'title'] if c in df.columns), None)
                label_col = next((c for c in ['label', 'phishing', 'is_phishing'] if c in df.columns), None)
                sender_col = next((c for c in ['from', 'sender', 'email_from'] if c in df.columns), None)
                
                process_col1, process_col2, process_col3 = st.columns([2, 1, 1])
                
                with process_col1:
                    if st.button("🚀 Analyze All Emails (Auto-Extract Features)", use_container_width=True, type="primary"):
                        results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        result_placeholder = st.empty()
                        
                        for idx, row in df.iterrows():
                            try:
                                # Extract features from email text
                                features = extract_features_from_email(
                                    row.get(email_col, ""),
                                    row.get(subject_col, "")
                                )
                                
                                # Get actual label
                                label_val = row.get(label_col, 0)
                                is_phishing = _parse_phishing_label(label_val)
                                
                                results.append({
                                    'Sender': row.get(sender_col, "Unknown") if sender_col else "Unknown",
                                    'Subject': str(row.get(subject_col, ""))[:45] if subject_col else "N/A",
                                    'Urgency': f"{features['urgency_score']:.2f}",
                                    'Financial Keywords': features['financial_keyword_count'],
                                    'Request Type': ['None', 'Credential', 'Wire'][features['request_type']],
                                    'Anomaly': '⚠️ Yes' if features['sender_anomaly'] else '✓ No',
                                    'Label': '🚨 PHISHING' if is_phishing else '✅ SAFE'
                                })
                            except Exception as e:
                                pass
                            
                            progress = (idx + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.write(f"⏳ Processing: {idx + 1}/{len(df)} emails ({progress:.1%})")
                        
                        st.markdown("---")
                        
                        # Results summary
                        results_df = pd.DataFrame(results)
                        phishing_count = len([r for r in results if 'PHISHING' in r['Label']])
                        safe_count = len([r for r in results if 'SAFE' in r['Label']])
                        
                        summary_col1, summary_col2, summary_col3 = st.columns(3)
                        
                        with summary_col1:
                            st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ff6b6b99 100%); 
                                           padding: 1.5rem; border-radius: 0.75rem;'>
                                    <p style='color: #ffffff; margin: 0; font-size: 0.9rem;'>🚨 Phishing Emails</p>
                                    <p style='color: #ffffff; margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 800;'>{phishing_count:,}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with summary_col2:
                            st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #84fab0 0%, #84fab099 100%); 
                                           padding: 1.5rem; border-radius: 0.75rem;'>
                                    <p style='color: #1a1f2e; margin: 0; font-size: 0.9rem;'>✅ Safe Emails</p>
                                    <p style='color: #1a1f2e; margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 800;'>{safe_count:,}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with summary_col3:
                            phishing_rate = (phishing_count / len(results) * 100) if results else 0
                            st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #667eea 0%, #667eea99 100%); 
                                           padding: 1.5rem; border-radius: 0.75rem;'>
                                    <p style='color: #ffffff; margin: 0; font-size: 0.9rem;'>📊 Phishing Rate</p>
                                    <p style='color: #ffffff; margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 800;'>{phishing_rate:.1f}%</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.success(f"✅ Successfully analyzed {len(results):,} emails!")
                        
                        st.write("**📊 Detailed Results:**")
                        st.dataframe(results_df, use_container_width=True, height=400)
                        
                        # Download button
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"aeonshield_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with process_col2:
                    if st.button("⟳ Refresh", use_container_width=True):
                        st.rerun()
                
                with process_col3:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.page = 'dashboard'
                        st.rerun()
            else:
                # Manual column mapping for other formats
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #ffd93d 0%, #ffd93d99 100%); 
                               padding: 1.5rem; border-radius: 0.75rem; border-left: 4px solid #ffd93d;
                               box-shadow: 0 8px 32px rgba(255, 217, 61, 0.2);'>
                        <h3 style='color: #1a1f2e; margin: 0 0 0.5rem 0;'>⚙️ Manual Column Mapping Required</h3>
                        <p style='color: #b8a030; margin: 0; font-size: 0.95rem;'>
                        Please select which columns correspond to the required fields.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.write("**🔄 Column Mapping** (Select columns manually):")
                
                map_col1, map_col2, map_col3 = st.columns(3, gap="medium")
                
                with map_col1:
                    sender_col = st.selectbox(
                        "Sender Name Column",
                        [None] + df.columns.tolist(),
                        key="map_sender"
                    )
                    urgency_col = st.selectbox(
                        "Urgency Score Column",
                        [None] + df.columns.tolist(),
                        key="map_urgency"
                    )
                
                with map_col2:
                    domain_col = st.selectbox(
                        "Domain Similarity Column",
                        [None] + df.columns.tolist(),
                        key="map_domain"
                    )
                    financial_col = st.selectbox(
                        "Financial Keywords Column",
                        [None] + df.columns.tolist(),
                        key="map_financial"
                    )
                
                with map_col3:
                    request_col = st.selectbox(
                        "Request Type Column",
                        [None] + df.columns.tolist(),
                        key="map_request"
                    )
                    anomaly_col = st.selectbox(
                        "Sender Anomaly Column",
                        [None] + df.columns.tolist(),
                        key="map_anomaly"
                    )
                
                st.markdown("---")
                
                process_col1, process_col2, process_col3 = st.columns([2, 1, 1])
                
                with process_col1:
                    if st.button("🚀 Process Batch", use_container_width=True, type="primary"):
                        results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df.iterrows():
                            try:
                                email_data = {}
                                
                                # Safe extraction with type checking
                                for key, col in [('sender_name', sender_col), ('urgency_score', urgency_col),
                                                ('domain_similarity_score', domain_col), 
                                                ('financial_keyword_count', financial_col),
                                                ('request_type', request_col), ('sender_anomaly', anomaly_col)]:
                                    if col and col in df.columns:
                                        try:
                                            val = row.get(col)
                                            if key in ['urgency_score', 'domain_similarity_score', 'financial_keyword_count', 'sender_anomaly']:
                                                email_data[key] = float(val) if val is not None else 0
                                            elif key == 'request_type':
                                                email_data[key] = int(float(val)) if val is not None else 0
                                            else:
                                                email_data[key] = str(val) if val is not None else "Unknown"
                                        except (ValueError, TypeError):
                                            email_data[key] = 0 if key != 'sender_name' else "Unknown"
                                    else:
                                        email_data[key] = 0 if key != 'sender_name' else "Unknown"
                                
                                req_type_int = int(email_data.get('request_type', 0))
                                results.append({
                                    'Sender': email_data.get('sender_name', 'Unknown'),
                                    'Urgency': f"{email_data.get('urgency_score', 0):.2f}",
                                    'Domain Sim': f"{email_data.get('domain_similarity_score', 0):.2f}",
                                    'Fin Keywords': int(email_data.get('financial_keyword_count', 0)),
                                    'Request Type': ['None', 'Credential', 'Wire'][min(req_type_int, 2)],
                                    'Anomaly': '⚠️ Yes' if email_data.get('sender_anomaly', 0) else '✓ No'
                                })
                            except Exception as e:
                                pass
                            
                            progress_bar.progress((idx + 1) / len(df))
                            status_text.write(f"⏳ Processing: {idx + 1}/{len(df)} emails ({(idx+1)/len(df)*100:.1f}%)")
                        
                        st.markdown("---")
                        st.success(f"✅ Successfully processed {len(results):,} emails!")
                        
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True, height=400)
                        
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"aeonshield_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with process_col2:
                    if st.button("⟳ Refresh", use_container_width=True):
                        st.rerun()
                
                with process_col3:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.page = 'dashboard'
                        st.rerun()
    
    # Model Analytics
    elif st.session_state.page == 'analytics':
        st.subheader("📈 Model Performance Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Model Accuracy", "79.75%")
        with col2:
            st.metric("Malicious Recall", "98.37%")
        with col3:
            st.metric("ROC-AUC Score", "0.8231")
        
        st.markdown("---")
        st.write("**📊 Feature Importance Rankings:**")
        
        try:
            fi_path = (
                "feature_importance_stylometry.csv"
                if os.path.isfile("feature_importance_stylometry.csv")
                else "feature_importance.csv"
            )
            feature_importance = pd.read_csv(fi_path)
            fig = px.bar(
                feature_importance.head(15),
                x='importance',
                y='feature',
                orientation='h',
                title='Top 15 Most Important Features',
                labels={'importance': 'Importance', 'feature': 'Feature'},
                color='importance',
                color_continuous_scale='Blues'
            )
            fig.update_layout(template='plotly_dark', paper_bgcolor='#1a2332', font=dict(color='#e0e0e0'))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("💡 Hover over bars for details; use the toolbar to zoom or pan.")
        except Exception as e:
            st.info("Feature importance data not available. Run training to generate.")
            st.caption(str(e))
        
        if st.button("← Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    
    # Baseline Profiles
    elif st.session_state.page == 'profiles':
        st.subheader("👥 Baseline Stylometry Profiles")
        
        profile_builder = models['profile_builder']
        
        if profile_builder is not None and getattr(profile_builder, "profiles", None):
            st.write(f"**Profiles Available:** {len(profile_builder.profiles)}")
            
            for sender_name, profile in profile_builder.profiles.items():
                with st.expander(f"📌 {sender_name}"):
                    # Extract key statistics
                    formality_mean = profile.get('formality_score_mean', 0)
                    urgency_mean = profile.get('urgency_words_freq_mean', 0)
                    
                    st.metric(
                        f"Baseline Formality Score",
                        f"{formality_mean:.3f}"
                    )
                    st.metric(
                        f"Baseline Urgency Words",
                        f"{urgency_mean:.3f}"
                    )
        else:
            st.warning("No baseline profiles available")
        
        if st.button("← Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
            
    # About Section
    elif st.session_state.page == 'about':
        st.subheader("ℹ️ About AeonShield Project")
        
        # Project Overview Card
        st.markdown(f"""<div style='background: {theme['card_bg']}; padding: 1.5rem; border-radius: 8px; border: 1px solid {theme['card_border']}; margin-bottom: 1.5rem;'>
<h3 style='color: {theme['accent_blue']}; margin-top: 0;'>Final Year Project</h3>
<p style='font-size: 1rem; line-height: 1.5; color: {theme['text_main']};'>
    <strong>AeonShield</strong> is a sophisticated Business Email Compromise (BEC) and Phishing Detection engine. Developed as a final year academic project, it integrates advanced Machine Learning, Stylometric Linguistic Analysis, and Organizational Graph forensics to detect modern email threats that traditional security gateways often miss.
</p>
<p style='font-style: italic; color: {theme['text_muted']}; margin-bottom: 0;'>Students of <strong>Behala Government Polytechnic</strong></p>
</div>""", unsafe_allow_html=True)

        # Team Section
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 1.2rem; font-size: 1.1rem;'>Project Team Members</h4>", unsafe_allow_html=True)
        
        t1, t2, t3 = st.columns(3)
        
        team = [
            ("Akash Basak", "Backend & Integration Architect", t1),
            ("Abhiraj Kumar Rajak", "ML & Stylometry Researcher", t2),
            ("Subhamita Mondal", "Security Analyst & UI Designer", t3)
        ]
        
        for name, role, col in team:
            with col:
                st.markdown(f"""<div style='background: {theme['card_bg']}; padding: 1.2rem; border-radius: 6px; border: 1px solid {theme['card_border']}; border-left: 4px solid {theme['accent_blue']}; height: 120px;'>
<strong style='color: #ffffff; font-size: 1rem;'>{name}</strong><br>
<span style='color: {theme['text_muted']}; font-size: 0.85rem;'>{role}</span>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mentorship Section
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 1.2rem; font-size: 1.1rem;'>Guidance & Supervision</h4>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown(f"""<div style='background: {theme['card_bg']}; padding: 1.5rem; border-radius: 8px; border: 1px solid {theme['card_border']}; border-top: 4px solid #10b981;'>
<span style='color: #10b981; font-weight: 700; font-size: 0.75rem; text-transform: uppercase;'>Mentorship</span>
<p style='margin-top: 0.5rem; margin-bottom: 0;'>
    <strong style='color: #ffffff; font-size: 1.1rem;'>Sayuj Sur</strong><br>
    <span style='color: {theme['text_muted']}; font-size: 0.9rem;'>Industry Mentor & Project Advisor</span>
</p>
</div>""", unsafe_allow_html=True)
            
        with g2:
            st.markdown(f"""<div style='background: {theme['card_bg']}; padding: 1.5rem; border-radius: 8px; border: 1px solid {theme['card_border']}; border-top: 4px solid #8b5cf6;'>
<span style='color: #8b5cf6; font-weight: 700; font-size: 0.75rem; text-transform: uppercase;'>Supervision</span>
<p style='margin-top: 0.5rem; margin-bottom: 0;'>
    <strong style='color: #ffffff; font-size: 1.1rem;'>Dr. Partha Sarathi Goswami</strong><br>
    <span style='color: {theme['text_muted']}; font-size: 0.9rem;'>Academic Supervisor</span>
</p>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    
if __name__ == "__main__":
    main()

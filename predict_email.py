import pandas as pd
import joblib
from ato_detector import analyze_incoming_email_for_ato, generate_ato_report
from org_graph_analyzer import OrganizationalGraph

def predict_new_email_modern(sender_name, email_text, urgency, domain_sim, fin_keywords, req_type, sender_anom):
    """
    Modern prediction script that uses the full 3nd-generation detection architecture.
    Integrates Phase 1 (XAI) and Phase 2 (Stylometry/ATO).
    """
    print("\n" + "="*75)
    print("🛡️  AeonShield: Unified BEC Threat Analysis (CLI)")
    print("="*75)
    
    # 1. Run Phase 1 & 2 Analysis
    print(f"\n📨 Analyzing email from: {sender_name}...")
    
    result = analyze_incoming_email_for_ato(
        sender_name=sender_name,
        email_text=email_text,
        urgency_score=urgency,
        domain_similarity_score=domain_sim,
        financial_keyword_count=fin_keywords,
        request_type=req_type,
        sender_anomaly=int(sender_anom)
    )
    
    # 2. Display Phase 1 & 2 Report
    print(generate_ato_report(result))
    
    # 3. Optional: Add Phase 3 (Organizational Graph) Analysis if graph exists
    try:
        org_graph = joblib.load('org_graph.pkl')
        anomalies = org_graph.detect_structural_anomalies(sender_name, 'Finance Department')
        
        print("\n" + "-"*75)
        print("🔗 PHASE 3: ORGANIZATIONAL GRAPH ANALYSIS")
        print("-"*75)
        print(f"   Structural Anomaly Score: {anomalies['anomaly_score']:.2f}")
        
        if anomalies['anomalies_detected']:
            print(f"   🚩 Anomalies: {', '.join(anomalies['anomalies_detected'])}")
        else:
            print("   ✅ No structural anomalies detected")
        print("-"*75)
    except FileNotFoundError:
        print("\n⚠️ Phase 3 Graph ('org_graph.pkl') not found. Skipping Phase 3 analysis.")
    except Exception as e:
        print(f"\n⚠️ Phase 3 error: {e}")

if __name__ == '__main__':
    # --- SIMULATE A HIGH-RISK INCOMING EMAIL ---
    # Testing a suspicious email that mimics an Account Takeover attempt
    
    ceo_spoof_email = """Hi finance team,
    
    I'm out of the office today but need a $250,000 wire transfer processed ASAP to our new retainer account. 
    
    Details: Acct ****5678. 
    
    Confirm as soon as this is done!!! ASAP!!!"""
    
    predict_new_email_modern(
        sender_name="John Executive",  # CEO name used in simulations
        email_text=ceo_spoof_email,
        urgency=0.95,
        domain_sim=0.0,            # High spoofing (same name, potentially same domain)
        fin_keywords=5,
        req_type=2,                # Wire Transfer
        sender_anom=False          # It's a "known" sender, but style is off!
    )
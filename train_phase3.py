"""
Phase 3 Training: Build Organizational Graph and Integrate All Phases
"""

import pandas as pd
import joblib
from org_graph_analyzer import build_org_graph_from_data
from data_simulator_enhanced import generate_bec_data_enhanced

def train_phase3():
    print("="*75)
    print("📊 PHASE 3: ORGANIZATIONAL GRAPH CONSTRUCTION")
    print("="*75)
    print()
    
    # 1. Load or generate data
    print("📦 Loading data...")
    try:
        df = pd.read_csv('simulated_emails_enhanced.csv')
        print(f"✅ Loaded {len(df)} emails from simulated_emails_enhanced.csv")
    except FileNotFoundError:
        print("⚠️  Dataset not found. Generating new dataset...")
        df, _ = generate_bec_data_enhanced(n_samples=2000)
        df.to_csv('simulated_emails_enhanced.csv', index=False)
        print(f"✅ Generated {len(df)} emails")
    
    # 2. Build organizational graph
    print("\n🔗 Building organizational graph...")
    org_graph = build_org_graph_from_data(df)
    
    graph_stats = org_graph.get_graph_stats()
    print(f"✅ Graph constructed:")
    print(f"   - Nodes (people): {graph_stats['total_nodes']}")
    print(f"   - Edges (communications): {graph_stats['total_edges']}")
    print(f"   - Average degree: {graph_stats['avg_degree']:.2f}")
    print(f"   - Graph density: {graph_stats['density']:.4f}")
    print(f"   - Connected components: {graph_stats['num_components']}")
    
    # 3. Save graph
    print("\n💾 Saving organizational graph...")
    joblib.dump(org_graph, 'org_graph.pkl')
    print("✅ Graph saved to 'org_graph.pkl'")
    
    # 4. Test anomaly detection
    print("\n🔍 Testing structural anomaly detection...")
    
    test_cases = [
        ('John Executive', 'Finance Department'),
        ('Jane Manager', 'Finance Department'),
        ('Bob Finance', 'Finance Department'),
    ]
    
    for sender, recipient in test_cases:
        result = org_graph.detect_structural_anomalies(sender, recipient)
        print(f"\n   📧 {sender} → {recipient}")
        print(f"      Anomaly Score: {result['anomaly_score']:.2f}")
        print(f"      Anomalies: {result['anomalies_detected']}")
    
    # 5. Integration summary
    print("\n" + "="*75)
    print("✨ PHASE 3 COMPLETE - ALL PHASES INTEGRATED")
    print("="*75)
    print()
    print("📊 Integrated Capabilities:")
    print("   ✅ Phase 1: XAI Explanations (SHAP-based)")
    print("   ✅ Phase 2: Stylometry & ATO Detection (17 linguistic features)")
    print("   ✅ Phase 3: Organizational Graph Analysis (structural anomalies)")
    print()
    print("🎯 Ready to Launch Dashboard:")
    print("   Run: streamlit run dashboard.py")
    print()

if __name__ == "__main__":
    train_phase3()

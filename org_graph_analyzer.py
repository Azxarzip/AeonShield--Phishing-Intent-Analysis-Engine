
import networkx as nx
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
import joblib

class OrganizationalGraph:
    """Build and analyze organizational communication graph."""
    
    def __init__(self):
        """Initialize organizational graph."""
        self.graph = nx.DiGraph()  # Directed graph for "sender -> recipient"
        self.sender_history = defaultdict(set)  # sender -> set of recipients
        self.recipient_history = defaultdict(set)  # recipient -> set of senders
        self.communication_counts = defaultdict(int)  # (sender, recipient) -> count
        self.hierarchy = {}  # sender -> role/level
        self.departments = {}  # sender -> department
        
    def add_communication(self, sender: str, recipient: str, weight: float = 1.0, 
                         role: str = None, department: str = None):
        """
        Add a communication edge to the graph.
        
        Args:
            sender: Email sender
            recipient: Email recipient
            weight: Edge weight (frequency or importance)
            role: Role of sender (CEO, Manager, Employee)
            department: Department of sender (Finance, HR, etc.)
        """
        # Add nodes with attributes
        if not self.graph.has_node(sender):
            self.graph.add_node(sender, role=role, department=department, 
                               communication_count=0, contacted_count=0)
        if not self.graph.has_node(recipient):
            self.graph.add_node(recipient, role=None, department=None,
                               communication_count=0, contacted_count=0)
        
        # Add edge or update weight
        if self.graph.has_edge(sender, recipient):
            self.graph[sender][recipient]['weight'] += weight
        else:
            self.graph.add_edge(sender, recipient, weight=weight)
        
        # Track history
        self.sender_history[sender].add(recipient)
        self.recipient_history[recipient].add(sender)
        self.communication_counts[(sender, recipient)] += 1
        
        # Update node attributes
        self.graph.nodes[sender]['communication_count'] += 1
        self.graph.nodes[recipient]['contacted_count'] += 1
        
        # Store hierarchy
        if role:
            self.hierarchy[sender] = role
        if department:
            self.departments[sender] = department
    
    def detect_structural_anomalies(self, sender: str, recipient: str) -> Dict:
        """
        Detect if a communication from sender to recipient is structurally anomalous.
        
        Scenarios:
        - CEO emails junior employee for first time (unusual span of control)
        - Employee emails executive they've never contacted
        - Cross-department communication from unlikely person
        - Outlier in communication pattern
        
        Args:
            sender: Email sender
            recipient: Email recipient
            
        Returns:
            Dictionary with anomaly scores
        """
        anomaly_score = 0.0
        anomalies_detected = []
        
        # 1. Check if this is a first-time communication
        if sender in self.graph and recipient not in self.sender_history.get(sender, set()):
            anomaly_score += 0.2
            anomalies_detected.append("FIRST_CONTACT")
        
        # 2. Check organizational hierarchy violation
        sender_role = self.hierarchy.get(sender, "Unknown")
        recipient_role = self.hierarchy.get(recipient, "Unknown")
        
        hierarchy_map = {"CEO": 3, "Manager": 2, "Employee": 1, "Unknown": 0}
        sender_level = hierarchy_map.get(sender_role, 0)
        recipient_level = hierarchy_map.get(recipient_role, 0)
        
        # CEO directly emailing junior employee (bypassing managers)
        if sender_level == 3 and recipient_level == 1:
            anomaly_score += 0.15
            anomalies_detected.append("HIERARCHY_BYPASS")
        
        # 3. Check communication degree (how many people does sender typically contact?)
        if sender in self.graph:
            out_degree = self.graph.out_degree(sender)
            in_degree = self.graph.in_degree(sender)
            
            # Unusual outbound: person suddenly contacting many new people
            avg_contacts = np.mean([d for s, d in self.graph.out_degree()])
            if out_degree > avg_contacts * 2:
                anomaly_score += 0.1
                anomalies_detected.append("HIGH_COMMUNICATION_DEGREE")
        
        # 4. Check department cross-over
        sender_dept = self.departments.get(sender, "Unknown")
        recipient_dept = self.departments.get(recipient, "Unknown")
        
        if sender_dept and recipient_dept and sender_dept != recipient_dept:
            # Check if this person typically crosses departments
            dept_crossings = sum(
                1 for s, r in self.communication_counts.keys()
                if s == sender and 
                   self.departments.get(r) != sender_dept
            )
            total_contacts = self.communication_counts.get((sender, recipient), 0)
            
            if dept_crossings == 0:  # Never crossed departments before
                anomaly_score += 0.15
                anomalies_detected.append("UNUSUAL_DEPT_CROSSING")
        
        # 5. Check betweenness centrality (person in middle of graph)
        if len(self.graph) > 2:
            try:
                centrality = nx.betweenness_centrality(self.graph)
                sender_centrality = centrality.get(sender, 0)
                avg_centrality = np.mean(list(centrality.values()))
                
                # If low centrality but suddenly sending to high-centrality person
                if sender_centrality < avg_centrality * 0.5:
                    recipient_centrality = centrality.get(recipient, 0)
                    if recipient_centrality > avg_centrality * 1.5:
                        anomaly_score += 0.1
                        anomalies_detected.append("UNUSUAL_TARGET_CONTACT")
            except Exception:
                pass
        
        return {
            'sender': sender,
            'recipient': recipient,
            'anomaly_score': float(np.clip(anomaly_score, 0, 1)),
            'anomalies_detected': anomalies_detected,
            'sender_role': sender_role,
            'recipient_role': recipient_role,
            'sender_dept': sender_dept,
            'recipient_dept': recipient_dept,
            'sender_out_degree': self.graph.out_degree(sender) if sender in self.graph else 0,
            'recipient_in_degree': self.graph.in_degree(recipient) if recipient in self.graph else 0
        }
    
    def get_graph_stats(self) -> Dict:
        """Get overall graph statistics."""
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'avg_degree': np.mean([d for n, d in self.graph.degree()]) if self.graph.number_of_nodes() > 0 else 0,
            'density': nx.density(self.graph),
            'num_components': nx.number_weakly_connected_components(self.graph)
        }
    
    def get_node_importance(self, node: str) -> Dict:
        """Calculate importance scores for a node."""
        if node not in self.graph:
            return {'error': 'Node not found'}
        
        try:
            centrality = nx.betweenness_centrality(self.graph)
            degree_centrality = nx.degree_centrality(self.graph)
            closeness_centrality = nx.closeness_centrality(self.graph)
            
            return {
                'betweenness': float(centrality.get(node, 0)),
                'degree': float(degree_centrality.get(node, 0)),
                'closeness': float(closeness_centrality.get(node, 0)),
                'out_degree': self.graph.out_degree(node),
                'in_degree': self.graph.in_degree(node)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary for serialization."""
        return {
            'nodes': [
                {
                    'id': node,
                    'role': self.graph.nodes[node].get('role'),
                    'department': self.graph.nodes[node].get('department'),
                    'out_degree': self.graph.out_degree(node),
                    'in_degree': self.graph.in_degree(node)
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    'weight': self.graph[u][v].get('weight', 1.0)
                }
                for u, v in self.graph.edges()
            ],
            'stats': self.get_graph_stats()
        }


def build_org_graph_from_data(df: pd.DataFrame) -> OrganizationalGraph:
    """
    Build organizational graph from email dataset.
    
    Args:
        df: DataFrame with sender, recipient, and organizational info
        
    Returns:
        OrganizationalGraph object
    """
    graph = OrganizationalGraph()
    
    # Assign roles based on sender_profile
    role_map = {
        'CEO_Formal': 'CEO',
        'Manager_Casual': 'Manager',
        'Attacker_Generic': 'Unknown',
        'ATO_Compromised': 'Employee'
    }
    
    dept_map = {
        'John Executive': 'Executive',
        'Jane Manager': 'Finance',
        'Bob Finance': 'Finance'
    }
    
    # Add communications
    for idx, row in df.iterrows():
        sender = row.get('sender_name', 'Unknown')
        recipient = 'Finance Department'  # Default recipient
        
        role = role_map.get(row.get('sender_profile'), 'Employee')
        dept = dept_map.get(sender, 'Operations')
        
        graph.add_communication(
            sender=sender,
            recipient=recipient,
            weight=1.0,
            role=role,
            department=dept
        )
    
    return graph


if __name__ == '__main__':
    # Example usage
    from data_simulator_enhanced import generate_bec_data_enhanced
    
    print("Building organizational graph...")
    df, _ = generate_bec_data_enhanced(n_samples=500)
    graph = build_org_graph_from_data(df)
    
    print(f"✅ Graph created with {graph.graph.number_of_nodes()} nodes, {graph.graph.number_of_edges()} edges")
    
    # Detect anomalies for sample communication
    anomalies = graph.detect_structural_anomalies('John Executive', 'Finance Department')
    print(f"\n📊 Anomaly Detection Sample:")
    print(f"  Sender: {anomalies['sender']}")
    print(f"  Recipient: {anomalies['recipient']}")
    print(f"  Anomaly Score: {anomalies['anomaly_score']:.2f}")
    print(f"  Detected Anomalies: {anomalies['anomalies_detected']}")
    
    # Save graph
    joblib.dump(graph, 'org_graph.pkl')
    print(f"\n✅ Graph saved to org_graph.pkl")

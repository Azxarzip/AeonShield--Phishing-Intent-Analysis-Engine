
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

class EmailTemplate:
    """Email template generator with stylistic variation."""
    
    # Sender profiles with distinct writing styles
    SENDER_PROFILES = {
        'CEO_Formal': {
            'urgency_words': ['kindly', 'appreciate', 'require', 'immediate attention'],
            'punctuation_freq': {'!': 0.02, '.': 0.95, '...': 0.01, ',': 0.20},
            'avg_sentence_length': 18,
            'vocabulary_level': 'high',
            'exclamations': False,
            'contractions': False
        },
        'Manager_Casual': {
            'urgency_words': ['need', 'asap', 'urgent', 'quick'],
            'punctuation_freq': {'!': 0.15, '.': 0.70, '...': 0.10, ',': 0.15},
            'avg_sentence_length': 12,
            'vocabulary_level': 'medium',
            'exclamations': True,
            'contractions': True
        },
        'Attacker_Generic': {
            'urgency_words': ['urgent', 'immediate', 'critical', 'asap'],
            'punctuation_freq': {'!': 0.25, '.': 0.60, '...': 0.05, ',': 0.08},
            'avg_sentence_length': 8,
            'vocabulary_level': 'low',
            'exclamations': True,
            'contractions': False
        },
        'ATO_Compromised': {
            # Similar to original profile but with slight variations
            'urgency_words': ['please', 'need', 'urgent', 'thanks'],
            'punctuation_freq': {'!': 0.08, '.': 0.85, '...': 0.02, ',': 0.18},
            'avg_sentence_length': 16,
            'vocabulary_level': 'medium',
            'exclamations': False,
            'contractions': True
        }
    }
    
    FINANCIAL_REQUESTS = {
        'wire_transfer': [
            'Please arrange a wire transfer of {amount} to the following account: {account}',
            'Can you initiate a wire of {amount}? Account: {account}',
            'Wire transfer needed: {amount} to {account}',
            'I need a wire transfer of {amount} sent to {account} urgently'
        ],
        'credential_update': [
            'Please update your email credentials at {url}',
            'Your credentials need updating - visit {url}',
            'Update required at {url} - use your current password',
            'Verify your account at {url} immediately'
        ],
        'payment': [
            'Please process payment of {amount} to invoice {invoice}',
            'Need payment approval for {amount}',
            'Can you approve the payment of {amount}?',
            'Payment due: {amount} for {description}'
        ]
    }
    
    @staticmethod
    def generate_email(sender_type: str, request_type: str, is_malicious: bool) -> str:
        """Generate realistic email text based on style profile."""
        profile = EmailTemplate.SENDER_PROFILES[sender_type]
        
        # Build greeting
        greetings = ['Hi', 'Hello', 'Good day', 'Team'] if sender_type != 'CEO_Formal' else ['Dear', 'Greetings']
        greeting = f"{random.choice(greetings)},"
        
        # Build main content
        if request_type == 'wire_transfer':
            templates = EmailTemplate.FINANCIAL_REQUESTS['wire_transfer']
            request = random.choice(templates).format(
                amount=f"${random.randint(10000, 500000)}",
                account="****1234"
            )
        elif request_type == 'credential_update':
            templates = EmailTemplate.FINANCIAL_REQUESTS['credential_update']
            request = random.choice(templates).format(
                url="https://secure-" + ('company' if not is_malicious else random.choice(['companyy', 'commpany'])) + ".com"
            )
        else:  # payment
            templates = EmailTemplate.FINANCIAL_REQUESTS['payment']
            request = random.choice(templates).format(
                amount=f"${random.randint(5000, 100000)}",
                invoice="INV-" + str(random.randint(10000, 99999)),
                description=random.choice(['contract', 'services', 'supplies', 'consulting'])
            )
        
        # Add closing remarks
        if profile['exclamations']:
            closing = random.choice([
                "This is urgent! Please handle immediately.",
                "Thanks! Need this done ASAP.",
                "Appreciate your quick response!",
                "Critical! Send confirmation once complete."
            ])
        else:
            closing = random.choice([
                "Please confirm once processed.",
                "Kindly arrange this at your earliest convenience.",
                "Thank you for your attention to this matter.",
                "Appreciation for your prompt action."
            ])
        
        # Construct email
        email_body = f"{greeting}\n\n{request}\n\n{closing}"
        
        if profile['contractions']:
            email_body = email_body.replace('Thank you', "Thanks").replace('Please', "Pls")
        
        return email_body


def generate_bec_data_enhanced(n_samples: int = 2000) -> Tuple[pd.DataFrame, Dict]:
    """
    Generates synthetic BEC/Phishing data with email text and sender metadata.
    
    Returns:
        DataFrame with enhanced features and metadata dictionary
    """
    
    data_records = []
    
    # Create sender profiles for baseline
    senders = {
        'CEO': {'name': 'John Executive', 'profile': 'CEO_Formal', 'style_baseline': None},
        'Manager1': {'name': 'Jane Manager', 'profile': 'Manager_Casual', 'style_baseline': None},
        'Manager2': {'name': 'Bob Finance', 'profile': 'Manager_Casual', 'style_baseline': None},
    }
    
    for i in range(n_samples):
        # Basic features (from original simulator)
        urgency = np.random.beta(a=3, b=5)
        domain_sim = np.random.beta(a=5, b=2)
        finance_keywords = np.random.poisson(lam=2)
        request_type = np.random.randint(0, 3)
        sender_anomaly = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Determine if malicious
        base_prob = (0.2 + 0.5 * urgency + 0.3 * (domain_sim > 0.7) + 
                     0.2 * (request_type > 0) + 0.4 * sender_anomaly)
        base_prob = np.clip(base_prob, 0.05, 0.95)
        
        if finance_keywords > 3:
            base_prob *= 1.2
        base_prob = np.clip(base_prob, 0.05, 0.95)
        
        is_malicious = np.random.rand() < base_prob
        label = int(is_malicious)
        
        # Assign sender
        sender_key = random.choice(list(senders.keys()))
        sender_info = senders[sender_key]
        
        # Determine if this is ATO (compromised account)
        is_ato = False
        if is_malicious and sender_anomaly == 0:  # No anomaly flag but malicious = possible ATO
            is_ato = np.random.rand() < 0.3  # 30% chance of ATO vs external attacker
        
        # Generate email text
        sender_profile = sender_info['profile']
        if is_ato:
            # Compromised account shows style drift
            sender_profile = 'ATO_Compromised'  # Slight style change
        
        email_text = EmailTemplate.generate_email(
            sender_profile, 
            'wire_transfer' if request_type == 2 else 'credential_update' if request_type == 1 else 'payment',
            is_malicious
        )
        
        record = {
            'urgency_score': urgency,
            'domain_similarity_score': domain_sim,
            'financial_keyword_count': finance_keywords,
            'request_type': request_type,
            'sender_anomaly': sender_anomaly,
            'sender_name': sender_info['name'],
            'sender_profile': sender_info['profile'],
            'email_body': email_text,
            'is_ato': int(is_ato),
            'label': label
        }
        
        data_records.append(record)
    
    df = pd.DataFrame(data_records)
    
    # Create metadata for baseline profiles
    metadata = {
        'senders': senders,
        'total_samples': int(n_samples),
        'n_malicious': int(df['label'].sum()),
        'n_ato': int(df['is_ato'].sum()),
        'generation_date': pd.Timestamp.now().isoformat()
    }
    
    return df, metadata


if __name__ == '__main__':
    df, metadata = generate_bec_data_enhanced(n_samples=2000)
    
    # Save main data
    df.to_csv('simulated_emails_enhanced.csv', index=False)
    
    # Save metadata
    import json
    with open('email_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Generating {len(df)} synthetic email records with text...")
    print(f"✅ Created simulated_emails_enhanced.csv")
    print(f"✅ Created email_metadata.json")
    print(f"\nDataset Statistics:")
    print(f"  - Total samples: {len(df)}")
    print(f"  - Malicious: {df['label'].sum()} ({df['label'].sum()/len(df)*100:.1f}%)")
    print(f"  - Account Takeover (ATO): {df['is_ato'].sum()} ({df['is_ato'].sum()/len(df)*100:.1f}%)")
    print(f"  - Sample email length: {len(df['email_body'].iloc[0])} chars")

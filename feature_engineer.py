import pandas as pd

def preprocess_features(df):
    """
    Cleans and prepares features for the BEC detection model.
    """
    # Create a copy to avoid modifying original data
    data = df.copy()
    
    # Feature Selection
    feature_cols = [
        'urgency_score', 
        'domain_similarity_score', 
        'financial_keyword_count', 
        'sender_anomaly'
    ]
    
    # One-Hot Encoding for 'request_type' (Categorical: 0=None, 1=Info, 2=Wire Transfer)
    request_dummies = pd.get_dummies(data['request_type'], prefix='req_type')
    
    # Combine numerical features and encoded dummies
    X = pd.concat([data[feature_cols], request_dummies], axis=1)
    
    # Define Target
    y = data['label']
    
    return X, y
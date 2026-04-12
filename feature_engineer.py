import pandas as pd
from stylometry_analyzer import StylometryAnalyzer, create_stylometry_features_df

def preprocess_features(df):
    """
    Cleans and prepares features for the BEC detection model.
    Now includes stylometry features if email_body is present.
    """
    # Create a copy to avoid modifying original data
    data = df.copy()
    
    # Feature Selection - Original technical features
    feature_cols = [
        'urgency_score', 
        'domain_similarity_score', 
        'financial_keyword_count', 
        'sender_anomaly'
    ]
    
    # Check if we have email text for stylometry features
    stylometry_cols = []
    if 'email_body' in data.columns:
        # Add stylometry features
        data = create_stylometry_features_df(data)
        
        # All stylometry features to use
        stylometry_cols = [
            'punctuation_exclamation_freq',
            'punctuation_question_freq',
            'punctuation_ellipsis_freq',
            'punctuation_comma_freq',
            'punctuation_density',
            'avg_sentence_length',
            'sentence_length_variance',
            'vocabulary_richness',
            'corporate_jargon_freq',
            'rare_words_freq',
            'avg_word_length',
            'word_length_variance',
            'contraction_freq',
            'pronoun_freq',
            'urgency_words_freq',
            'capitalization_freq',
            'formality_score'
        ]
        
        # Add ATO indicator if available
        if 'is_ato' in data.columns:
            feature_cols.insert(0, 'is_ato')
    
    # One-Hot Encoding for 'request_type' (Categorical: 0=None, 1=Info, 2=Wire Transfer)
    request_dummies = pd.get_dummies(data['request_type'], prefix='req_type')
    # Ensure all expected OHE columns exist
    expected_ohe = ['req_type_0', 'req_type_1', 'req_type_2']
    request_dummies = request_dummies.reindex(columns=expected_ohe, fill_value=0)
    
    # Combine all features: technical + stylometry + encoded dummies
    X = pd.concat([data[feature_cols], data[stylometry_cols] if stylometry_cols else pd.DataFrame(), request_dummies], axis=1)
    
    # Define Target
    y = data['label']
    
    return X, y


def preprocess_features_for_prediction(email_text: str, 
                                       urgency_score: float,
                                       domain_similarity_score: float,
                                       financial_keyword_count: int,
                                       request_type: int,
                                       sender_anomaly: int,
                                       is_ato: int = 0) -> pd.DataFrame:
    """
    Prepare a single email prediction with stylometry features.
    
    Args:
        email_text: Raw email body
        urgency_score: Urgency score (0-1)
        domain_similarity_score: Domain similarity (0-1)
        financial_keyword_count: Count of financial keywords
        request_type: Request type (0, 1, 2)
        sender_anomaly: Sender anomaly flag (0 or 1)
        is_ato: Account takeover indicator (0 or 1)
        
    Returns:
        DataFrame with all features ready for prediction
    """
    # Extract stylometry features from email text
    analyzer = StylometryAnalyzer()
    stylometry_features = analyzer.extract_features(email_text)
    
    # Build feature record
    record = {
        'is_ato': is_ato,
        'urgency_score': urgency_score,
        'domain_similarity_score': domain_similarity_score,
        'financial_keyword_count': financial_keyword_count,
        'sender_anomaly': sender_anomaly,
    }
    
    # Add stylometry features
    record.update(stylometry_features)
    
    # Create dataframe
    df_new = pd.DataFrame([record])
    
    # Apply OHE for request_type (ensure int for correct dummies)
    request_type = int(request_type) if request_type is not None else 0
    df_new['request_type'] = min(max(request_type, 0), 2)
    df_processed = pd.get_dummies(df_new, columns=['request_type'], prefix='req_type')
    # Single-row get_dummies omits absent categories; model expects all three columns
    for col in ['req_type_0', 'req_type_1', 'req_type_2']:
        if col not in df_processed.columns:
            df_processed[col] = 0

    return df_processed
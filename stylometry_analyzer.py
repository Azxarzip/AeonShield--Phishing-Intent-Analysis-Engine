
import re
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple
import pandas as pd

class StylometryAnalyzer:
    """Extract linguistic features from email text for ATO detection."""
    
    def __init__(self):
        """Initialize analyzer with linguistic resources."""
        # Common punctuation patterns
        self.punctuation_marks = {
            'exclamation': '!',
            'question': '?',
            'period': '.',
            'comma': ',',
            'ellipsis': '...',
            'dash': '-',
            'colon': ':'
        }
        
        # Vocabulary complexity markers
        self.corporate_jargon = [
            'facilitate', 'synergy', 'leverage', 'paradigm', 'stakeholder',
            'escalate', 'bandwidth', 'pivot', 'roadmap', 'deliverable',
            'milestone', 'value-add', 'touch base', 'circle back'
        ]
        
        self.rare_words_set = self._get_rare_words()
        
    def _get_rare_words(self) -> set:
        """Common rare/formal words."""
        return {
            'pursuant', 'hereinafter', 'aforementioned', 'notwithstanding',
            'heretofore', 'whatsoever', 'thereafter', 'insofar', 'whereby'
        }
    
    def extract_features(self, email_text: str) -> Dict[str, float]:
        """
        Extract all stylometry features from email text.
        
        Args:
            email_text: Raw email body text
            
        Returns:
            Dictionary of stylometry features (0-1 normalized)
        """
        features = {}
        
        # Text preprocessing
        text_lower = email_text.lower()
        sentences = self._split_sentences(email_text)
        words = self._tokenize_words(email_text)
        
        # 1. Punctuation Patterns
        features['punctuation_exclamation_freq'] = self._count_punctuation(email_text, '!')
        features['punctuation_question_freq'] = self._count_punctuation(email_text, '?')
        features['punctuation_ellipsis_freq'] = self._count_punctuation(email_text, '...')
        features['punctuation_comma_freq'] = self._count_punctuation(email_text, ',')
        features['punctuation_density'] = self._punctuation_density(email_text)
        
        # 2. Sentence Structure
        features['avg_sentence_length'] = self._avg_sentence_length(sentences, words)
        features['sentence_length_variance'] = self._sentence_length_variance(sentences, words)
        
        # 3. Vocabulary Complexity
        features['vocabulary_richness'] = self._vocabulary_richness(words)
        features['corporate_jargon_freq'] = self._corporate_jargon_freq(text_lower)
        features['rare_words_freq'] = self._rare_words_freq(text_lower)
        
        # 4. Word Patterns
        features['avg_word_length'] = self._avg_word_length(words)
        features['word_length_variance'] = self._word_length_variance(words)
        
        # 5. Contraction & Informal Speech
        features['contraction_freq'] = self._contraction_freq(text_lower)
        features['pronoun_freq'] = self._pronoun_freq(text_lower)
        
        # 6. Urgency Linguistic Markers
        features['urgency_words_freq'] = self._urgency_words_freq(text_lower)
        features['capitalization_freq'] = self._capitalization_freq(email_text)
        
        # 7. Formality Score (composite)
        features['formality_score'] = self._calculate_formality(features)
        
        # Ensure all values are in [0, 1]
        features = {k: float(np.clip(v, 0, 1)) for k, v in features.items()}
        
        return features
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on period, !, ?
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _count_punctuation(self, text: str, punctuation: str) -> float:
        """Count frequency of specific punctuation (normalized by text length)."""
        if len(text) == 0:
            return 0
        count = text.count(punctuation)
        return min(count / (len(text) / 100), 1.0)  # Normalize
    
    def _punctuation_density(self, text: str) -> float:
        """Calculate overall punctuation density."""
        if len(text) == 0:
            return 0
        punct_count = sum(text.count(p) for p in '!?.,;:-')
        return min(punct_count / (len(text) / 10), 1.0)
    
    def _split_sentences_properly(self, sentences: List[str]) -> List[int]:
        """Get word count for each sentence."""
        sentence_lengths = []
        for sent in sentences:
            word_count = len(self._tokenize_words(sent))
            sentence_lengths.append(word_count)
        return sentence_lengths
    
    def _avg_sentence_length(self, sentences: List[str], all_words: List[str]) -> float:
        """Average sentence length in words (normalized 0-1)."""
        if len(sentences) == 0:
            return 0.5
        avg_length = len(all_words) / len(sentences)
        return min(avg_length / 30, 1.0)  # Normalize to typical range
    
    def _sentence_length_variance(self, sentences: List[str], all_words: List[str]) -> float:
        """Variance in sentence length (consistency of writing)."""
        if len(sentences) <= 1:
            return 0
        
        sent_lengths = self._split_sentences_properly(sentences)
        if not sent_lengths:
            return 0
        
        variance = np.var(sent_lengths)
        return min(variance / 100, 1.0)  # Normalize
    
    def _vocabulary_richness(self, words: List[str]) -> float:
        """Type-Token Ratio (TTR): unique words / total words."""
        if len(words) == 0:
            return 0
        unique_words = len(set(words))
        ttr = unique_words / len(words)
        return min(ttr, 1.0)
    
    def _corporate_jargon_freq(self, text_lower: str) -> float:
        """Frequency of corporate jargon usage."""
        count = sum(text_lower.count(word) for word in self.corporate_jargon)
        words = len(self._tokenize_words(text_lower))
        if words == 0:
            return 0
        return min(count / (words / 20), 1.0)
    
    def _rare_words_freq(self, text_lower: str) -> float:
        """Frequency of rare/formal words."""
        count = sum(text_lower.count(word) for word in self.rare_words_set)
        words = len(self._tokenize_words(text_lower))
        if words == 0:
            return 0
        return min(count / (words / 50), 1.0)
    
    def _avg_word_length(self, words: List[str]) -> float:
        """Average word length (normalized 0-1)."""
        if len(words) == 0:
            return 0.5
        avg_len = np.mean([len(w) for w in words])
        return min(avg_len / 15, 1.0)  # Normalize
    
    def _word_length_variance(self, words: List[str]) -> float:
        """Variance in word lengths."""
        if len(words) <= 1:
            return 0.5
        word_lengths = [len(w) for w in words]
        variance = np.var(word_lengths)
        return min(variance / 20, 1.0)
    
    def _contraction_freq(self, text_lower: str) -> float:
        """Frequency of contractions (I'm, don't, etc.)."""
        contractions = ["i'm", "don't", "can't", "won't", "it's", "that's", "you're"]
        count = sum(text_lower.count(c) for c in contractions)
        words = len(self._tokenize_words(text_lower))
        if words == 0:
            return 0
        return min(count / (words / 10), 1.0)
    
    def _pronoun_freq(self, text_lower: str) -> float:
        """Frequency of personal pronouns."""
        pronouns = ['i ', ' me ', ' we ', ' us ', ' you ', ' he ', ' she ', ' they ', ' them ']
        count = sum(text_lower.count(p) for p in pronouns)
        words = len(self._tokenize_words(text_lower))
        if words == 0:
            return 0
        return min(count / (words / 5), 1.0)
    
    def _urgency_words_freq(self, text_lower: str) -> float:
        """Frequency of urgency-indicating words."""
        urgency_words = [
            'urgent', 'urgent!', 'asap', 'immediate', 'immediately', 'critical',
            'critical!', 'emergency', 'emergency!', 'now', 'quickly', 'hurry', 'rushed'
        ]
        count = sum(text_lower.count(w) for w in urgency_words)
        words = len(self._tokenize_words(text_lower))
        if words == 0:
            return 0
        return min(count / (words / 20), 1.0)
    
    def _capitalization_freq(self, text: str) -> float:
        """Frequency of ALL CAPS words."""
        caps_words = len([w for w in text.split() if w.isupper() and len(w) > 1])
        total_words = len(text.split())
        if total_words == 0:
            return 0
        return min(caps_words / (total_words / 10), 1.0)
    
    def _calculate_formality(self, features: Dict[str, float]) -> float:
        """
        Calculate overall formality score.
        Formal: high rare words, low contractions, low exclamations
        """
        formality = (
            features.get('rare_words_freq', 0) * 0.3 +
            features.get('corporate_jargon_freq', 0) * 0.2 +
            (1 - features.get('contraction_freq', 0)) * 0.2 +
            (1 - features.get('punctuation_exclamation_freq', 0)) * 0.15 +
            (1 - features.get('capitalization_freq', 0)) * 0.15
        )
        return min(formality, 1.0)


class BaselineProfileBuilder:
    """Build and manage baseline stylometry profiles for senders."""
    
    def __init__(self, analyzer: StylometryAnalyzer):
        """Initialize with stylometry analyzer."""
        self.analyzer = analyzer
        self.profiles = {}
    
    def build_profile(self, sender_name: str, email_texts: List[str], 
                     min_emails: int = 3) -> Dict[str, float]:
        """
        Build baseline stylometry profile for a sender.
        
        Args:
            sender_name: Name of sender
            email_texts: List of email bodies from this sender
            min_emails: Minimum emails to build profile
            
        Returns:
            Baseline profile (mean + std of features)
        """
        if len(email_texts) < min_emails:
            raise ValueError(f"Need at least {min_emails} emails, got {len(email_texts)}")
        
        # Extract features from all emails
        all_features = [self.analyzer.extract_features(text) for text in email_texts]
        
        # Calculate mean and std
        profile = {}
        for key in all_features[0].keys():
            values = [f[key] for f in all_features]
            profile[f'{key}_mean'] = float(np.mean(values))
            profile[f'{key}_std'] = float(np.std(values))
        
        self.profiles[sender_name] = profile
        return profile
    
    def detect_style_drift(self, sender_name: str, email_text: str,
                          threshold: float = 2.0) -> Tuple[bool, float, Dict]:
        """
        Detect if an email shows stylometric deviation from sender's baseline.
        
        Args:
            sender_name: Name of sender
            email_text: New email to analyze
            threshold: Z-score threshold for anomaly (default 2.0 = 95% confidence)
            
        Returns:
            (is_anomaly, anomaly_score, details)
        """
        if sender_name not in self.profiles:
            return False, 0.0, {}
        
        profile = self.profiles[sender_name]
        features = self.analyzer.extract_features(email_text)
        
        # Calculate z-scores for each feature
        z_scores = {}
        for key, value in features.items():
            mean_key = f'{key}_mean'
            std_key = f'{key}_std'
            
            if mean_key in profile and std_key in profile:
                std_val = profile[std_key]
                if std_val > 0:
                    z_score = (value - profile[mean_key]) / std_val
                    z_scores[key] = z_score
        
        # Calculate anomaly score (max z-score deviation)
        if z_scores:
            anomaly_score = max(abs(z) for z in z_scores.values())
            is_anomaly = anomaly_score > threshold
        else:
            anomaly_score = 0.0
            is_anomaly = False
        
        return is_anomaly, float(anomaly_score), z_scores


def create_stylometry_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add stylometry features to dataframe with email_body column.
    
    Args:
        df: DataFrame with 'email_body' column
        
    Returns:
        DataFrame with added stylometry features
    """
    analyzer = StylometryAnalyzer()
    
    # Extract stylometry features
    stylometry_features = []
    for email_text in df['email_body']:
        features = analyzer.extract_features(email_text)
        stylometry_features.append(features)
    
    # Create dataframe of stylometry features
    stylometry_df = pd.DataFrame(stylometry_features)
    
    # Concatenate with original data
    result = pd.concat([df.reset_index(drop=True), stylometry_df.reset_index(drop=True)], axis=1)
    
    return result


if __name__ == '__main__':
    # Example usage
    from data_simulator_enhanced import generate_bec_data_enhanced
    
    print("Generating enhanced dataset...")
    df, metadata = generate_bec_data_enhanced(n_samples=500)
    
    print("Extracting stylometry features...")
    df_with_stylometry = create_stylometry_features_df(df)
    
    print(f"✅ Added {len(df_with_stylometry.columns) - len(df.columns)} stylometry features")
    print(f"\nNew features:")
    stylometry_cols = [c for c in df_with_stylometry.columns if c not in df.columns]
    for col in stylometry_cols[:5]:
        print(f"  - {col}")
    print(f"  ... and {len(stylometry_cols) - 5} more")
    
    # Save with stylometry features
    df_with_stylometry.to_csv('simulated_emails_with_stylometry.csv', index=False)
    print(f"\n✅ Saved to simulated_emails_with_stylometry.csv")

import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from feature_engineer import preprocess_features

def train_and_evaluate():
    print("--- BEC Phishing Detection Model Training (Visual) ---")
    
    # 1. Load Data
    try:
        df = pd.read_csv('simulated_emails.csv')
    except FileNotFoundError:
        print("Error: 'simulated_emails.csv' not found. Run data_simulator.py first.")
        return

    # 2. Preprocess
    X, y = preprocess_features(df)
    
    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train with Class Weights for High Recall
    # We give the 'Malicious' class (1) much higher weight
    model = RandomForestClassifier(
        n_estimators=100, 
        class_weight={0: 1, 1: 5}, 
        random_state=42
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Malicious']))

    # 6. Save Model
    joblib.dump(model, 'model.pkl')
    print("✅ Model saved to 'model.pkl'")

    # Save feature names used by the model so predictions can align features correctly
    feature_names = X.columns.tolist()
    joblib.dump(feature_names, 'feature_names.pkl')
    print("✅ Feature names saved to 'feature_names.pkl'")

    # 7. GRAPHICAL CONFUSION MATRIX
    print("\nGenerating Confusion Matrix Plot...")
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Predicted Legitimate', 'Predicted Malicious'],
                yticklabels=['Actual Legitimate', 'Actual Malicious'])
    
    plt.title('Confusion Matrix: BEC Phishing Detection')
    plt.ylabel('Actual Category')
    plt.xlabel('Predicted Category')
    
    # Save the plot as an image for your report
    plt.savefig('confusion_matrix.png', bbox_inches='tight')
    print("✅ Plot saved as 'confusion_matrix.png'")
    plt.close()

if __name__ == "__main__":
    train_and_evaluate()
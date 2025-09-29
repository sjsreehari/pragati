import pandas as pd
import xgboost as xgb
import os
from preprocess import preprocess_dataframe, encode_labels, save_vectorizer, save_encoder
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Optional translation support for multilingual DPRs
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("Translation not available - continuing with English only")

def translate_text_if_needed(text, target_lang='en'):
    """Translate text to target language if translation is available"""
    if not TRANSLATION_AVAILABLE or not text.strip():
        return text
    
    try:
        # Detect if text is already in English
        if len(text.split()) > 0 and all(ord(char) < 128 for char in text[:100]):
            return text  # Already English
        
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def preprocess_multilingual_data(df):
    """Handle multilingual DPR data for Northeast India languages"""
    if 'text' not in df.columns:
        return df
    
    print("Processing multilingual data...")
    processed_texts = []
    
    for text in df['text']:
        translated_text = translate_text_if_needed(text)
        processed_texts.append(translated_text)
    
    df['text'] = processed_texts
    return df

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("data/data.csv")

# Handle multilingual content for Northeast India
df = preprocess_multilingual_data(df)

# -----------------------------
# Preprocess features & labels
# -----------------------------
X, tfidf = preprocess_dataframe(df)
y, encoder = encode_labels(df["label"])

# -----------------------------
# Train-test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# Train XGBoost GPU model
# -----------------------------
model = xgb.XGBClassifier(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="gpu_hist" if os.environ.get('CUDA_AVAILABLE') else "hist",
    predictor="gpu_predictor" if os.environ.get('CUDA_AVAILABLE') else "auto",
    gpu_id=0 if os.environ.get('CUDA_AVAILABLE') else None,
    random_state=42
)

print("Training model...")
model.fit(X_train, y_train)

# -----------------------------
# Evaluate
# -----------------------------
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# -----------------------------
# Save model, encoder, TF-IDF
# -----------------------------
os.makedirs("models", exist_ok=True)
model.save_model("models/dpr_model.json")       # XGBoost native JSON
joblib.dump(model, "models/dpr_model.pkl")      # sklearn wrapper for easy loading
save_vectorizer(tfidf)
save_encoder(encoder)

print("✅ Model, encoder, and TF-IDF vectorizer saved in 'models/' folder")

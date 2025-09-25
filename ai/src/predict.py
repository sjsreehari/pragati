import pandas as pd
import joblib
from preprocess import preprocess_dataframe, load_vectorizer, load_encoder
import xgboost as xgb

# -----------------------------
# Load saved model & preprocessing
# -----------------------------
model = joblib.load("models/dpr_model.pkl")
tfidf = load_vectorizer()
encoder = load_encoder()

# -----------------------------
# Example: new DPR text
# -----------------------------
new_dpr_text = [
    {
        "text": "Bridge construction of 3 km over Brahmaputra. Budget ₹15 crore. Timeline 5 months.",
    },
]

new_df = pd.DataFrame(new_dpr_text)

# -----------------------------
# Preprocess new data
# -----------------------------
X_new, _ = preprocess_dataframe(new_df, fit_vectorizer=False, tfidf=tfidf)

# -----------------------------
# Predict feasibility
# -----------------------------
y_pred = model.predict(X_new)
decoded_pred = encoder.inverse_transform(y_pred)

print("Prediction:", decoded_pred[0])

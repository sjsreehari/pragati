import pandas as pd
import xgboost as xgb
import os
from preprocess import preprocess_dataframe, encode_labels, save_vectorizer, save_encoder
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("data/data.csv")

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
    tree_method="gpu_hist",
    predictor="gpu_predictor",
    gpu_id=0,
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

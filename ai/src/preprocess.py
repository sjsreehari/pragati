import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack
import joblib
import os

# -----------------------------
# Numeric feature extraction
# -----------------------------
def extract_budget(text):
    """Extract budget in crores from DPR text"""
    m = re.search(r"Budget[^\d]*(\d+)", str(text))
    return float(m.group(1)) if m else 0.0

def extract_timeline(text):
    """Extract timeline in months from DPR text"""
    m = re.search(r"Timeline[^\d]*(\d+)", str(text))
    return float(m.group(1)) if m else 0.0

# -----------------------------
# Preprocessing dataset
# -----------------------------
def preprocess_dataframe(df, fit_vectorizer=True, tfidf=None):
    """
    Preprocess DPR DataFrame:
    - Extract budget and timeline
    - Convert text to TF-IDF features
    - Returns feature matrix X and optionally fitted TF-IDF vectorizer
    """
    df = df.copy()
    df["budget"] = df["text"].apply(extract_budget)
    df["timeline"] = df["text"].apply(extract_timeline)

    if fit_vectorizer or tfidf is None:
        tfidf = TfidfVectorizer(max_features=500)
        X_text = tfidf.fit_transform(df["text"].astype(str))
    else:
        X_text = tfidf.transform(df["text"].astype(str))

    # Combine numeric + text features
    X = hstack([X_text, df[["budget","timeline"]].values])

    return X, tfidf

# -----------------------------
# Label encoding
# -----------------------------
def encode_labels(y=None, fit=True, encoder=None):
    """
    Encode 'feasible'/'risky' labels to 1/0
    Returns encoded labels and encoder
    """
    if fit or encoder is None:
        encoder = LabelEncoder()
        y_enc = encoder.fit_transform(y)
    else:
        y_enc = encoder.transform(y)
    return y_enc, encoder

# -----------------------------
# Save/load helpers
# -----------------------------
def save_vectorizer(tfidf, path="models/tfidf.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(tfidf, path)

def load_vectorizer(path="models/tfidf.pkl"):
    return joblib.load(path)

def save_encoder(encoder, path="models/encoder.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(encoder, path)

def load_encoder(path="models/encoder.pkl"):
    return joblib.load(path)

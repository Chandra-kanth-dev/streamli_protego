"""
train_risk.py
=============
Improved training script for SAFETY-CRITICAL risk classification in PROTEGO.

Upgrades:
- Stronger linear classifier (LinearSVC)
- Cleaner TF-IDF features
- Conservative, audit-friendly design
- Same runtime compatibility
"""

import pandas as pd
import joblib
from pathlib import Path
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from protego.nlp.preprocess import clean_text


# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "risk_data.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# -------------------------------------------------
# Load & validate dataset
# -------------------------------------------------
df = pd.read_csv(DATA_PATH)

required_cols = {"text", "risk"}
if not required_cols.issubset(df.columns):
    raise ValueError("Dataset must contain 'text' and 'risk' columns")

df = df.dropna(subset=["text", "risk"])
df["risk"] = df["risk"].str.strip().str.lower()

ALLOWED_RISKS = {"low", "medium", "high", "emergency"}
invalid_labels = set(df["risk"]) - ALLOWED_RISKS
if invalid_labels:
    raise ValueError(f"Invalid risk labels found: {invalid_labels}")

print("📊 Risk label distribution:")
print(Counter(df["risk"]))
print("-" * 40)


# -------------------------------------------------
# Preprocess text
# -------------------------------------------------
df["clean_text"] = df["text"].astype(str).apply(clean_text)

X = df["clean_text"]
y = df["risk"]


# -------------------------------------------------
# Train-test split (stratified)
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -------------------------------------------------
# Pipeline: TF-IDF + Linear SVM (Conservative)
# -------------------------------------------------
pipeline = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=8000,
                min_df=2,
                sublinear_tf=True
            )
        ),
        (
            "clf",
            LinearSVC(
                class_weight={
                    "low": 1.0,
                    "medium": 1.2,
                    "high": 1.5,
                    "emergency": 2.0
                },
                random_state=42
            )
        )
    ]
)


# -------------------------------------------------
# Train
# -------------------------------------------------
pipeline.fit(X_train, y_train)


# -------------------------------------------------
# Evaluate
# -------------------------------------------------
y_pred = pipeline.predict(X_test)

print("\n📊 Risk Model Evaluation")
print("-" * 40)
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# -------------------------------------------------
# Save artifacts (runtime compatible)
# -------------------------------------------------
joblib.dump(pipeline.named_steps["clf"], MODEL_DIR / "risk_model.pkl")
joblib.dump(pipeline.named_steps["tfidf"], MODEL_DIR / "risk_vectorizer.pkl")

print("\n✅ Risk model training complete")
print(f"📁 Model saved to: {MODEL_DIR / 'risk_model.pkl'}")
print(f"📁 Vectorizer saved to: {MODEL_DIR / 'risk_vectorizer.pkl'}")

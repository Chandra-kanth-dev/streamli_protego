"""
train_sentiment.py
==================
Improved training script for sentiment analysis in PROTEGO.
Upgrades:
- Cleaner TF-IDF
- Better Logistic Regression configuration
- Pipeline-based training
- Same runtime compatibility
"""

import pandas as pd
import joblib
from pathlib import Path
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from protego.nlp.preprocess import clean_text


# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "sentiment_data.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# -------------------------------------------------
# Load & validate dataset
# -------------------------------------------------
df = pd.read_csv(DATA_PATH)

required_cols = {"text", "sentiment"}
if not required_cols.issubset(df.columns):
    raise ValueError("Dataset must contain 'text' and 'sentiment' columns")

df = df.dropna(subset=["text", "sentiment"])
df["sentiment"] = df["sentiment"].str.strip().str.lower()

ALLOWED_SENTIMENTS = {"positive", "neutral", "negative"}
invalid_labels = set(df["sentiment"]) - ALLOWED_SENTIMENTS
if invalid_labels:
    raise ValueError(f"Invalid sentiment labels found: {invalid_labels}")

print("📊 Sentiment label distribution:")
print(Counter(df["sentiment"]))
print("-" * 40)


# -------------------------------------------------
# Preprocess text
# -------------------------------------------------
df["clean_text"] = df["text"].astype(str).apply(clean_text)

X = df["clean_text"]
y = df["sentiment"]


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
# Pipeline: TF-IDF + Logistic Regression
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
            LogisticRegression(
                solver="saga",
                max_iter=3000,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
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

print("\n📊 Sentiment Model Evaluation")
print("-" * 40)
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# -------------------------------------------------
# Save artifacts (runtime compatible)
# -------------------------------------------------
joblib.dump(pipeline.named_steps["clf"], MODEL_DIR / "sentiment_model.pkl")
joblib.dump(pipeline.named_steps["tfidf"], MODEL_DIR / "sentiment_vectorizer.pkl")

print("\n✅ Sentiment model training complete")
print(f"📁 Model saved to: {MODEL_DIR / 'sentiment_model.pkl'}")
print(f"📁 Vectorizer saved to: {MODEL_DIR / 'sentiment_vectorizer.pkl'}")

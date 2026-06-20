"""
train_emotion.py
================
Improved training script for emotion classification in PROTEGO.
Upgrades:
- Cleaner TF-IDF
- Stronger linear classifier
- Pipeline-based training
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
DATA_PATH = BASE_DIR / "data" / "raw" / "emotion_data.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# -------------------------------------------------
# Load & validate dataset
# -------------------------------------------------
df = pd.read_csv(DATA_PATH)

required_cols = {"text", "emotion"}
if not required_cols.issubset(df.columns):
    raise ValueError("Dataset must contain 'text' and 'emotion' columns")

df = df.dropna(subset=["text", "emotion"])
df["emotion"] = df["emotion"].str.strip().str.lower()

ALLOWED_EMOTIONS = {"sadness", "fear", "anger", "shame", "neutral"}
invalid_labels = set(df["emotion"]) - ALLOWED_EMOTIONS
if invalid_labels:
    raise ValueError(f"Invalid emotion labels found: {invalid_labels}")

print("📊 Emotion label distribution:")
print(Counter(df["emotion"]))
print("-" * 40)


# -------------------------------------------------
# Preprocess text
# -------------------------------------------------
df["clean_text"] = df["text"].astype(str).apply(clean_text)

X = df["clean_text"]
y = df["emotion"]


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
# Pipeline: TF-IDF + Linear SVM
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
                class_weight="balanced",
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

print("\n📊 Emotion Model Evaluation")
print("-" * 40)
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# -------------------------------------------------
# Save artifacts (runtime compatible)
# -------------------------------------------------
joblib.dump(pipeline.named_steps["clf"], MODEL_DIR / "emotion_model.pkl")
joblib.dump(pipeline.named_steps["tfidf"], MODEL_DIR / "emotion_vectorizer.pkl")

print("\n✅ Emotion model training complete")
print(f"📁 Model saved to: {MODEL_DIR / 'emotion_model.pkl'}")
print(f"📁 Vectorizer saved to: {MODEL_DIR / 'emotion_vectorizer.pkl'}")

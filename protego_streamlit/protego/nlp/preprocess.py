"""
preprocess.py
================
Enhanced centralized NLP preprocessing module for PROTEGO.
"""

import re
import nltk
from functools import lru_cache
from typing import List

# Download required NLTK data silently
for pkg in ['stopwords', 'wordnet', 'omw-1.4']:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

_LEMMATIZER = WordNetLemmatizer()

try:
    _STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download('stopwords', quiet=True)
    _STOP_WORDS = set(stopwords.words("english"))

NEGATION_WORDS = {
    "not", "no", "never",
    "dont", "can't", "cant",
    "won't", "wont",
    "isn't", "isnt",
    "aren't", "arent",
    "didn't", "didnt",
    "couldn't", "couldnt",
    "shouldn't", "shouldnt"
}

_STOP_WORDS = _STOP_WORDS - NEGATION_WORDS

URL_PATTERN = re.compile(r"http\S+|www\S+")
NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z!?'\s]")
MULTISPACE_PATTERN = re.compile(r"\s+")
REPEAT_CHAR_PATTERN = re.compile(r"(.)\1{2,}")


@lru_cache(maxsize=4096)
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip().lower()
    if not text:
        return ""
    text = REPEAT_CHAR_PATTERN.sub(r"\1\1", text)
    text = URL_PATTERN.sub("", text)
    text = NON_ALPHA_PATTERN.sub(" ", text)
    text = MULTISPACE_PATTERN.sub(" ", text)
    tokens = text.split()
    if len(tokens) <= 3:
        return " ".join(tokens)
    cleaned_tokens = []
    for token in tokens:
        if token not in _STOP_WORDS:
            if token.endswith("ing") or token.endswith("ed"):
                lemma = _LEMMATIZER.lemmatize(token, pos="v")
            else:
                lemma = _LEMMATIZER.lemmatize(token)
            cleaned_tokens.append(lemma)
    return " ".join(cleaned_tokens)


def preprocess_batch(texts: List[str]) -> List[str]:
    if not isinstance(texts, list):
        return []
    return [clean_text(t) for t in texts if isinstance(t, str)]

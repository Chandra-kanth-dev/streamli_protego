import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from protego.nlp.preprocess import clean_text

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "knowledge" / "rag_kb.json"

_VECTORIZER = None
_DOCS = []
_TFIDF_MATRIX = None

def _load_kb() -> None:
    """Load the RAG Knowledge Base and fit TF-IDF vectors."""
    global _VECTORIZER, _DOCS, _TFIDF_MATRIX
    
    if len(_DOCS) > 0:
        return
        
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            _DOCS = json.load(f)
    except Exception as e:
        print(f"Error loading RAG KB: {e}")
        _DOCS = []
        return
        
    if not _DOCS:
        return
        
    # Combine title, keywords, and content for a rich representation
    corpus = []
    for doc in _DOCS:
        keywords_str = " ".join(doc.get("keywords", []))
        text = f"{doc.get('title', '')} {doc.get('category', '')} {keywords_str} {doc.get('content', '')}"
        corpus.append(clean_text(text))
        
    try:
        _VECTORIZER = TfidfVectorizer(stop_words='english')
        _TFIDF_MATRIX = _VECTORIZER.fit_transform(corpus)
    except Exception as e:
        print(f"Error vectorizing RAG corpus: {e}")
        _VECTORIZER = None
        _TFIDF_MATRIX = None

def query_kb(query: str, top_k: int = 1, min_score: float = 0.05) -> List[Dict[str, Any]]:
    """
    Search the local RAG knowledge base for matching safety documents.
    
    Returns:
        List of matching document dicts with an added 'score' field.
    """
    _load_kb()
    
    if not _DOCS or _VECTORIZER is None or _TFIDF_MATRIX is None or not query.strip():
        return []
        
    # Clean and vectorize query
    cleaned_query = clean_text(query)
    if not cleaned_query:
        # Fallback to raw query if preprocessing removes everything (very short query)
        cleaned_query = query.lower()
        
    try:
        query_vec = _VECTORIZER.transform([cleaned_query])
        # Compute cosine similarities
        similarities = cosine_similarity(query_vec, _TFIDF_MATRIX)[0]
        
        # Zip, sort and filter matches
        results = []
        for idx, score in enumerate(similarities):
            if score >= min_score:
                results.append((score, _DOCS[idx]))
                
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Format return payload
        matched_docs = []
        for score, doc in results[:top_k]:
            doc_copy = doc.copy()
            doc_copy["score"] = round(float(score), 3)
            matched_docs.append(doc_copy)
            
        return matched_docs
    except Exception as e:
        print(f"RAG query execution error: {e}")
        return []

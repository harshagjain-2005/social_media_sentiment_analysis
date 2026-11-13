# preprocessing/text_cleaner.py

import re
import nltk

# Download required NLTK data silently. OMW is optional for the WordNet
# lemmatizer and is intentionally not required at startup.
for resource in ["stopwords", "wordnet"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_stop_words = set(stopwords.words("english"))
# Preserve negations
_NEGATIONS = {"no", "not", "never", "neither", "none", "nor", "nothing", "nowhere", "hardly", "barely", "scarcely"}
_stop_words -= _NEGATIONS

_lemmatizer = WordNetLemmatizer()

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#(\w+)")
_SPECIAL_RE = re.compile(r"[^a-zA-Z0-9\s']")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Full preprocessing pipeline."""
    text = _URL_RE.sub("", text)
    text = _MENTION_RE.sub("", text)
    text = _HASHTAG_RE.sub(r"\1", text)   # keep the word
    text = _SPECIAL_RE.sub(" ", text)
    text = text.lower()
    tokens = text.split()
    tokens = [_lemmatizer.lemmatize(t) for t in tokens if t not in _stop_words and len(t) > 1]
    return _WHITESPACE_RE.sub(" ", " ".join(tokens)).strip()

# sentiment/analyzer.py

import nltk

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

_sia = SentimentIntensityAnalyzer()

POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05


def analyze(text: str) -> dict:
    scores = _sia.polarity_scores(text)
    compound = scores["compound"]
    if compound >= POS_THRESHOLD:
        label = "Positive"
    elif compound <= NEG_THRESHOLD:
        label = "Negative"
    else:
        label = "Neutral"
    return {
        "pos_score": round(scores["pos"], 4),
        "neg_score": round(scores["neg"], 4),
        "neu_score": round(scores["neu"], 4),
        "compound_score": round(compound, 4),
        "sentiment_label": label,
    }

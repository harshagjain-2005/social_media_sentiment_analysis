# visualization/charts.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter
import io


COLORS = {
    "Positive": "#2ecc71",
    "Negative": "#e74c3c",
    "Neutral":  "#3498db",
}
PALETTE = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]


def _fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    plt.close(fig)
    return buf


def sentiment_pie(records):
    counts = Counter(r["sentiment_label"] for r in records)
    labels = list(counts.keys())
    sizes  = list(counts.values())
    colors = [COLORS.get(l, "#95a5a6") for l in labels]
    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
    ax.set_title("Overall Sentiment Distribution", fontsize=13, fontweight="bold")
    return _fig_to_bytes(fig)


def topic_sentiment_bar(records):
    from collections import defaultdict
    topics = sorted({r.get("topic", "Unknown") for r in records})
    sentiments = ["Positive", "Negative", "Neutral"]
    data = defaultdict(lambda: defaultdict(int))
    for r in records:
        data[r.get("topic", "Unknown")][r["sentiment_label"]] += 1

    x = np.arange(len(topics))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, s in enumerate(sentiments):
        vals = [data[t][s] for t in topics]
        bars = ax.bar(x + i * width, vals, width, label=s, color=COLORS[s], edgecolor="white")
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(v), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x + width)
    ax.set_xticklabels(topics, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Count")
    ax.set_title("Topic-wise Sentiment Comparison", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    return _fig_to_bytes(fig)


def platform_sentiment_bar(records):
    from collections import defaultdict
    platforms = sorted({r.get("platform", "Unknown") for r in records if "platform" in r})
    if not platforms:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "No platform data", ha="center")
        return _fig_to_bytes(fig)
    sentiments = ["Positive", "Negative", "Neutral"]
    data = defaultdict(lambda: defaultdict(int))
    for r in records:
        if "platform" in r:
            data[r["platform"]][r["sentiment_label"]] += 1
    x = np.arange(len(platforms))
    width = 0.25
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, s in enumerate(sentiments):
        vals = [data[p][s] for p in platforms]
        ax.bar(x + i * width, vals, width, label=s, color=COLORS[s], edgecolor="white")
    ax.set_xticks(x + width)
    ax.set_xticklabels(platforms, rotation=10, fontsize=9)
    ax.set_ylabel("Count")
    ax.set_title("Platform-wise Sentiment Analysis", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    return _fig_to_bytes(fig)


def compound_distribution(records):
    scores = [r.get("compound_score", 0) for r in records]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(scores, bins=30, color="#3498db", edgecolor="white", alpha=0.85)
    ax.axvline(0.05,  color="#2ecc71", linestyle="--", linewidth=1.5, label="Positive threshold (+0.05)")
    ax.axvline(-0.05, color="#e74c3c", linestyle="--", linewidth=1.5, label="Negative threshold (-0.05)")
    ax.set_xlabel("Compound Score")
    ax.set_ylabel("Frequency")
    ax.set_title("Compound Score Distribution", fontsize=13, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    return _fig_to_bytes(fig)


def top_keywords(records, label, n=15):
    import re
    STOP = {"the","a","an","is","in","it","of","to","and","for","on","with","this","that","are","was",
            "be","i","my","you","your","we","they","their","our","but","so","at","by","as","or","from","have"}
    words = []
    for r in records:
        if r.get("sentiment_label") == label:
            tokens = re.findall(r"\b[a-zA-Z]{3,}\b", r.get("cleaned_text", r.get("raw_text", "")).lower())
            words.extend([t for t in tokens if t not in STOP])
    counts = Counter(words).most_common(n)
    if not counts:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, f"No {label} records", ha="center")
        return _fig_to_bytes(fig)
    terms, freqs = zip(*counts)
    color = COLORS.get(label, "#95a5a6")
    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(terms))
    ax.barh(y, freqs, color=color, edgecolor="white", alpha=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels(terms, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Frequency")
    ax.set_title(f"Top {label} Keywords", fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    return _fig_to_bytes(fig)

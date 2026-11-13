#!/usr/bin/env python3
# mapreduce/reducer.py
# Hadoop Streaming reducer — aggregates mapper output

import sys
from collections import defaultdict

sentiment_counts = defaultdict(int)
topic_sentiment_counts = defaultdict(int)
topic_compound_sums = defaultdict(float)
topic_compound_counts = defaultdict(int)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) != 3:
        continue
    key_type, key, value = parts
    try:
        val = float(value)
    except ValueError:
        continue

    if key_type == "SENTIMENT":
        sentiment_counts[key] += int(val)
    elif key_type == "TOPIC_SENTIMENT":
        topic_sentiment_counts[key] += int(val)
    elif key_type == "TOPIC_COMPOUND":
        topic_compound_sums[key] += val
        topic_compound_counts[key] += 1

# Output overall sentiment counts
print("=== Overall Sentiment Distribution ===")
for label in ["Positive", "Negative", "Neutral"]:
    print(f"{label}: {sentiment_counts.get(label, 0)}")

# Output topic-wise sentiment
print("\n=== Topic-wise Sentiment Counts ===")
for key in sorted(topic_sentiment_counts):
    topic, label = key.split("::")
    print(f"{topic} | {label}: {topic_sentiment_counts[key]}")

# Output average compound per topic
print("\n=== Topic-wise Average Compound Score ===")
for topic in sorted(topic_compound_sums):
    avg = topic_compound_sums[topic] / topic_compound_counts[topic]
    print(f"{topic}: {avg:.4f}")

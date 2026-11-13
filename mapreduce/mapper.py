#!/usr/bin/env python3
# mapreduce/mapper.py
# Hadoop Streaming mapper — reads JSON lines from stdin, emits key\tvalue pairs

import sys
import json

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        continue

    label = rec.get("sentiment_label", "Unknown")
    topic = rec.get("topic", "Unknown")
    compound = rec.get("compound_score", 0.0)

    # Overall sentiment count
    print(f"SENTIMENT\t{label}\t1")

    # Topic-wise sentiment count
    print(f"TOPIC_SENTIMENT\t{topic}::{label}\t1")

    # Topic-wise compound score accumulation
    print(f"TOPIC_COMPOUND\t{topic}\t{compound}")

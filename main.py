#!/usr/bin/env python3
# main.py — Dataset generation, preprocessing, sentiment analysis, storage, MapReduce simulation

import sys, os, json, random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from config import PLATFORMS, TOPICS, TARGET_POSTS, TARGET_COMMENTS, MR_OUTPUT_FILE, DATA_FILE
from preprocessing.text_cleaner import clean_text
from sentiment.analyzer import analyze
from database import mongo_handler as db

# ── Synthetic Data Templates ────────────────────────────────────────────────

POSITIVE_TEMPLATES = [
    "I absolutely love {topic}! It has completely changed my life for the better.",
    "Amazing advances in {topic} this year. The future looks so bright!",
    "{topic} is incredible. Best investment I've ever made!",
    "Just tried the new {topic} update and I'm blown away. Highly recommend!",
    "The progress in {topic} is mind-blowing. Kudos to the innovators!",
    "Wow {topic} never ceases to amaze me. Pure excellence!",
    "So grateful for {topic} making everyday tasks easier and more enjoyable.",
    "Great experience with {topic} today. Exceeded all my expectations! #happy",
    "The community around {topic} is so supportive and inspiring. Love it!",
    "{topic} just keeps getting better and better. Truly impressed!",
    "Had an amazing time exploring {topic}. Highly recommended to everyone!",
    "Brilliant work by the team behind {topic}. Exceptional quality!",
    "Five stars for {topic}! Worth every penny and more.",
    "The {topic} scene is thriving and I couldn't be happier about it.",
    "Thank you {topic} for bringing so much joy into my daily routine!",
]

NEGATIVE_TEMPLATES = [
    "Honestly {topic} is so overrated. Completely disappointed with the results.",
    "{topic} is a disaster. I wasted so much money and time on this.",
    "Fed up with {topic}. Nothing but bugs and broken promises.",
    "The {topic} experience has been absolutely terrible. Avoid at all costs!",
    "So frustrated with {topic}. Customer support was useless and rude.",
    "{topic} keeps crashing and no one seems to care. Unacceptable!",
    "I regret ever getting into {topic}. Total waste of my resources.",
    "Worst decision ever to invest time in {topic}. It's a complete mess.",
    "{topic} is falling apart. The quality has dropped massively.",
    "Deeply dissatisfied with {topic}. They need to do much better.",
    "Cannot believe how bad {topic} has become. Used to be great but now terrible.",
    "The {topic} hype is just marketing. The reality is far from impressive.",
    "Major disappointment with {topic}. Expected so much more.",
    "Angry and frustrated with {topic}. This is not what was promised.",
    "{topic} is draining my patience. Too many issues for too long.",
]

NEUTRAL_TEMPLATES = [
    "Just read about {topic}. Interesting developments happening in the space.",
    "{topic} has its pros and cons. Worth looking into if you're curious.",
    "The state of {topic} in 2024 is evolving. Time will tell how it goes.",
    "Some updates on {topic} today. Nothing groundbreaking but informative.",
    "Watching the {topic} space closely. Mixed signals so far.",
    "{topic} is what it is. Some people love it, others don't.",
    "Had a standard experience with {topic}. Nothing special to report.",
    "Heard about the latest {topic} news. Need to research more before forming an opinion.",
    "The {topic} debate continues. Both sides have valid points.",
    "Tried {topic} for the first time. Needs some getting used to.",
    "{topic} is developing steadily. Let's see where it goes.",
    "Attended a talk on {topic} today. Learned a few new things.",
    "The {topic} landscape is complex. Hard to say definitively.",
    "Looking at {topic} data. Trends are neither clearly up nor down.",
    "Comparing options in {topic}. Research is ongoing.",
]

COMMENT_POS = [
    "Totally agree! {topic} has been a game changer.",
    "Same experience here! Love {topic} so much.",
    "Couldn't agree more! {topic} is fantastic.",
    "Yes! {topic} is simply amazing!",
    "Great point! {topic} deserves all the praise.",
    "Absolutely! {topic} is worth every bit of attention.",
]

COMMENT_NEG = [
    "I had the same terrible experience with {topic}. Very frustrating.",
    "Exactly! {topic} is not worth the hype at all.",
    "So true. {topic} needs serious improvement.",
    "I completely agree. {topic} has let me down repeatedly.",
    "Same here, {topic} has become unreliable and disappointing.",
    "Yes, {topic} customer support is awful.",
]

COMMENT_NEU = [
    "Interesting perspective on {topic}.",
    "Fair assessment of {topic}. It depends on personal expectations.",
    "I've had mixed results with {topic} myself.",
    "Hard to say definitively about {topic}. It varies.",
    "Neutral take, makes sense. {topic} is complex.",
    "Worth watching how {topic} develops.",
]

USERNAMES = [
    "tech_wizard42", "datanerd_99", "codemaster_j", "social_guru", "pixel_pioneer",
    "cloudsurfer", "ai_enthusiast", "quantum_coder", "netrunner_x", "stream_king",
    "byte_bandit", "neural_nomad", "silicon_sage", "digital_drifter", "algo_artist",
    "cyber_ninja", "matrix_maven", "loop_lord", "hash_hero", "cache_commander",
    "api_ace", "node_navigator", "lambda_lover", "query_queen", "sync_star",
    "frame_flicker", "ping_poet", "deploy_duke", "build_baron", "scope_scout",
]


def rand_datetime(days_back=180):
    base = datetime.now() - timedelta(days=random.randint(0, days_back))
    return base.strftime("%Y-%m-%dT%H:%M:%S")


def pick_template(sentiment):
    if sentiment == "pos":
        return random.choice(POSITIVE_TEMPLATES)
    elif sentiment == "neg":
        return random.choice(NEGATIVE_TEMPLATES)
    return random.choice(NEUTRAL_TEMPLATES)


def pick_comment_template(sentiment):
    if sentiment == "pos":
        return random.choice(COMMENT_POS)
    elif sentiment == "neg":
        return random.choice(COMMENT_NEG)
    return random.choice(COMMENT_NEU)


def generate_posts():
    posts = []
    # Distribute sentiment: ~40% pos, 35% neg, 25% neutral
    sentiments = (["pos"] * 60) + (["neg"] * 52) + (["neu"] * 38)
    random.shuffle(sentiments)
    for i in range(TARGET_POSTS):
        s = sentiments[i % len(sentiments)]
        topic = TOPICS[i % len(TOPICS)]
        platform = PLATFORMS[i % len(PLATFORMS)]
        tmpl = pick_template(s)
        raw = tmpl.format(topic=topic)
        post = {
            "post_id": f"POST_{i+1:04d}",
            "platform": platform,
            "username": random.choice(USERNAMES),
            "topic": topic,
            "raw_text": raw,
            "likes": random.randint(0, 5000),
            "shares": random.randint(0, 1000),
            "created_at": rand_datetime(),
            "_sentiment_hint": s,
        }
        posts.append(post)
    return posts


def generate_comments(posts):
    comments = []
    cid = 1
    per_post = TARGET_COMMENTS // TARGET_POSTS
    extra = TARGET_COMMENTS - (per_post * TARGET_POSTS)
    for idx, post in enumerate(posts):
        n = per_post + (1 if idx < extra else 0)
        for _ in range(n):
            s = post["_sentiment_hint"] if random.random() < 0.6 else random.choice(["pos", "neg", "neu"])
            tmpl = pick_comment_template(s)
            raw = tmpl.format(topic=post["topic"])
            comments.append({
                "comment_id": f"CMT_{cid:05d}",
                "post_id": post["post_id"],
                "username": random.choice(USERNAMES),
                "topic": post["topic"],
                "platform": post["platform"],
                "raw_text": raw,
                "likes": random.randint(0, 500),
                "created_at": rand_datetime(90),
            })
            cid += 1
    return comments


def process_records(records):
    for r in records:
        r["cleaned_text"] = clean_text(r["raw_text"])
        sentiment = analyze(r["raw_text"])
        r.update(sentiment)
    return records


def run_mapreduce_simulation(all_records):
    """Local Python simulation of Hadoop MapReduce."""
    from collections import defaultdict
    sentiment_counts = defaultdict(int)
    topic_sentiment = defaultdict(int)
    topic_compound_sum = defaultdict(float)
    topic_compound_cnt = defaultdict(int)

    for r in all_records:
        label = r.get("sentiment_label", "Unknown")
        topic = r.get("topic", "Unknown")
        compound = r.get("compound_score", 0.0)
        sentiment_counts[label] += 1
        topic_sentiment[f"{topic}::{label}"] += 1
        topic_compound_sum[topic] += compound
        topic_compound_cnt[topic] += 1

    result = {
        "mode": "Local Python Simulation ",
        "overall_sentiment": dict(sentiment_counts),
        "topic_sentiment": dict(topic_sentiment),
        "topic_avg_compound": {
            t: round(topic_compound_sum[t] / topic_compound_cnt[t], 4)
            for t in topic_compound_sum
        },
    }

    os.makedirs("data", exist_ok=True)
    with open(MR_OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print("\n[MapReduce] Local simulation complete .")
    print(f"[MapReduce] Output saved to: {MR_OUTPUT_FILE}")
    print("[MapReduce] Overall Sentiment:", dict(sentiment_counts))
    return result


def main():
    print("=" * 60)
    print("  Social Media Sentiment Analysis — Data Pipeline")
    print("=" * 60)

    # Init DB
    db.init_db()
    print(f"[Storage] Mode: {db.storage_mode()}\n")

    print("[1/5] Generating synthetic dataset...")
    random.seed(42)
    posts = generate_posts()
    comments = generate_comments(posts)

    print(f"       Posts: {len(posts)}, Comments: {len(comments)}")

    print("[2/5] Preprocessing and sentiment analysis...")
    posts = process_records(posts)
    comments = process_records(comments)

    # Remove internal hint key
    for p in posts:
        p.pop("_sentiment_hint", None)

    print("[3/5] Storing records...")
    db.upsert_posts(posts)
    db.upsert_comments(comments)

    # Save combined JSON regardless (for dashboard)
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"posts": posts, "comments": comments}, f, indent=2, default=str)
    print(f"       Data saved to {DATA_FILE}")

    all_records = posts + comments
    total = len(all_records)
    pos = sum(1 for r in all_records if r["sentiment_label"] == "Positive")
    neg = sum(1 for r in all_records if r["sentiment_label"] == "Negative")
    neu = sum(1 for r in all_records if r["sentiment_label"] == "Neutral")
    print(f"       Total: {total} | Positive: {pos} | Negative: {neg} | Neutral: {neu}")

    print("[4/5] Running MapReduce (local simulation)...")
    run_mapreduce_simulation(all_records)

    print("[5/5] Pipeline complete.")
    print("\nAll done! Run the dashboard with:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()

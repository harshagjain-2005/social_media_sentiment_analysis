# config.py - Project Configuration

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "social_media_sentiment"
POSTS_COLLECTION = "posts"
COMMENTS_COLLECTION = "comments"

DATA_FILE = "data/social_media_data.json"
MR_OUTPUT_FILE = "data/mapreduce_output.json"

SENTIMENT_THRESHOLDS = {
    "positive": 0.05,
    "negative": -0.05,
}

PLATFORMS = ["Twitter/X", "Reddit", "Instagram", "Threads"]
TOPICS = [
    "Artificial Intelligence",
    "Smartphones",
    "Electric Vehicles",
    "Gaming",
    "Streaming Movies",
    "Customer Service",
]

TARGET_POSTS = 150
TARGET_COMMENTS = 521

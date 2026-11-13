# database/mongo_handler.py

import json
import os
from datetime import datetime

_USE_MONGO = False
_db = None
_fallback_data = {"posts": [], "comments": []}
_FALLBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "social_media_data.json")


def _load_fallback():
    global _fallback_data
    if os.path.exists(_FALLBACK_FILE):
        with open(_FALLBACK_FILE, "r", encoding="utf-8") as f:
            _fallback_data = json.load(f)


def init_db():
    global _USE_MONGO, _db
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        _db = client["social_media_sentiment"]
        _USE_MONGO = True
        print("[DB] MongoDB connected successfully.")
    except Exception:
        _USE_MONGO = False
        _load_fallback()
        print("[DB] MongoDB unavailable — using local JSON fallback.")
    return _USE_MONGO


def storage_mode():
    return "MongoDB" if _USE_MONGO else "Local JSON Fallback"


def upsert_posts(records: list):
    if _USE_MONGO:
        col = _db["posts"]
        for r in records:
            col.update_one({"post_id": r["post_id"]}, {"$set": r}, upsert=True)
    else:
        _fallback_data["posts"] = records
        _save_fallback()


def upsert_comments(records: list):
    if _USE_MONGO:
        col = _db["comments"]
        for r in records:
            col.update_one({"comment_id": r["comment_id"]}, {"$set": r}, upsert=True)
    else:
        _fallback_data["comments"] = records
        _save_fallback()


def get_posts():
    if _USE_MONGO:
        return list(_db["posts"].find({}, {"_id": 0}))
    return _fallback_data.get("posts", [])


def get_comments():
    if _USE_MONGO:
        return list(_db["comments"].find({}, {"_id": 0}))
    return _fallback_data.get("comments", [])


def _save_fallback():
    os.makedirs(os.path.dirname(_FALLBACK_FILE), exist_ok=True)
    with open(_FALLBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(_fallback_data, f, indent=2, default=str)

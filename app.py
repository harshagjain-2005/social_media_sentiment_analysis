# app.py — Streamlit Dashboard

import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import DATA_FILE, MR_OUTPUT_FILE
from database import mongo_handler as db
from sentiment.analyzer import analyze
from preprocessing.text_cleaner import clean_text
from visualization.charts import (
    sentiment_pie, topic_sentiment_bar, platform_sentiment_bar,
    compound_distribution, top_keywords
)

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Social Media Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {font-size:2.2rem; font-weight:800; color:#2c3e50; margin-bottom:0;}
    .sub-title  {font-size:1rem;  color:#7f8c8d; margin-bottom:1.5rem;}
    .kpi-card   {background:#f8f9fa; border-radius:12px; padding:18px 24px;
                 text-align:center; border-left:5px solid #3498db; box-shadow:0 2px 8px rgba(0,0,0,.08);}
    .kpi-value  {font-size:2rem; font-weight:700;}
    .kpi-label  {font-size:.85rem; color:#7f8c8d; margin-top:4px;}
    .pos-card   {border-left-color:#2ecc71 !important;}
    .neg-card   {border-left-color:#e74c3c !important;}
    .neu-card   {border-left-color:#3498db !important;}
    .tot-card   {border-left-color:#9b59b6 !important;}
    section[data-testid="stSidebar"] {background:#2c3e50;}
    section[data-testid="stSidebar"] * {color:#ecf0f1 !important;}
</style>
""", unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    db.init_db()
    posts    = db.get_posts()
    comments = db.get_comments()
    if not posts and os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        posts    = d.get("posts", [])
        comments = d.get("comments", [])
    all_rec = posts + comments
    return posts, comments, all_rec


posts, comments, all_records = load_data()
df_all  = pd.DataFrame(all_records)
df_post = pd.DataFrame(posts)

# Load MapReduce output
mr_result = {}
if os.path.exists(MR_OUTPUT_FILE):
    with open(MR_OUTPUT_FILE) as f:
        mr_result = json.load(f)

storage_mode = db.storage_mode()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    topics    = ["All"] + sorted(df_all["topic"].unique().tolist()) if "topic" in df_all.columns else ["All"]
    platforms = ["All"] + sorted(df_all["platform"].dropna().unique().tolist()) if "platform" in df_all.columns else ["All"]
    sentiments = ["All", "Positive", "Negative", "Neutral"]

    sel_topic     = st.selectbox("Topic",     topics)
    sel_platform  = st.selectbox("Platform",  platforms)
    sel_sentiment = st.selectbox("Sentiment", sentiments)

    st.markdown("---")
    st.markdown(f"**Storage Mode:** `{storage_mode}`")
    if mr_result:
        st.markdown(f"**MapReduce:** `{mr_result.get('mode','N/A')}`")
    st.markdown("---")
    st.markdown("Team -04 ")


# ── Filter Logic ──────────────────────────────────────────────────────────
filtered = all_records[:]
if sel_topic != "All":
    filtered = [r for r in filtered if r.get("topic") == sel_topic]
if sel_platform != "All":
    filtered = [r for r in filtered if r.get("platform") == sel_platform]
if sel_sentiment != "All":
    filtered = [r for r in filtered if r.get("sentiment_label") == sel_sentiment]


# ── Header ────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📊 Social Media Sentiment Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Python · NLTK VADER · MongoDB · Hadoop MapReduce  |  Team -04 </p>', unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────
total = len(filtered)
pos   = sum(1 for r in filtered if r.get("sentiment_label") == "Positive")
neg   = sum(1 for r in filtered if r.get("sentiment_label") == "Negative")
neu   = sum(1 for r in filtered if r.get("sentiment_label") == "Neutral")

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card tot-card"><div class="kpi-value" style="color:#9b59b6">{total}</div><div class="kpi-label">Total Records</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card pos-card"><div class="kpi-value" style="color:#2ecc71">{pos}</div><div class="kpi-label">😊 Positive</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card neg-card"><div class="kpi-value" style="color:#e74c3c">{neg}</div><div class="kpi-label">😠 Negative</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card neu-card"><div class="kpi-value" style="color:#3498db">{neu}</div><div class="kpi-label">😐 Neutral</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### 🥧 Sentiment Distribution")
    if filtered:
        st.image(sentiment_pie(filtered), use_container_width=True)
    else:
        st.info("No data for selected filters.")

with col2:
    st.markdown("### 📊 Topic-wise Sentiment")
    if filtered:
        st.image(topic_sentiment_bar(filtered), use_container_width=True)
    else:
        st.info("No data.")

# ── Charts Row 2 ──────────────────────────────────────────────────────────
col3, col4 = st.columns(2)
with col3:
    st.markdown("### 🌐 Platform-wise Sentiment")
    if filtered:
        st.image(platform_sentiment_bar(filtered), use_container_width=True)
    else:
        st.info("No data.")

with col4:
    st.markdown("### 📈 Compound Score Distribution")
    if filtered:
        st.image(compound_distribution(filtered), use_container_width=True)
    else:
        st.info("No data.")

# ── Top Keywords ──────────────────────────────────────────────────────────
st.markdown("### 🔑 Top Keywords")
kw1, kw2 = st.columns(2)
with kw1:
    st.image(top_keywords(filtered, "Positive"), use_container_width=True)
with kw2:
    st.image(top_keywords(filtered, "Negative"), use_container_width=True)

# ── MapReduce Results ──────────────────────────────────────────────────────
if mr_result:
    with st.expander("⚙️ MapReduce Results", expanded=False):
        st.info(f"**Mode:** {mr_result.get('mode', 'N/A')}")
        col_mr1, col_mr2 = st.columns(2)
        with col_mr1:
            st.markdown("**Overall Sentiment Counts**")
            st.json(mr_result.get("overall_sentiment", {}))
        with col_mr2:
            st.markdown("**Topic Avg Compound Score**")
            st.json(mr_result.get("topic_avg_compound", {}))

# ── Searchable Records Table ───────────────────────────────────────────────
st.markdown("### 🗃️ Records Explorer")
search_term = st.text_input("🔎 Search in text", placeholder="e.g. amazing, disappointed, AI...")

display_df = pd.DataFrame(filtered)
if search_term and not display_df.empty:
    mask = display_df["raw_text"].str.contains(search_term, case=False, na=False)
    display_df = display_df[mask]

COLS = [c for c in ["post_id","comment_id","platform","username","topic","sentiment_label",
                     "compound_score","raw_text","created_at"] if c in display_df.columns]
if not display_df.empty:
    st.dataframe(display_df[COLS].reset_index(drop=True), use_container_width=True, height=320)
    st.caption(f"Showing {len(display_df)} records")
else:
    st.info("No records match.")

# ── Live Sentiment Analyzer ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💬 Analyze a New Post Instantly")
user_text = st.text_area("Enter social media text:", placeholder="Type or paste a post here...", height=100)
if st.button("🔍 Analyze Sentiment", type="primary") and user_text.strip():
    cleaned = clean_text(user_text)
    result  = analyze(user_text)
    label   = result["sentiment_label"]
    emoji   = "😊" if label == "Positive" else ("😠" if label == "Negative" else "😐")
    color   = "#2ecc71" if label == "Positive" else ("#e74c3c" if label == "Negative" else "#3498db")
    st.markdown(f"""
    <div style="background:#f8f9fa;border-radius:12px;padding:20px;border-left:6px solid {color};margin-top:10px;">
        <h3 style="color:{color};margin:0">{emoji} {label}</h3>
        <p style="margin:8px 0 4px 0;color:#555"><strong>Compound Score:</strong> {result['compound_score']}</p>
        <p style="margin:4px 0;color:#555">Pos: {result['pos_score']} · Neg: {result['neg_score']} · Neu: {result['neu_score']}</p>
        <p style="margin:8px 0 0 0;color:#888;font-size:.85rem"><strong>Cleaned:</strong> {cleaned}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🎓 Team -04 ")

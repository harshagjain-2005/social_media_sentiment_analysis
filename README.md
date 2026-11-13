# Social Media Sentiment Analysis

**Big Data Analytics (BIS701)**  
Department of Information Science and Engineering  
Acharya Institute of Technology, Bengaluru

---

## 👥 Team — Group 1

| # | Name | USN |
|---|------|-----|
| 1 | CHIRAG URS C | 1AY23IS031 |
| 2 | DEEPAK Y C | 1AY23IS032 |
| 3 | DEEPIKA A L | 1AY23IS033 |
| 4 | DHARSHAN G | 1AY23IS034 |
| 5 | GAURAV AKSHAY KARDONI | 1AY23IS035 |
| 6 | GIRISH K | 1AY23IS036 |
| 7 | HARSHA C | 1AY23IS037 |
| 8 | HARSHA G JAIN | 1AY23IS038 |
| 9 | HARSHAVARDHAN H N | 1AY23IS039 |
| 10 | HARSHITH K V | 1AY23IS040 |

**Guide:** Prof. YOGESH N

---

## 📋 Project Overview

A complete Big Data Analytics pipeline that collects synthetic social media posts and comments, preprocesses them, classifies sentiment using NLTK VADER, stores results in MongoDB (with JSON fallback), runs a Hadoop MapReduce simulation, and visualizes insights via an interactive Streamlit dashboard.

### Technology Stack
| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Sentiment Analysis | NLTK VADER |
| Text Preprocessing | NLTK + Regex |
| Database | MongoDB (PyMongo) + JSON fallback |
| Big Data Processing | Hadoop Streaming MapReduce (Python) |
| Visualization | Matplotlib |
| Dashboard | Streamlit |

---

## 🗂️ Project Structure

```
social_media_sentiment_analysis/
├── app.py                  # Streamlit dashboard
├── main.py                 # Data pipeline (generate → analyze → store → MapReduce)
├── config.py               # Configuration constants
├── requirements.txt        # Python dependencies
├── README.md
├── data/
│   ├── social_media_data.json     # Generated dataset
│   └── mapreduce_output.json      # MapReduce simulation results
├── preprocessing/
│   └── text_cleaner.py     # URL/mention/hashtag removal, lemmatization
├── sentiment/
│   └── analyzer.py         # VADER sentiment classification
├── database/
│   └── mongo_handler.py    # MongoDB + JSON fallback handler
├── mapreduce/
│   ├── mapper.py           # Hadoop Streaming mapper
│   └── reducer.py          # Hadoop Streaming reducer
└── visualization/
    └── charts.py           # Matplotlib chart generators
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the data pipeline
```bash
cd social_media_sentiment_analysis
python main.py
```
This will:
- Generate 150 posts + 521 comments (671 total synthetic records)
- Preprocess text (remove URLs, mentions, hashtags; lemmatize)
- Classify sentiment with NLTK VADER
- Store results in MongoDB (or JSON fallback if MongoDB is unavailable)
- Run MapReduce simulation and save output

### 3. Launch the dashboard
```bash
streamlit run app.py
```

---

## 📊 Dataset Details

- **Posts:** 150 (Twitter/X, Reddit, Instagram, Threads)
- **Comments:** 521
- **Total Records:** 671
- **Topics:** Artificial Intelligence, Smartphones, Electric Vehicles, Gaming, Streaming Movies, Customer Service
- **Data is synthetic** — generated programmatically for academic demonstration purposes

---

## ⚙️ Hadoop MapReduce

### Local Simulation (default)
Run automatically via `main.py`. Output saved to `data/mapreduce_output.json`.

### Real Hadoop Streaming (if Hadoop is installed)
```bash
# Prepare input
python -c "
import json
with open('data/social_media_data.json') as f:
    d = json.load(f)
all_r = d['posts'] + d['comments']
with open('/tmp/mr_input.txt', 'w') as out:
    for r in all_r:
        out.write(json.dumps(r) + '\n')
"

# Run Hadoop job
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapreduce/mapper.py,mapreduce/reducer.py \
  -mapper "python mapper.py" \
  -reducer "python reducer.py" \
  -input /tmp/mr_input.txt \
  -output /tmp/mr_output
```

---

## 💡 Sentiment Thresholds (VADER)

| Compound Score | Label |
|----------------|-------|
| ≥ +0.05 | Positive |
| ≤ −0.05 | Negative |
| Between −0.05 and +0.05 | Neutral |

---

## 📌 Notes

- MongoDB is optional. If not running, the app automatically uses `data/social_media_data.json` as fallback.
- The dashboard shows storage mode and MapReduce mode in the sidebar.
- Hadoop Streaming scripts (`mapper.py`, `reducer.py`) are real and compatible with Hadoop Streaming.
- Local simulation is clearly labeled — no fabricated Hadoop results.

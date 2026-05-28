# 🌳 TATA IPL EcoDot Analytics — Turning Dot Balls Into Trees! 🏏

Welcome to the **TATA IPL EcoDot Analytics** project! This is an interactive data analytics and machine learning dashboard that tracks, visualizes, and models the environmental impact of the **TATA IPL Green Dot Ball Initiative**.

## 📖 The Backstory: What is the Green Dot Ball Initiative?

In **2023**, the BCCI partnered with the TATA Group to launch a groundbreaking sustainability initiative. In T20 cricket, a scoreless delivery is called a **"dot ball"** (because it is recorded as a simple dot on the scorecard). To turn these pressure-building deliveries into a force for ecological good, the broadcasters replaced the traditional white dot icon on the television screen with an animated **🌳 tree icon**. 

For every single dot ball bowled during the initiative's matches, the TATA Group commits to planting saplings across various eco-sensitive regions in India (such as Assam, Kerala, Gujarat, Karnataka, Maharashtra, and Himachal Pradesh).

The initiative has expanded rapidly season-over-season:
1.  **IPL 2023 (Pilot Launch):** Active during the **Playoffs only** (4 matches). Pledged **500 trees** per dot ball.
    *   *Result:* 294 dot balls bowled → **147,000 trees** planted.
2.  **IPL 2024 (Expanded Pilot):** Active during the **Playoffs only** (4 matches). Pledged **500 trees** per dot ball.
    *   *Result:* 323 dot balls bowled → **161,500 trees** planted.
3.  **IPL 2025 (Full Scale-up):** Expanded to cover **all 74 matches** of the tournament. The rate was set to **18 trees** per dot ball to mark the 18th edition of the IPL.
    *   *Result:* 5,562 dot balls bowled → **100,116 trees** planted.
4.  **IPL 2026 (Current Season):** Active for the **entire season**. Pledged **19 trees** per dot ball for all **70 League matches** (marking the 19th IPL edition) and **500 trees** per dot ball for the **Playoff matches**.
    *   *Result (League Stage):* 5,141 dot balls bowled → **97,679 trees** planted so far.

---

## 🎯 What This Project Does

While standard sports dashboards focus heavily on runs, wickets, boundaries, and strike rates, this project bridges the gap between **high-octane cricket analytics** and **real-world ecological sustainability**.

Using ball-by-ball raw match data sourced from **Cricsheet.org** and combining it with official sustainability figures from **greendotball.com**, this project provides a full-stack data pipeline:
*   **ETL Data Pipeline:** Processes and cleans raw Cricsheet JSON files (dating back to 2008) to isolate dot balls, calculate dynamic tree plantation rates, and determine CO₂ offset figures (at the standard IPCC rate of **21.77 kg of CO₂ absorbed per tree per year**).
*   **Interactive Streamlit Dashboard:** Features a gorgeous, dark-themed dashboard packed with rich micro-animations, glassmorphic styles, and interactive charts displaying overview trends, bowler/batter stats, venue analysis, and sustainability impact trackers.
*   **Machine Learning Model:** Uses a **Random Forest Regressor** to predict the number of dot balls and corresponding tree plantations for future matchups based on the venue, batting team, and season.

---

## 📁 Repository Structure

```files
├── Datasets/
│   ├── raw/
│   │   └── Cricsheet/          # 1,200+ raw ball-by-ball match JSON files
│   ├── processed/
│   │   ├── ipl_dot_ball_dataset.csv      # Consolidated cleaned dataset (290k+ rows)
│   │   └── ipl_dot_ball_dataset.parquet  # Optimized parquet format for rapid loading
│   └── sustainability/
│       ├── green_dot_ball_initiative.csv  # Season-level official benchmarks
│       └── green_dot_ball_per_match.csv   # Per-match playoff breakdowns
├── dashboard/
│   └── app.py                  # Streamlit dashboard application
├── scripts/
│   ├── etl_pipeline.py         # Parses Cricsheet JSONs, unifies names, and computes trees
│   ├── analytics_engine.py     # Generates static Plotly visualizations
│   └── ml_model.py             # Random Forest regressor for dot-ball predictions
├── requirements.txt            # Python dependencies (for easy cloud deployment)
└── README.md                   # You are here!
```

---

## 💻 Tech Stack & Design System
*   **Core Logic:** Python 3.10+
*   **Data Processing:** Pandas, PyArrow
*   **Visualizations:** Plotly Express, Plotly Graph Objects
*   **Web Framework:** Streamlit
*   **Machine Learning:** Scikit-Learn
*   **Design Language:** HSL-tailored dark modes, smooth gradients, premium typography (`Inter` via Google Fonts), and responsive micro-animations.

---

## 🚀 Running the Project Locally

### 1. Clone the repository & Install Dependencies
First, install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Run the ETL Pipeline
To process the raw match files, unify team names (e.g., merging "Royal Challengers Bangalore" and "Royal Challengers Bengaluru" historical records), and regenerate the processed datasets, run:
```bash
python scripts/etl_pipeline.py
```

### 3. Launch the Dashboard
Run the Streamlit application:
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8504` in your browser.

### 4. Run the ML Pipeline
To train the Random Forest regressor and print model performance metrics, run:
```bash
python scripts/ml_model.py
```

---

## 📊 Core Dashboard Tabs

1.  **📊 Overview:** Visualizes season-wise dot ball frequencies, percentage trends, phase breakdowns (Powerplay vs. Middle vs. Death overs), and overall team leaderboards.
2.  **🏟️ Match Records:** Showcases individual match extremes—highest and lowest dot ball counts, highest percentage dot ball matches, and distributions.
3.  **🎯 Bowler Insights:** Features the **Green Impact Score** to rank the tournament's most eco-friendly bowlers based on cumulative dot balls bowled and economy rates.
4.  **🏏 Batter Insights:** Ranks batters by dot ball percentages, isolating aggressive run-scorers who avoid dot balls vs. defensive players.
5.  **📍 Venue Analysis:** Evaluates which stadiums are bowler-friendly (high dot-ball ratio) vs. batter-friendly, complete with a beautiful **Venue × Season Heatmap**.
6.  **🌿 Eco Impact:** The crown jewel tab! Auto-calculates cumulative trees planted, presents a dynamic season-by-season legend, displays pledged vs. planted overlay comparison charts, and provides annual $CO_2$ offset metrics.

---

## 🌿 Data Source and Verification
*   **Match Data:** [Cricsheet.org](https://cricsheet.org) (Open-source ball-by-ball cricket data).
*   **Initiative Data:** [greendotball.com](https://greendotball.com) (Official TATA Green Dot Ball initiative web app).
*   **CO₂ Metrics:** Calculated based on the standard IPCC estimate of **21.77 kg** $CO_2$ offset per tree per year.

Feel free to open an issue or submit a pull request if you'd like to contribute to this sustainability tracker! 🌳✨

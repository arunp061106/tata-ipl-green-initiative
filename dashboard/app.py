import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import textwrap

# Wrap st.markdown to automatically dedent multiline strings, preventing indented HTML from being parsed as code blocks
_original_markdown = st.markdown
def _custom_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        body = textwrap.dedent(body)
    return _original_markdown(body, *args, **kwargs)
st.markdown = _custom_markdown

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="EcoDot Analytics — Tata IPL",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
# OFFICIAL INITIATIVE DATA  (from greendotball.com)
# ══════════════════════════════════════════════════════════════════

# Real data per season — verified from official sources
INITIATIVE = {
    2023: {
        "scope":          "Playoffs Only",
        "trees_per_dot":  500,
        "dot_balls":      294,       # actual dots in 4 playoff matches
        "trees_pledged":  147_000,
        "trees_planted":  147_000,   # confirmed planted
        "matches":        4,
        "color":          "#3fb950",
        "icon":           "🌱",
        "note":           "Pilot: Q1, Eliminator, Q2 & Final",
    },
    2024: {
        "scope":          "Playoffs Only",
        "trees_per_dot":  500,
        "dot_balls":      323,       # Q1(73)+Elim(74)+Q2(96)+Final(80)
        "trees_pledged":  161_500,
        "trees_planted":  161_500,   # confirmed planted
        "matches":        4,
        "color":          "#58a6ff",
        "icon":           "🌿",
        "note":           "KKR vs SRH Final · 323 dots across 4 playoffs",
    },
    2025: {
        "scope":          "Full Season",
        "trees_per_dot":  18,        # 18 trees for 18th IPL edition
        "dot_balls":      5562,      # official figure from greendotball.com
        "trees_pledged":  100_116,
        "trees_planted":  100_116,   # confirmed planted
        "matches":        74,
        "color":          "#f0a500",
        "icon":           "🌳",
        "note":           "Full 74-match season · 18 trees = 18th IPL edition",
    },
    2026: {
        "scope":          "Full Season",
        "trees_per_dot":  "19 / 500",  # League: 19 / Playoffs: 500
        "dot_balls":      0,
        "trees_pledged":  0,
        "trees_planted":  0,
        "matches":        0,
        "color":          "#ec7211",
        "icon":           "🌲",
        "note":           "19 trees/dot for 70 League matches (19th IPL edition) · 500 trees/dot for Playoffs",
    },
}

CUMULATIVE_ALL = 641_166   # IPL + WPL combined from greendotball.com

CO2_PER_TREE   = 21.77     # kg CO2 per tree per year (IPCC)

# Paths
DATA_PATH      = os.path.join("Datasets", "processed", "ipl_dot_ball_dataset.csv")
INIT_CSV       = os.path.join("Datasets", "sustainability", "green_dot_ball_initiative.csv")
MATCH_CSV      = os.path.join("Datasets", "sustainability", "green_dot_ball_per_match.csv")

PLOT_THEME     = "plotly_dark"
MIN_BOW_BALLS  = 300
MIN_BAT_BALLS  = 200

_LAY = dict(
    plot_bgcolor ="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font         =dict(family="Inter, sans-serif", color="#c9d1d9"),
    title_font   =dict(size=15, color="#e6edf3"),
    legend       =dict(bgcolor="rgba(0,0,0,0)", bordercolor="#21262d"),
    margin       =dict(t=55, b=30, l=20, r=20),
)

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

.stApp{background:linear-gradient(135deg, #07090e 0%, #0d121f 50%, #07170e 100%) !important;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#07090e,#0d121f);border-right:1px solid #1f2a3d;}

/* Glassmorphism Metric cards */
div[data-testid="metric-container"]{
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.6), rgba(26, 35, 50, 0.6)) !important;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(46,160,67,.2) !important;
    border-radius:14px;padding:16px 20px;
    box-shadow:0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
div[data-testid="metric-container"]:hover{
    transform:translateY(-3px);
    border-color: rgba(46,160,67,.5) !important;
    box-shadow:0 12px 40px rgba(46,160,67,.25);
}
div[data-testid="metric-container"] label{color:#8b949e!important;font-size:.72rem!important;letter-spacing:.08em;text-transform:uppercase;}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{color:#2ea043!important;font-size:1.65rem!important;font-weight:700!important;text-shadow: 0 0 10px rgba(46,160,67,0.25);}

h1{color:#e6edf3!important;letter-spacing:-.5px;}
h2{color:#c9d1d9!important;}
h3{color:#8b949e!important;font-size:1rem!important;}
hr{border-color:#1f2a3d;}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"]{gap:6px;background:transparent;border-bottom:1px solid #1f2a3d;padding-bottom:6px;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{background:#0d121f;border-radius:8px;color:#8b949e;border:1px solid #1f2a3d;padding:7px 16px;font-size:.85rem;font-weight:500;transition:all .2s;}
.stTabs [data-baseweb="tab"]:hover{background:#1a2332;color:#c9d1d9;border-color:#2ea043;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#123824,#2ea043)!important;color:#fff!important;border-color:#2ea043!important;box-shadow:0 2px 12px rgba(46,160,67,.45);}

.js-plotly-plot{border-radius:12px;overflow:hidden;box-shadow:0 8px 32px 0 rgba(0,0,0,0.4);border: 1px solid rgba(255,255,255,0.05);}
.stDataFrame{border:1px solid #1f2a3d;border-radius:10px;overflow:hidden;}

/* Premium Glass Cards */
.glass-card {
    background: rgba(13, 18, 31, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(46, 160, 67, 0.15);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
    margin-bottom: 20px;
    transition: all 0.3s ease-in-out;
}
.glass-card:hover {
    transform: translateY(-2px);
    border-color: rgba(46, 160, 67, 0.35);
    box-shadow: 0 12px 40px 0 rgba(46, 160, 67, 0.15);
}

/* Sustainability Pipeline funnel */
.funnel-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin: 15px 0 10px 0;
}
.funnel-step {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.7), rgba(26, 35, 50, 0.7));
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}
.funnel-step::after {
    content: "➔";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    color: rgba(46, 160, 67, 0.4);
    z-index: 2;
}
@media (max-width: 992px) {
    .funnel-step::after { content: "▼"; right: auto; bottom: -15px; left: 50%; transform: translateX(-50%); top: auto; }
}
.funnel-step:last-child::after {
    display: none;
}
.funnel-step:hover {
    transform: translateY(-4px) scale(1.02);
    border-color: rgba(46, 160, 67, 0.4);
    box-shadow: 0 8px 25px rgba(46, 160, 67, 0.15);
}
.funnel-step-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 6px;
}
.funnel-step-value {
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 8px 0;
}
.funnel-step-sub {
    font-size: 0.75rem;
    color: #8b949e;
}

/* Season legend cards */
.season-card{
    border-radius:14px;padding:20px;text-align:center;
    box-shadow:0 8px 32px 0 rgba(0,0,0,0.35);
    transition:transform .2s,box-shadow .2s;
}
.season-card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.45);}

/* Info banner & Analytical Tips */
.info-banner{
    background:linear-gradient(135deg,#0d1627,#161b22);
    border:1px solid #1f2a3d;border-left:4px solid #2ea043;
    border-radius:0 10px 10px 0;padding:14px 18px;margin:12px 0;
}
.tip-card {
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.5), rgba(46, 160, 67, 0.05));
    border: 1px solid rgba(46, 160, 67, 0.2);
    border-left: 4px solid #2ea043;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    font-size: 0.88rem;
    color: #c9d1d9;
    line-height: 1.5;
}

/* Vertical Funnel classes */
.funnel-container-vertical {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 15px 0 10px 0;
}
.funnel-step-vertical {
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.7), rgba(26, 35, 50, 0.7));
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 15px 20px;
    text-align: center;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}
.funnel-step-vertical::after {
    content: "▼";
    position: absolute;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.1rem;
    color: rgba(46, 160, 67, 0.5);
    z-index: 2;
}
.funnel-step-vertical:last-child::after {
    display: none;
}
.funnel-step-vertical:hover {
    transform: translateY(-2px) scale(1.01);
    border-color: rgba(46, 160, 67, 0.4);
    box-shadow: 0 8px 25px rgba(46, 160, 67, 0.15);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DATA LOAD
# ══════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_csv(path, mtime):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

with st.spinner("🌱 Loading data..."):
    mtime_df = os.path.getmtime(DATA_PATH) if os.path.exists(DATA_PATH) else 0
    mtime_init = os.path.getmtime(INIT_CSV) if os.path.exists(INIT_CSV) else 0
    mtime_match = os.path.getmtime(MATCH_CSV) if os.path.exists(MATCH_CSV) else 0
    
    df      = load_csv(DATA_PATH, mtime_df)
    init_df = load_csv(INIT_CSV, mtime_init)
    pmatch  = load_csv(MATCH_CSV, mtime_match)

# Populate 2026 dynamically from data if it exists
if not df.empty and 2026 in df["season"].values:
    df_2026 = df[df["season"] == 2026]
    dot_balls_2026 = int(df_2026["is_dot_ball"].sum())
    trees_2026 = int(df_2026["trees_generated"].sum())
    matches_2026 = int(df_2026["match_id"].nunique())
    
    INITIATIVE[2026]["dot_balls"] = dot_balls_2026
    INITIATIVE[2026]["trees_pledged"] = trees_2026
    INITIATIVE[2026]["trees_planted"] = trees_2026
    INITIATIVE[2026]["matches"] = matches_2026

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <div style='font-size:2.8rem;'>🌳</div>
        <div style='color:#3fb950;font-size:1.2rem;font-weight:700;'>EcoDot Analytics</div>
        <div style='color:#8b949e;font-size:.75rem;margin-top:3px;'>Tata IPL Green Initiative</div>
    </div><hr>
    """, unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found! Run `scripts/etl_pipeline.py` first.")
        st.stop()

    seasons   = sorted(df["season"].dropna().unique().tolist())
    all_teams = sorted(df["batting_team"].dropna().unique().tolist())

    st.subheader("🔎 Filters")
    # Default to Green Dot Ball Initiative seasons (2023 onwards)
    default_seasons = [s for s in seasons if s >= 2023]
    selected_seasons = st.multiselect("Season(s)", seasons, default=default_seasons, key="sf")
    selected_teams   = st.multiselect("Team(s)", all_teams, default=all_teams, key="tf")
    selected_phase   = st.selectbox("Match Phase", ["All","Powerplay","Middle","Death"], key="pf")
    selected_venue   = st.selectbox("Venue", ["All"]+sorted(df["venue"].dropna().unique()), key="vf")

    st.markdown("<hr>", unsafe_allow_html=True)

    n_matches = df["match_id"].nunique()
    n_seasons = df["season"].nunique()
    n_teams   = df["batting_team"].nunique()
    total_ini = sum(v["trees_planted"] for v in INITIATIVE.values())

    st.markdown(f"""
    <div style='background:#161b22;border-radius:10px;padding:14px;text-align:center;border:1px solid #21262d;'>
        <div style='color:#8b949e;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>DATASET OVERVIEW</div>
        <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;'>
            <div><div style='color:#3fb950;font-size:1.1rem;font-weight:700;'>{n_matches:,}</div><div style='color:#8b949e;font-size:.65rem;'>Matches</div></div>
            <div><div style='color:#58a6ff;font-size:1.1rem;font-weight:700;'>{n_seasons}</div><div style='color:#8b949e;font-size:.65rem;'>Seasons</div></div>
            <div><div style='color:#f0a500;font-size:1.1rem;font-weight:700;'>{n_teams}</div><div style='color:#8b949e;font-size:.65rem;'>Teams</div></div>
        </div>
        <hr style='border-color:#21262d;margin:10px 0;'>
        <div style='color:#3fb950;font-size:.85rem;font-weight:600;'>🌳 {total_ini:,} IPL Trees Planted</div>
        <div style='color:#8b949e;font-size:.7rem;margin-top:2px;'>Since Initiative Launch (2023)</div>
    </div>
    <p style='color:#8b949e;font-size:.68rem;text-align:center;margin-top:10px;'>
        Source: greendotball.com<br>
        🌿 Initiative active: IPL 2023 onwards
    </p>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# FILTER
# ══════════════════════════════════════════════════════════════════

flt = df.copy()
if selected_seasons: flt = flt[flt["season"].isin(selected_seasons)]
if selected_teams:   flt = flt[flt["batting_team"].isin(selected_teams)]
if selected_phase != "All": flt = flt[flt["phase"] == selected_phase]
if selected_venue != "All": flt = flt[flt["venue"] == selected_venue]

# Aggregates
@st.cache_data(show_spinner=False)
def make_aggs(flt_hash, data):
    match_a = (
        data.groupby(["match_id","season","date","venue","match_number"])
        .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
             total_runs=("total_runs","sum"), wickets=("wicket","sum"),
             trees=("trees_generated","sum"), initiative=("initiative_active","max"))
        .reset_index()
    )
    teams = (data.groupby("match_id")["batting_team"]
             .apply(lambda x: " vs ".join(sorted(x.unique()))).reset_index()
             .rename(columns={"batting_team":"matchup"}))
    match_a = match_a.merge(teams, on="match_id", how="left")
    match_a["dot_pct"] = (match_a["dot_balls"]/match_a["total_balls"]*100).round(1)
    match_a["label"]   = match_a["matchup"]+" ("+match_a["season"].astype(str)+")"

    bow = (data.groupby("bowler")
           .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                wickets=("wicket","sum"), runs_given=("total_runs","sum"))
           .reset_index())
    bow["dot_pct"] = (bow["dot_balls"]/bow["total_balls"]*100).round(2)
    bow["economy"] = (bow["runs_given"]/bow["total_balls"]*6).round(2)

    bat = (data.groupby("batter")
           .agg(dot_balls_faced=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                runs_scored=("batter_runs","sum"), dismissals=("wicket","sum"))
           .reset_index())
    bat["dot_pct"]     = (bat["dot_balls_faced"]/bat["total_balls"]*100).round(2)
    bat["strike_rate"] = (bat["runs_scored"]/bat["total_balls"]*100).round(2)

    phase = (data.groupby("phase")
             .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"))
             .reset_index())
    phase["dot_pct"] = (phase["dot_balls"]/phase["total_balls"]*100).round(1)

    season = (data.groupby("season")
              .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                   trees=("trees_generated","sum"), co2=("co2_offset_kg","sum"),
                   matches=("match_id","nunique"))
              .reset_index().sort_values("season"))
    season["dot_pct"]    = (season["dot_balls"]/season["total_balls"]*100).round(1)
    season["dots_match"] = (season["dot_balls"]/season["matches"]).round(1)

    venue_t = (data.groupby("venue")
               .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                    matches=("match_id","nunique"), runs=("total_runs","sum"))
               .reset_index())
    venue_t["dot_pct"]    = (venue_t["dot_balls"]/venue_t["total_balls"]*100).round(1)
    venue_t["dots_match"] = (venue_t["dot_balls"]/venue_t["matches"]).round(1)

    venue_s = (data.groupby(["venue","season"])
               .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                    matches=("match_id","nunique"))
               .reset_index())
    venue_s["dot_pct"] = (venue_s["dot_balls"]/venue_s["total_balls"]*100).round(1)

    team = (data.groupby("batting_team")
            .agg(dot_balls=("is_dot_ball","sum"), total_balls=("is_dot_ball","count"),
                 runs=("total_runs","sum"), trees=("trees_generated","sum"))
            .reset_index())
    team["dot_pct"] = (team["dot_balls"]/team["total_balls"]*100).round(2)

    return match_a, bow, bat, phase, season, venue_t, venue_s, team

flt_hash = hash(tuple(selected_seasons) + tuple(selected_teams) + (selected_phase, selected_venue))
match_agg, bow_agg, bat_agg, phase_agg, season_agg, venue_agg, venue_season, team_agg = make_aggs(flt_hash, flt)

# Global KPIs
total_balls   = len(flt)
total_dots    = int(flt["is_dot_ball"].sum())
dot_pct_g     = (total_dots/total_balls*100) if total_balls else 0
total_trees   = flt["trees_generated"].sum()
total_co2     = flt["co2_offset_kg"].sum()
n_matches_flt = flt["match_id"].nunique()

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div style='padding:20px 0 6px;'>
    <h1 style='margin:0;font-size:2.3rem;font-weight:700;'>
        🌍 Tata IPL <span style='color:#3fb950;'>EcoDot</span> Analytics
    </h1>
    <p style='color:#8b949e;margin:8px 0 0;font-size:.95rem;'>
        Dot-ball intelligence &amp; sustainability impact ·
        <span style='color:#3fb950;font-weight:500;'>Green Dot Ball Initiative — IPL 2023 onwards</span>
    </p>
</div><hr>
""", unsafe_allow_html=True)

# KPI strip
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("🏏 Total Balls",    f"{total_balls:,}")
k2.metric("⚫ Dot Balls",      f"{total_dots:,}")
k3.metric("📊 Dot Ball %",    f"{dot_pct_g:.1f}%")
k4.metric("🏟️ Matches",       f"{n_matches_flt:,}")
k5.metric("🌳 Trees Planted",  f"{total_trees:,.0f}")
k6.metric("🌿 CO₂ Offset",    f"{total_co2:,.0f} kg")

# ══════════════════════════════════════════════════════════════════
# HERO SECTION — ECO-IMPACT HUB
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div style='margin: 10px 0 20px 0;'>
    <h2 style='margin-top:0;font-size:1.6rem;color:#e6edf3;font-weight:700;display:flex;align-items:center;gap:10px;'>
        🌳 Eco-Impact Hub <span style='background:rgba(46,160,67,0.15);color:#2ea043;font-size:0.75rem;padding:3px 10px;border-radius:20px;border:1px solid rgba(46,160,67,0.3);font-weight:600;'>Priority View</span>
    </h2>
</div>
""", unsafe_allow_html=True)

# Dynamic calculations based on selected seasons in the sidebar
selected_init_seasons = [s for s in selected_seasons if s in INITIATIVE]
if not selected_init_seasons:
    # fallback to show all seasons if none match the initiative years
    selected_init_seasons = list(INITIATIVE.keys())

hero_dots = sum(INITIATIVE[s]["dot_balls"] for s in selected_init_seasons)
hero_pledged = sum(INITIATIVE[s]["trees_pledged"] for s in selected_init_seasons)
hero_planted = sum(INITIATIVE[s]["trees_planted"] for s in selected_init_seasons)

hcol1, hcol2 = st.columns([2, 3])

with hcol1:
    st.html(f"""
    <div class="glass-card" style="height: 535px; display: flex; flex-direction: column; justify-content: space-between; padding: 20px 24px;">
        <div>
            <h3 style="margin-top: 0; color: #2ea043; font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                🌿 The Green Conversion Pipeline
            </h3>
            <p style="color: #8b949e; font-size: 0.82rem; margin-top: 4px; margin-bottom: 12px; line-height: 1.45;">
                From deliveries bowled on the pitch to trees growing in forests. 
                Below is the dynamic visual flow of the sustainability initiative for the selected seasons (<b>{", ".join(map(str, sorted(selected_init_seasons)))}</b>).
            </p>
        </div>
        
        <div class="funnel-container-vertical" style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; gap: 10px;">
            <div class="funnel-step-vertical">
                <div class="funnel-step-title">⚫ 1. Sowing Phase</div>
                <div class="funnel-step-value" style="color: #c9d1d9; font-size: 1.55rem; margin: 4px 0;">{hero_dots:,}</div>
                <div class="funnel-step-sub">Dot Balls Bowled</div>
            </div>
            <div class="funnel-step-vertical">
                <div class="funnel-step-title">📜 2. Commitment Phase</div>
                <div class="funnel-step-value" style="color: #f0a500; font-size: 1.55rem; margin: 4px 0;">{hero_pledged:,}</div>
                <div class="funnel-step-sub">Trees Pledged (to be planted)</div>
            </div>
            <div class="funnel-step-vertical">
                <div class="funnel-step-title">🌳 3. Harvest Phase</div>
                <div class="funnel-step-value" style="color: #2ea043; font-size: 1.55rem; margin: 4px 0;">✅ {hero_planted:,}</div>
                <div class="funnel-step-sub">Trees Actually Planted (Confirmed)</div>
            </div>
        </div>
        
        <div class="tip-card" style="margin-top: 15px; margin-bottom: 0; padding: 10px 14px; font-size: 0.78rem;">
            💡 <b>Did you know?</b> A single tree absorbs roughly <b>21.77 kg</b> of CO₂ annually. The {hero_planted:,} trees planted in these seasons offset approximately <b>{hero_planted * CO2_PER_TREE:,.0f} kg</b> of CO₂ per year!
        </div>
    </div>
    """)

with hcol2:
    # Aggregate data for the hero chart
    plot_seasons = sorted(selected_init_seasons)
    plot_dots = [INITIATIVE[s]["dot_balls"] for s in plot_seasons]
    plot_pledged = [INITIATIVE[s]["trees_pledged"] for s in plot_seasons]
    plot_planted = [INITIATIVE[s]["trees_planted"] for s in plot_seasons]

    # ── Beautiful summary horizontal bar chart ─────────────────────
    # Shows 3 key metrics as big, bold horizontal bars
    labels = [
        "⚫ Dot Balls Bowled",
        "📜 Trees To Be Planted",
        "🌳 Trees Actually Planted"
    ]
    values = [hero_dots, hero_pledged, hero_planted]
    colors = ["#58a6ff", "#f0a500", "#2ea043"]

    fig_hero = go.Figure()
    for i in range(3):
        fig_hero.add_trace(go.Bar(
            y=[labels[i]],
            x=[values[i]],
            orientation="h",
            marker=dict(
                color=colors[i],
                line=dict(color=colors[i], width=1),
                opacity=0.85,
            ),
            text=[f"  {values[i]:,}"],
            textposition="outside",
            textfont=dict(color=colors[i], size=18, family="Inter, sans-serif"),
            hovertemplate=f"<b>{labels[i]}</b><br>Value: %{{x:,}}<extra></extra>",
            showlegend=False,
        ))

    fig_hero.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#c9d1d9"),
        height=520,
        margin=dict(t=60, b=30, l=10, r=90),
        title=dict(
            text="📊 Green Conversion Pipeline — At a Glance",
            font=dict(color="#e6edf3", size=16),
            x=0.5,
            xanchor="center",
        ),
        xaxis=dict(
            title="Count",
            tickfont=dict(color="#8b949e", size=11),
            gridcolor="rgba(255, 255, 255, 0.04)",
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#e6edf3", size=13),
            categoryorder="array",
            categoryarray=list(reversed(labels)),
            gridcolor="rgba(0,0,0,0)",
        ),
        bargap=0.45,
    )

    st.plotly_chart(fig_hero, use_container_width=True)

st.markdown("<hr style='margin: 20px 0 25px 0; border-color: #1f2a3d;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🏟️ Match Records",
    "🎯 Bowler Insights",
    "🏏 Batter Insights",
    "📍 Venue Analysis",
    "🌿 Eco Impact",
])

# ──────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ──────────────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(season_agg, x="season", y="dot_balls",
                     color="dot_pct", color_continuous_scale="Tealgrn",
                     title="⚫ Total Dot Balls per Season",
                     labels={"season":"Season","dot_balls":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**_LAY, xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.line(season_agg, x="season", y="dot_pct", markers=True,
                      title="📈 Dot Ball % Trend",
                      labels={"season":"Season","dot_pct":"Dot %"},
                      color_discrete_sequence=["#3fb950"], template=PLOT_THEME)
        fig.update_traces(line_width=3, marker_size=9)
        fig.update_layout(**_LAY)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="glass-card" style="margin-top: 15px; margin-bottom: 20px; padding: 20px 24px;">
        <h3 style="margin-top: 0; color: #2ea043; font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
            🏏 Match Phase Dynamics: Volume vs. Density
        </h3>
        <p style="color: #8b949e; font-size: 0.85rem; margin-top: 4px; margin-bottom: 10px; line-height: 1.45;">
            Analyzing dot ball behavior by match phase reveals the difference between <b>Volume</b> (total count of dot balls bowled) and <b>Density</b> (the percentage of total deliveries in that phase that are dots).
        </p>
    </div>
    """, unsafe_allow_html=True)

    c3, c4 = st.columns([2,3])
    with c3:
        fig = px.pie(phase_agg, values="dot_balls", names="phase", hole=.48,
                     title="🏏 Dot Balls Volume by Phase",
                     color_discrete_sequence=["#2ea043","#58a6ff","#f0a500"],
                     template=PLOT_THEME)
        fig.update_traces(textinfo="percent+label", pull=[.04]*3, textfont_size=13)
        fig.update_layout(**_LAY)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.bar(phase_agg.sort_values("dot_pct", ascending=False),
                     x="phase", y="dot_pct", color="phase",
                     color_discrete_sequence=["#2ea043","#58a6ff","#f0a500"],
                     title="📊 Dot Ball Density (%) by Phase",
                     labels={"phase":"Phase","dot_pct":"Dot Ball %"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Calculate Powerplay dot percentage dynamically for the tip card
    try:
        pp_dot_pct = phase_agg[phase_agg['phase']=='Powerplay']['dot_pct'].values[0]
        pp_str = f"<b>{pp_dot_pct:.1f}%</b>"
    except IndexError:
        pp_str = "<b>high</b>"

    st.markdown(f"""
    <div class="tip-card" style="margin-bottom: 25px;">
        💡 <b>Analytical Insight:</b> While the <b>left chart (Volume)</b> shows that the <b>Middle Phase</b> contributes the largest absolute quantity of dot balls (since it spans 9 overs), the <b>right chart (Density)</b> reveals that the <b>Powerplay Phase</b> has the highest dot ball density at {pp_str}. This is where new-ball bowling intensity meets cautious opening batters trying to preserve their wickets!
    </div>
    """, unsafe_allow_html=True)


    st.subheader("📋 Team Summary")
    td = (team_agg.sort_values("dot_balls", ascending=False).reset_index(drop=True)
          .rename(columns={"batting_team":"Team","dot_balls":"Dot Balls",
                            "total_balls":"Total Balls","dot_pct":"Dot %",
                            "runs":"Runs","trees":"Trees 🌳"}))
    td.index += 1
    st.dataframe(td, use_container_width=True, height=380)


# ──────────────────────────────────────────────────────────────────
# TAB 2 — MATCH RECORDS
# ──────────────────────────────────────────────────────────────────
with tab2:
    max_m = match_agg.loc[match_agg["dot_balls"].idxmax()]
    min_m = match_agg.loc[match_agg["dot_balls"].idxmin()]

    r1,r2 = st.columns(2)
    with r1:
        st.markdown(f"""
        <div class='info-banner'>
            <b style='color:#3fb950;'>🏆 Most Dot Balls in a Match</b><br>
            <span style='font-size:1.5rem;font-weight:700;color:#e6edf3;'>{int(max_m['dot_balls'])} dot balls</span><br>
            <span style='color:#8b949e;'>{max_m['matchup']} · {max_m['venue']} · Season {int(max_m['season'])} · Dot%: {max_m['dot_pct']}%</span>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='info-banner' style='border-left-color:#f85149;'>
            <b style='color:#f85149;'>🔥 Fewest Dot Balls in a Match</b><br>
            <span style='font-size:1.5rem;font-weight:700;color:#e6edf3;'>{int(min_m['dot_balls'])} dot balls</span><br>
            <span style='color:#8b949e;'>{min_m['matchup']} · {min_m['venue']} · Season {int(min_m['season'])} · Dot%: {min_m['dot_pct']}%</span>
        </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        top10 = match_agg.nlargest(10,"dot_balls").sort_values("dot_balls")
        fig = px.bar(top10, x="dot_balls", y="label", orientation="h",
                     color="dot_pct", color_continuous_scale="Greens",
                     title="🏆 Top 10 — Most Dot Balls",
                     labels={"label":"","dot_balls":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls")
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(**_LAY, height=420, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        bot10 = match_agg.nsmallest(10,"dot_balls").sort_values("dot_balls",ascending=False)
        fig = px.bar(bot10, x="dot_balls", y="label", orientation="h",
                     color="dot_pct", color_continuous_scale="Reds",
                     title="🔥 Top 10 — Fewest Dot Balls",
                     labels={"label":"","dot_balls":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls")
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(**_LAY, height=420, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        tp10 = match_agg.nlargest(10,"dot_pct").sort_values("dot_pct")
        fig = px.bar(tp10, x="dot_pct", y="label", orientation="h",
                     color="dot_pct", color_continuous_scale="Tealgrn",
                     title="📊 Highest Dot Ball % in a Match",
                     labels={"label":"","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, height=420, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.histogram(match_agg, x="dot_balls", nbins=40,
                           color_discrete_sequence=["#3fb950"],
                           title="📉 Distribution of Dot Balls per Match",
                           labels={"dot_balls":"Dot Balls"},
                           template=PLOT_THEME)
        fig.update_layout(**_LAY)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Full Match Table"):
        disp = (match_agg[["label","season","venue","dot_balls","dot_pct","total_balls","total_runs","wickets","trees"]]
                .sort_values("dot_balls", ascending=False).reset_index(drop=True)
                .rename(columns={"label":"Match","season":"Season","venue":"Venue",
                                  "dot_balls":"Dot Balls","dot_pct":"Dot %",
                                  "total_balls":"Total Balls","total_runs":"Runs",
                                  "wickets":"Wickets","trees":"Trees 🌳"}))
        disp.index += 1
        st.dataframe(disp, use_container_width=True, height=420)


# ──────────────────────────────────────────────────────────────────
# TAB 3 — BOWLER
# ──────────────────────────────────────────────────────────────────
with tab3:
    min_b = st.slider("Min balls bowled",100,2000,MIN_BOW_BALLS,step=50,key="bw")
    bow = bow_agg[bow_agg["total_balls"] >= min_b].copy()

    max_bw  = bow.loc[bow["dot_balls"].idxmax()]
    min_bw  = bow.loc[bow["dot_balls"].idxmin()]
    max_pct = bow.loc[bow["dot_pct"].idxmax()]
    min_pct = bow.loc[bow["dot_pct"].idxmin()]

    r1,r2,r3,r4 = st.columns(4)
    cards = [
        (r1,"🎯 Most Dot Balls",f"{int(max_bw['dot_balls']):,}",max_bw['bowler'],
         f"{int(max_bw['total_balls']):,} balls bowled","#3fb950"),
        (r2,"🏏 Fewest Dot Balls",f"{int(min_bw['dot_balls']):,}",min_bw['bowler'],
         f"{int(min_bw['total_balls']):,} balls bowled","#f85149"),
        (r3,"📈 Highest Dot %",f"{max_pct['dot_pct']:.1f}%",max_pct['bowler'],
         f"{int(max_pct['dot_balls'])} dots in {int(max_pct['total_balls'])} balls","#58a6ff"),
        (r4,"📉 Lowest Dot %",f"{min_pct['dot_pct']:.1f}%",min_pct['bowler'],
         f"{int(min_pct['dot_balls'])} dots in {int(min_pct['total_balls'])} balls","#f0a500"),
    ]
    for col,label,val,name,sub,color in cards:
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#161b22,#1a2332);
                border:1px solid {color};border-radius:12px;padding:16px;text-align:center;'>
                <div style='color:#8b949e;font-size:.7rem;text-transform:uppercase;'>{label}</div>
                <div style='color:{color};font-size:1.6rem;font-weight:700;margin:4px 0;'>{val}</div>
                <div style='color:#e6edf3;font-size:.9rem;font-weight:600;'>{name}</div>
                <div style='color:#8b949e;font-size:.75rem;margin-top:2px;'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(bow.nlargest(20,"dot_balls").sort_values("dot_balls"),
                     x="dot_balls", y="bowler", orientation="h",
                     color="dot_pct", color_continuous_scale="Greens",
                     title="🎯 Top 20 — Most Dot Balls",
                     labels={"bowler":"","dot_balls":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(bow.nsmallest(20,"dot_balls").sort_values("dot_balls",ascending=False),
                     x="dot_balls", y="bowler", orientation="h",
                     color="dot_pct", color_continuous_scale="Reds",
                     title="🔥 Bottom 20 — Fewest Dot Balls",
                     labels={"bowler":"","dot_balls":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total descending"})
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig = px.bar(bow.nlargest(20,"dot_pct").sort_values("dot_pct"),
                     x="dot_pct", y="bowler", orientation="h",
                     color="dot_pct", color_continuous_scale="Tealgrn",
                     title=f"📊 Highest Dot Ball % (min {min_b} balls)",
                     labels={"bowler":"","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.scatter(bow, x="dot_pct", y="economy",
                         size="total_balls", color="dot_balls",
                         color_continuous_scale="Greens", hover_name="bowler",
                         title="🔍 Economy vs Dot % (bubble = balls bowled)",
                         labels={"dot_pct":"Dot %","economy":"Economy"},
                         template=PLOT_THEME)
        fig.update_layout(**_LAY)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Bowler Leaderboard")
    disp = (bow.sort_values("dot_balls",ascending=False).reset_index(drop=True)
            .rename(columns={"bowler":"Bowler","dot_balls":"Dot Balls","dot_pct":"Dot %",
                              "total_balls":"Balls Bowled","wickets":"Wickets",
                              "runs_given":"Runs Given","economy":"Economy"}))
    disp.index += 1
    st.dataframe(disp, use_container_width=True, height=400)


# ──────────────────────────────────────────────────────────────────
# TAB 4 — BATTER
# ──────────────────────────────────────────────────────────────────
with tab4:
    min_bb = st.slider("Min balls faced",100,2000,MIN_BAT_BALLS,step=50,key="bt")
    bat = bat_agg[bat_agg["total_balls"] >= min_bb].copy()

    max_bat   = bat.loc[bat["dot_balls_faced"].idxmax()]
    min_bat   = bat.loc[bat["dot_balls_faced"].idxmin()]
    max_pbat  = bat.loc[bat["dot_pct"].idxmax()]
    min_pbat  = bat.loc[bat["dot_pct"].idxmin()]

    r1,r2,r3,r4 = st.columns(4)
    cards_b = [
        (r1,"⚫ Most Dots Faced",f"{int(max_bat['dot_balls_faced']):,}",max_bat['batter'],
         f"SR: {max_bat['strike_rate']:.1f}","#f85149"),
        (r2,"🚀 Fewest Dots Faced",f"{int(min_bat['dot_balls_faced']):,}",min_bat['batter'],
         f"SR: {min_bat['strike_rate']:.1f}","#3fb950"),
        (r3,"⏱️ Highest Dot %",f"{max_pbat['dot_pct']:.1f}%",max_pbat['batter'],
         f"SR: {max_pbat['strike_rate']:.1f}","#f0a500"),
        (r4,"⚡ Lowest Dot %",f"{min_pbat['dot_pct']:.1f}%",min_pbat['batter'],
         f"SR: {min_pbat['strike_rate']:.1f}","#58a6ff"),
    ]
    for col,label,val,name,sub,color in cards_b:
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#161b22,#1a2332);
                border:1px solid {color};border-radius:12px;padding:16px;text-align:center;'>
                <div style='color:#8b949e;font-size:.7rem;text-transform:uppercase;'>{label}</div>
                <div style='color:{color};font-size:1.6rem;font-weight:700;margin:4px 0;'>{val}</div>
                <div style='color:#e6edf3;font-size:.9rem;font-weight:600;'>{name}</div>
                <div style='color:#8b949e;font-size:.75rem;margin-top:2px;'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(bat.nlargest(20,"dot_balls_faced").sort_values("dot_balls_faced"),
                     x="dot_balls_faced", y="batter", orientation="h",
                     color="dot_pct", color_continuous_scale="Oranges",
                     title="⚫ Top 20 — Most Dot Balls Faced",
                     labels={"batter":"","dot_balls_faced":"Dot Balls","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_balls_faced")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(bat.nsmallest(20,"dot_balls_faced").sort_values("dot_balls_faced",ascending=False),
                     x="dot_balls_faced", y="batter", orientation="h",
                     color="strike_rate", color_continuous_scale="Greens",
                     title="🚀 Top 20 Most Aggressive — Fewest Dots Faced",
                     labels={"batter":"","dot_balls_faced":"Dot Balls","strike_rate":"SR"},
                     template=PLOT_THEME, text="dot_balls_faced")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total descending"})
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig = px.scatter(bat, x="dot_pct", y="strike_rate",
                         size="total_balls", color="dot_balls_faced",
                         color_continuous_scale="Oranges", hover_name="batter",
                         title="🔍 Strike Rate vs Dot % (bubble = balls faced)",
                         labels={"dot_pct":"Dot %","strike_rate":"Strike Rate"},
                         template=PLOT_THEME)
        fig.update_layout(**_LAY)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.bar(bat.nlargest(20,"dot_pct").sort_values("dot_pct"),
                     x="dot_pct", y="batter", orientation="h",
                     color="strike_rate", color_continuous_scale="Reds",
                     title="⏱️ Highest Dot % Batters",
                     labels={"batter":"","dot_pct":"Dot %","strike_rate":"SR"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, height=560, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Batter Leaderboard")
    disp = (bat.sort_values("dot_balls_faced",ascending=False).reset_index(drop=True)
            .rename(columns={"batter":"Batter","dot_balls_faced":"Dot Balls Faced",
                              "dot_pct":"Dot %","total_balls":"Balls Faced",
                              "runs_scored":"Runs","strike_rate":"Strike Rate",
                              "dismissals":"Dismissals"}))
    disp.index += 1
    st.dataframe(disp, use_container_width=True, height=400)


# ──────────────────────────────────────────────────────────────────
# TAB 5 — VENUE
# ──────────────────────────────────────────────────────────────────
with tab5:
    max_v = venue_agg.loc[venue_agg["dot_pct"].idxmax()]
    min_v = venue_agg.loc[venue_agg["dot_pct"].idxmin()]

    r1,r2 = st.columns(2)
    with r1:
        st.markdown(f"""
        <div class='info-banner'>
            <b style='color:#3fb950;'>🏟️ Most Bowler-Friendly Venue</b><br>
            <span style='font-size:1.4rem;font-weight:700;color:#e6edf3;'>{max_v['dot_pct']:.1f}% dot balls</span><br>
            <span style='color:#8b949e;'>{max_v['venue']} · {int(max_v['matches'])} matches · {max_v['dots_match']:.0f} dots/match</span>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='info-banner' style='border-left-color:#f0a500;'>
            <b style='color:#f0a500;'>🎯 Most Batter-Friendly Venue</b><br>
            <span style='font-size:1.4rem;font-weight:700;color:#e6edf3;'>{min_v['dot_pct']:.1f}% dot balls</span><br>
            <span style='color:#8b949e;'>{min_v['venue']} · {int(min_v['matches'])} matches · {min_v['dots_match']:.0f} dots/match</span>
        </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(venue_agg.nlargest(15,"dot_pct").sort_values("dot_pct"),
                     x="dot_pct", y="venue", orientation="h",
                     color="dot_pct", color_continuous_scale="Greens",
                     title="🏟️ Top 15 — Highest Dot Ball %",
                     labels={"venue":"","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, height=500, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(venue_agg.nsmallest(15,"dot_pct").sort_values("dot_pct",ascending=False),
                     x="dot_pct", y="venue", orientation="h",
                     color="dot_pct", color_continuous_scale="Oranges",
                     title="🎯 Top 15 Batter-Friendly Venues",
                     labels={"venue":"","dot_pct":"Dot %"},
                     template=PLOT_THEME, text="dot_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**_LAY, height=500, yaxis={"categoryorder":"total descending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🗺️ Venue × Season Heatmap")
    top_v = venue_agg.nlargest(25,"matches")["venue"].tolist()
    pivot = venue_season[venue_season["venue"].isin(top_v)].pivot_table(
        index="venue", columns="season", values="dot_pct", aggfunc="mean").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[str(c) for c in pivot.columns], y=pivot.index.tolist(),
        colorscale="Greens",
        colorbar=dict(title="Dot %", tickfont=dict(color="#c9d1d9")),
        hovertemplate="Venue: %{y}<br>Season: %{x}<br>Dot %%: %{z:.1f}%%<extra></extra>",
        zmin=0, zmax=60,
    ))
    fig.update_layout(**_LAY, height=600,
                      title=dict(text="Dot Ball % — Top 25 Venues × Season", font=dict(color="#e6edf3",size=15)),
                      xaxis=dict(title="Season", tickfont=dict(color="#c9d1d9")),
                      yaxis=dict(title="Venue",  tickfont=dict(color="#c9d1d9")))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Venue Summary")
    disp = (venue_agg.sort_values("dot_balls",ascending=False).reset_index(drop=True)
            .rename(columns={"venue":"Venue","dot_balls":"Dot Balls","total_balls":"Total Balls",
                              "matches":"Matches","dot_pct":"Dot %","dots_match":"Dots/Match","runs":"Runs"}))
    disp.index += 1
    st.dataframe(disp, use_container_width=True, height=380)


# ──────────────────────────────────────────────────────────────────
# TAB 6 — ECO IMPACT  (2023 onwards only)
# ──────────────────────────────────────────────────────────────────
with tab6:

    # ── Season Legend ────────────────────────────────────────────
    st.subheader("📖 Season-by-Season Initiative Legend")
    st.markdown("""
    <div class='info-banner'>
        <b style='color:#3fb950;'>🌍 Green Dot Ball Initiative — Official Data (greendotball.com)</b><br>
        <span style='color:#8b949e;font-size:.85rem;'>
        Launched as a pilot in IPL 2023 Playoffs by BCCI &amp; Tata Group.
        For every dot ball bowled, a fixed number of tree saplings are planted across India
        (Kerala, Assam, Gujarat, Karnataka, Maharashtra, Himachal Pradesh).
        The scorecard dot symbol is replaced with a 🌳 tree icon during initiative matches.
        </span>
    </div>
    """, unsafe_allow_html=True)

    legend_cols = st.columns(len(INITIATIVE))
    for i, (season, cfg) in enumerate(INITIATIVE.items()):
        co2 = cfg["trees_planted"] * CO2_PER_TREE
        t_per_dot = cfg["trees_per_dot"]
        t_per_dot_str = f"{t_per_dot:,}" if isinstance(t_per_dot, (int, float)) else str(t_per_dot)
        with legend_cols[i]:
            st.markdown(f"""
            <div class='season-card' style='background:linear-gradient(135deg,#161b22,#1a2332);
                border:2px solid {cfg["color"]};'>
                <div style='font-size:2rem;'>{cfg["icon"]}</div>
                <div style='color:{cfg["color"]};font-size:1.5rem;font-weight:800;margin:4px 0;'>
                    IPL {season}
                </div>
                <div style='background:{cfg["color"]}22;border-radius:20px;padding:4px 14px;
                    display:inline-block;color:{cfg["color"]};font-size:.8rem;font-weight:600;margin-bottom:12px;'>
                    {cfg["scope"]}
                </div>
                <table style='width:100%;color:#c9d1d9;font-size:.82rem;border-collapse:collapse;'>
                    <tr><td style='color:#8b949e;padding:4px 0;'>Trees per dot ball</td>
                        <td style='text-align:right;font-weight:700;color:{cfg["color"]};font-size:1rem;'>
                        {t_per_dot_str}</td></tr>
                    <tr><td style='color:#8b949e;padding:4px 0;'>Dot balls counted</td>
                        <td style='text-align:right;font-weight:600;'>{cfg["dot_balls"]:,}</td></tr>
                    <tr><td style='color:#8b949e;padding:4px 0;'>Trees pledged</td>
                        <td style='text-align:right;font-weight:600;'>{cfg["trees_pledged"]:,}</td></tr>
                    <tr><td style='color:#8b949e;padding:4px 0;'>Trees actually planted</td>
                        <td style='text-align:right;font-weight:700;color:{cfg["color"]};'>
                        ✅ {cfg["trees_planted"]:,}</td></tr>
                    <tr><td style='color:#8b949e;padding:4px 0;'>CO₂ offset/year</td>
                        <td style='text-align:right;color:#26a69a;font-weight:600;'>
                        {co2:,.0f} kg</td></tr>
                    <tr><td style='color:#8b949e;padding:4px 0;'>Matches covered</td>
                        <td style='text-align:right;'>{cfg["matches"]}</td></tr>
                </table>
                <div style='margin-top:10px;color:#8b949e;font-size:.72rem;font-style:italic;'>
                    {cfg["note"]}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pledged vs Actually Planted comparison ───────────────────
    st.subheader("📊 Trees Pledged vs Trees Actually Planted — By Season")

    seasons_list   = list(INITIATIVE.keys())
    trees_pledged  = [INITIATIVE[s]["trees_pledged"]  for s in seasons_list]
    trees_planted  = [INITIATIVE[s]["trees_planted"]  for s in seasons_list]
    dot_balls_list = [INITIATIVE[s]["dot_balls"]       for s in seasons_list]
    factor_list    = [INITIATIVE[s]["trees_per_dot"]   for s in seasons_list]
    scope_list     = [INITIATIVE[s]["scope"]           for s in seasons_list]

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        x=[str(s) for s in seasons_list],
        y=trees_pledged,
        name="Trees Pledged",
        marker=dict(color="#21262d", line=dict(color="#3fb950", width=2)),
        opacity=0.7,
        text=trees_pledged,
        texttemplate="%{text:,}",
        textposition="outside",
    ))
    fig_compare.add_trace(go.Bar(
        x=[str(s) for s in seasons_list],
        y=trees_planted,
        name="Trees Actually Planted ✅",
        marker=dict(color="#3fb950"),
        text=trees_planted,
        texttemplate="%{text:,}",
        textposition="inside",
    ))
    # Annotate each bar with the rate
    for i, season in enumerate(seasons_list):
        fig_compare.add_annotation(
            x=str(season), y=trees_planted[i] + max(trees_pledged)*0.06,
            text=f"{factor_list[i]} trees/dot · {dot_balls_list[i]} dots · {scope_list[i]}",
            showarrow=False, font=dict(color="#8b949e", size=10),
            xanchor="center",
        )
    fig_compare.update_layout(
        **_LAY,
        barmode="overlay",
        title=dict(text="🌳 Trees Pledged vs Actually Planted per Season", font=dict(color="#e6edf3", size=16)),
        xaxis=dict(title="IPL Season", tickfont=dict(color="#c9d1d9")),
        yaxis=dict(title="Number of Trees", tickfont=dict(color="#c9d1d9")),
        height=450,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # ── Per-match breakdown chart ─────────────────────────────────
    st.subheader("🏟️ Per-Match Dot Balls & Trees — Playoff Matches")

    if not pmatch.empty:
        pmatch["label"] = pmatch["match"] + " " + pmatch["season"].astype(str) + "\n(" + pmatch["teams"] + ")"
        pmatch_sorted = pmatch.sort_values(["season","dot_balls"])

        fig_pm = go.Figure()
        colors_pm = {2023:"#3fb950", 2024:"#58a6ff", 2025:"#f0a500", 2026:"#ec7211"}
        for season_yr in pmatch_sorted["season"].unique():
            sub = pmatch_sorted[pmatch_sorted["season"]==season_yr]
            fig_pm.add_trace(go.Bar(
                x=sub["trees_planted"], y=sub["label"],
                orientation="h",
                name=f"IPL {season_yr}",
                marker=dict(color=colors_pm.get(season_yr,"#3fb950")),
                text=sub["trees_planted"],
                texttemplate="%{text:,} trees",
                textposition="outside",
                hovertemplate=(
                    f"<b>IPL {season_yr}</b><br>"
                    "%{y}<br>"
                    "Dot Balls: " + sub["dot_balls"].astype(str) + "<br>"
                    "Trees: %{x:,}<extra></extra>"
                ),
            ))
        fig_pm.update_layout(
            **_LAY,
            title=dict(text="Trees Planted per Playoff Match (2023–2024)", font=dict(color="#e6edf3", size=15)),
            xaxis=dict(title="Trees Planted", tickfont=dict(color="#c9d1d9")),
            yaxis=dict(title="", tickfont=dict(color="#c9d1d9")),
            barmode="group",
            height=460,
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    # ── Cumulative growth ─────────────────────────────────────────
    st.subheader("🌱 Cumulative Trees Planted — Season by Season")

    cum_seasons = list(INITIATIVE.keys())
    cum_vals    = []
    running     = 0
    for s in cum_seasons:
        running += INITIATIVE[s]["trees_planted"]
        cum_vals.append(running)

    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=[str(s) for s in cum_seasons],
        y=cum_vals,
        mode="lines+markers+text",
        line=dict(color="#3fb950", width=3),
        marker=dict(size=14, color=[INITIATIVE[s]["color"] for s in cum_seasons],
                    line=dict(width=2, color="#0d1117")),
        text=[f"{v:,}" for v in cum_vals],
        textposition="top center",
        textfont=dict(color="#3fb950", size=12),
        fill="tozeroy",
        fillcolor="rgba(63,185,80,0.08)",
        name="IPL Trees (Cumulative)",
    ))
    fig_cum.add_annotation(
        x=str(cum_seasons[-1]), y=cum_vals[-1]*1.15,
        text=f"IPL Total: {cum_vals[-1]:,}<br>(IPL+WPL Combined: {CUMULATIVE_ALL:,})",
        showarrow=False, font=dict(color="#8b949e", size=11), xanchor="center",
    )
    fig_cum.update_layout(
        **_LAY,
        title=dict(text="🌳 Cumulative Trees Planted — IPL Green Dot Ball Initiative", font=dict(color="#e6edf3", size=15)),
        xaxis=dict(title="IPL Season", tickfont=dict(color="#c9d1d9")),
        yaxis=dict(title="Total Trees Planted", tickfont=dict(color="#c9d1d9")),
        height=420,
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    # ── Dot balls used for trees vs total dot balls ───────────────
    st.subheader("⚫ Dot Balls Counted for Initiative vs Total Season Dot Balls")

    season_agg_eco = season_agg[season_agg["season"].isin(seasons_list)].copy()
    offic_dots = {s: INITIATIVE[s]["dot_balls"] for s in seasons_list}

    fig_dots = go.Figure()
    fig_dots.add_trace(go.Bar(
        x=[str(s) for s in seasons_list],
        y=[season_agg_eco[season_agg_eco["season"]==s]["dot_balls"].sum() for s in seasons_list],
        name="Total Season Dot Balls (Cricsheet)",
        marker=dict(color="#21262d", line=dict(color="#8b949e", width=1.5)),
        opacity=0.7,
    ))
    fig_dots.add_trace(go.Bar(
        x=[str(s) for s in seasons_list],
        y=[offic_dots[s] for s in seasons_list],
        name="Dot Balls Counted for Initiative (Official)",
        marker=dict(color="#3fb950"),
        text=[offic_dots[s] for s in seasons_list],
        texttemplate="%{text}",
        textposition="inside",
    ))
    for i,s in enumerate(seasons_list):
        fig_dots.add_annotation(
            x=str(s), y=-max(offic_dots.values())*0.08,
            text=INITIATIVE[s]["scope"], showarrow=False,
            font=dict(color="#8b949e", size=9), xanchor="center",
        )
    fig_dots.update_layout(
        **_LAY, barmode="overlay", height=420,
        title=dict(text="⚫ Dot Balls: Initiative Scope vs Full Season", font=dict(color="#e6edf3", size=15)),
        xaxis=dict(title="Season", tickfont=dict(color="#c9d1d9")),
        yaxis=dict(title="Dot Balls", tickfont=dict(color="#c9d1d9")),
    )
    st.plotly_chart(fig_dots, use_container_width=True)

    # ── Initiative dataset preview ────────────────────────────────
    st.subheader("📁 Initiative Dataset (Datasets/sustainability/)")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**green_dot_ball_initiative.csv** — Season-level summary")
        if not init_df.empty:
            st.dataframe(init_df, use_container_width=True)
        else:
            st.warning("File not found.")
    with c2:
        st.markdown("**green_dot_ball_per_match.csv** — Per-match breakdown")
        if not pmatch.empty:
            st.dataframe(pmatch[["season","match","teams","dot_balls","trees_per_dot_ball","trees_planted"]],
                         width="stretch")
        else:
            st.warning("File not found.")

    # ── CO2 impact ───────────────────────────────────────────────
    st.subheader("🌿 CO₂ Offset Impact")
    total_ipl_trees = sum(v["trees_planted"] for v in INITIATIVE.values())
    total_co2_ipl   = total_ipl_trees * CO2_PER_TREE

    i1,i2,i3,i4 = st.columns(4)
    i1.metric("🌳 Total IPL Trees",    f"{total_ipl_trees:,}")
    i2.metric("🌿 CO₂ Offset (kg/yr)", f"{total_co2_ipl:,.0f}")
    i3.metric("🌍 IPL+WPL Combined",   f"{CUMULATIVE_ALL:,} trees")
    i4.metric("🌡️ CO₂ (IPL+WPL)",     f"{CUMULATIVE_ALL*CO2_PER_TREE:,.0f} kg/yr")

    # ── Interactive Green Impact Simulator ────────────────────────
    st.markdown("<hr style='border-color: #1f2a3d; margin: 25px 0;'>", unsafe_allow_html=True)
    st.subheader("🔮 Interactive Green Impact Simulator")
    st.markdown("""
    Adjust the sliders below to simulate hypothetical scenarios and visualize the projected environmental pay-offs if the Green Dot Ball Initiative rate or coverage changes.
    """)
    
    sim_col1, sim_col2 = st.columns([1, 1])
    with sim_col1:
        st.markdown("""
        <div style='background:rgba(13, 18, 31, 0.45); border:1px solid rgba(46, 160, 67, 0.2); border-radius:12px; padding:20px; margin-bottom: 15px;'>
            <h4 style='margin-top:0; color:#2ea043; font-size:0.95rem; font-weight:600; display:flex; align-items:center; gap:6px;'>
                ⚙️ Simulation Controls
            </h4>
            <p style='color:#8b949e; font-size:0.78rem; margin-top:4px;'>Modify the parameters to view cumulative offset potentials.</p>
        </div>
        """, unsafe_allow_html=True)
        sim_dots = st.slider("Hypothetical Dot Balls Bowled", min_value=100, max_value=15000, value=5000, step=100, key="sim_dots_slider")
        sim_rate = st.slider("Saplings Planted per Dot Ball", min_value=1, max_value=1000, value=18, step=1, key="sim_rate_slider")
    
    with sim_col2:
        sim_trees = sim_dots * sim_rate
        sim_co2 = sim_trees * CO2_PER_TREE
        # Average passenger vehicle emissions: 4600 kg CO2 / year (US EPA)
        sim_cars = sim_co2 / 4600
        # Average US forest acre absorption: 2500 kg CO2 / year
        sim_acres = sim_co2 / 2500
        
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom:0; height:100%; display:flex; flex-direction:column; justify-content:space-between; padding:20px 24px;">
            <h4 style="margin-top:0; color:#2ea043; font-size:1rem; font-weight:600; display:flex; align-items:center; gap:8px;">
                🌳 Projected Environmental Payoff
            </h4>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin:15px 0;">
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em;">Trees Planted</div>
                    <div style="color:#2ea043; font-size:1.5rem; font-weight:700; margin-top:4px;">{sim_trees:,}</div>
                </div>
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em;">CO₂ Offset / Yr</div>
                    <div style="color:#58a6ff; font-size:1.5rem; font-weight:700; margin-top:4px;">{sim_co2:,.0f} kg</div>
                </div>
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em;">🚗 Cars Removed / Yr</div>
                    <div style="color:#f0a500; font-size:1.50rem; font-weight:700; margin-top:4px;">{sim_cars:.1f}</div>
                </div>
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em;">🌲 Forest Acres / Yr</div>
                    <div style="color:#ff7b72; font-size:1.50rem; font-weight:700; margin-top:4px;">{sim_acres:.1f}</div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:#8b949e; text-align:center; font-style:italic; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;">
                Based on IPCC standards (21.77 kg CO₂/tree/yr) and US EPA passenger vehicle statistics.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<hr>
<div style='text-align:center;color:#8b949e;font-size:.78rem;padding:16px 0 24px;'>
    🌳 <strong style='color:#3fb950;'>EcoDot Analytics</strong>
    &nbsp;—&nbsp; Tata IPL Sustainability Project
    &nbsp;|&nbsp; Data: <a href='https://cricsheet.org' style='color:#58a6ff;text-decoration:none;'>Cricsheet.org</a>
    &nbsp;|&nbsp; Initiative: <a href='https://greendotball.com' style='color:#3fb950;text-decoration:none;'>greendotball.com</a>
    &nbsp;|&nbsp; Green Dot Ball: IPL 2023 onwards
</div>
""", unsafe_allow_html=True)
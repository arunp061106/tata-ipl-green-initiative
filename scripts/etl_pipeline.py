import os
import json
import pandas as pd

# =========================
# CONSTANTS
# =========================

RAW_PATH    = os.path.join("Datasets", "raw", "Cricsheet")
OUTPUT_PATH = os.path.join("Datasets", "processed")
os.makedirs(OUTPUT_PATH, exist_ok=True)

CO2_PER_TREE = 21.77  # kg CO2 absorbed per tree per year (IPCC standard)

# ── Tata IPL Green Dot Ball Initiative — OFFICIAL DATA ──────────────────────
# Source: greendotball.com  |  Verified: wisden.com, mykhel.com, india.com
#
# Key facts:
#   2023 — PILOT: Playoffs only (4 matches). 500 trees per dot ball.
#           294 dot balls → 147,000 trees planted.
#   2024 — EXPANDED: Playoffs only (4 matches). 500 trees per dot ball.
#           323 dot balls → 161,500 trees planted.
#   2025 — FULL SEASON: All 74 matches. 18 trees per dot ball.
#           (18 to mark the 18th IPL edition)
#           5,562 dot balls → 100,116 trees planted.
#   Cumulative (IPL + WPL combined) as of 2026: 641,166 trees.
#
# IMPORTANT: 2023 & 2024 used ONLY PLAYOFF matches.
#   Playoff match IDs are identified by match_number in the JSON info.
#   Any match with event.match_number > (league_matches) is a playoff.
# ─────────────────────────────────────────────────────────────────────────────

# Season → (trees_per_dot_ball, scope)
INITIATIVE_CONFIG = {
    2023: {"trees_per_dot": 500, "scope": "playoffs_only"},
    2024: {"trees_per_dot": 500, "scope": "playoffs_only"},
    2025: {"trees_per_dot": 18,  "scope": "full_season"},
    2026: {"trees_per_dot": "dynamic", "scope": "full_season"},
}

# Playoff match numbers: IPL has 70 league matches; match_number 71+ = playoffs
# (Qualifier1, Eliminator, Qualifier2, Final = match numbers 71-74)
PLAYOFF_THRESHOLD = {2023: 70, 2024: 70, 2025: None, 2026: 70}  # None = full season

def is_playoff_match(season, match_number):
    """Return True if this match qualifies for the Green Dot Ball initiative."""
    cfg = INITIATIVE_CONFIG.get(season)
    if cfg is None:
        return False
    if cfg["scope"] == "full_season":
        return True
    threshold = PLAYOFF_THRESHOLD.get(season)
    if threshold is None:
        return True
    # match_number from JSON is 1-based
    return match_number > threshold

# =========================
# LOAD & PARSE JSON FILES
# =========================

records = []

json_files = sorted([f for f in os.listdir(RAW_PATH) if f.endswith(".json")])
print(f"Found {len(json_files)} match files. Processing...")

for filename in json_files:
    filepath = os.path.join(RAW_PATH, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        match_data = json.load(f)

    info    = match_data.get("info", {})
    innings = match_data.get("innings", [])

    match_id   = filename.replace(".json", "")
    season_raw = info.get("season", "Unknown")

    try:
        season_int = int(str(season_raw).split("/")[0])
    except ValueError:
        season_int = 0

    match_date   = info.get("dates", ["Unknown"])[0]
    venue        = info.get("venue", "Unknown")
    event_info   = info.get("event", {})
    match_number = event_info.get("match_number", 0) or 0

    # Determine if this match is covered by the initiative
    initiative_active = is_playoff_match(season_int, match_number)
    cfg             = INITIATIVE_CONFIG.get(season_int, {})
    if season_int == 2026 and initiative_active:
        tree_factor = 500 if match_number > 70 else 19
        scope = "playoffs" if match_number > 70 else "league_stage"
    else:
        tree_factor     = cfg.get("trees_per_dot", 0) if initiative_active else 0
        scope           = cfg.get("scope", "none") if initiative_active else "none"

    # =========================
    # ITERATE OVER INNINGS
    # =========================

    for innings_index, innings_data in enumerate(innings):
        team_name = innings_data.get("team", "Unknown")
        if team_name == "Royal Challengers Bangalore":
            team_name = "Royal Challengers Bengaluru"

        for over_data in innings_data.get("overs", []):
            over_number = over_data.get("over", 0)

            for ball_index, delivery in enumerate(over_data.get("deliveries", [])):
                batter      = delivery.get("batter", "Unknown")
                bowler      = delivery.get("bowler", "Unknown")
                non_striker = delivery.get("non_striker", "Unknown")

                runs        = delivery.get("runs", {})
                batter_runs = runs.get("batter", 0)
                extras      = runs.get("extras", 0)
                total_runs  = runs.get("total", 0)

                wickets     = delivery.get("wickets", [])
                wicket_flag = 1 if len(wickets) > 0 else 0

                # True dot ball = batter scores 0 AND no extras
                is_dot_ball = 1 if batter_runs == 0 and extras == 0 else 0

                # Match phase
                if over_number <= 5:
                    phase = "Powerplay"
                elif over_number <= 14:
                    phase = "Middle"
                else:
                    phase = "Death"

                # Trees & CO2 — only for initiative matches
                trees_generated = is_dot_ball * tree_factor
                co2_offset      = trees_generated * CO2_PER_TREE

                record = {
                    "match_id":           match_id,
                    "season":             season_int,
                    "date":               match_date,
                    "venue":              venue,
                    "match_number":       match_number,
                    "innings":            innings_index,
                    "batting_team":       team_name,
                    "bowler":             bowler,
                    "batter":             batter,
                    "non_striker":        non_striker,
                    "over":               over_number,
                    "ball":               ball_index,
                    "batter_runs":        batter_runs,
                    "extras":             extras,
                    "total_runs":         total_runs,
                    "is_dot_ball":        is_dot_ball,
                    "wicket":             wicket_flag,
                    "phase":              phase,
                    "initiative_active":  int(initiative_active),
                    "tree_factor":        tree_factor,
                    "trees_generated":    trees_generated,
                    "co2_offset_kg":      co2_offset,
                }

                records.append(record)

# =========================
# CREATE & SAVE DATAFRAME
# =========================

print("Creating DataFrame...")
df = pd.DataFrame(records)

print(df.head())
print(f"\nShape  : {df.shape}")
print(f"Seasons: {sorted(df['season'].unique().tolist())}")

# Print initiative summary
print("\n" + "="*55)
print("  GREEN DOT BALL INITIATIVE SUMMARY")
print("="*55)
init_df = df[df["initiative_active"] == 1]
for season in sorted(init_df["season"].unique()):
    s_df = init_df[init_df["season"] == season]
    dots  = int(s_df["is_dot_ball"].sum())
    trees = int(s_df["trees_generated"].sum())
    factors = s_df["tree_factor"].unique()
    if len(factors) == 1:
        factor_str = str(int(factors[0]))
    else:
        factor_str = "/".join(str(int(f)) for f in sorted(factors) if f > 0)
    scope = INITIATIVE_CONFIG[season]["scope"].replace("_", " ")
    print(f"  {season} ({scope}): {dots} dot balls (factor {factor_str}) = {trees:,} trees")
print("="*55)

csv_path     = os.path.join(OUTPUT_PATH, "ipl_dot_ball_dataset.csv")
parquet_path = os.path.join(OUTPUT_PATH, "ipl_dot_ball_dataset.parquet")

print("\nSaving datasets...")
df.to_csv(csv_path, index=False)
df.to_parquet(parquet_path, index=False)

print(f"Total Rows : {len(df):,}")
print(f"CSV     -> {csv_path}")
print(f"Parquet -> {parquet_path}")
print("Done!")
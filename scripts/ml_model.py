import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

# =========================
# LOAD DATA
# =========================

DATA_PATH = os.path.join("Datasets", "processed", "ipl_dot_ball_dataset.csv")

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df):,} rows")

# =========================
# MATCH-LEVEL FEATURES
# =========================

match_df = (
    df.groupby(["match_id", "venue", "batting_team", "season"])
    .agg(dot_balls=("is_dot_ball", "sum"))
    .reset_index()
)

# =========================
# LABEL ENCODING
# =========================

venue_encoder = LabelEncoder()
team_encoder  = LabelEncoder()

match_df["venue_encoded"] = venue_encoder.fit_transform(match_df["venue"])
match_df["team_encoded"]  = team_encoder.fit_transform(match_df["batting_team"])

# =========================
# FEATURE MATRIX
# =========================

X = match_df[["venue_encoded", "team_encoded", "season"]]
y = match_df["dot_balls"]

# =========================
# TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# =========================
# MODEL — Random Forest
# =========================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1,
)

print("\nTraining model...")
model.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print(f"\n===== MODEL PERFORMANCE =====")
print(f"  Mean Absolute Error : {mae:.2f} dot balls")
print(f"  R² Score            : {r2:.4f}")

# =========================
# SAMPLE PREDICTION
# =========================

# Predict dot balls for a sample match
sample_venue  = "Wankhede Stadium"
sample_team   = "Mumbai Indians"
sample_season = 2023

# Handle unseen labels gracefully
if sample_venue in venue_encoder.classes_:
    venue_enc = venue_encoder.transform([sample_venue])[0]
else:
    venue_enc = 0
    print(f"  ⚠ Venue '{sample_venue}' not seen during training — defaulting to 0")

if sample_team in team_encoder.classes_:
    team_enc = team_encoder.transform([sample_team])[0]
else:
    team_enc = 0
    print(f"  ⚠ Team '{sample_team}' not seen during training — defaulting to 0")

sample = pd.DataFrame(
    [[venue_enc, team_enc, sample_season]],
    columns=["venue_encoded", "team_encoded", "season"],
)

predicted_dot_balls = model.predict(sample)[0]
predicted_trees     = predicted_dot_balls * 0.01  # TREE_FACTOR

print(f"\n===== SAMPLE PREDICTION =====")
print(f"  Venue   : {sample_venue}")
print(f"  Team    : {sample_team}")
print(f"  Season  : {sample_season}")
print(f"  Predicted Dot Balls : {predicted_dot_balls:.0f}")
print(f"  Predicted Trees     : {predicted_trees:.2f}")

# =========================
# FEATURE IMPORTANCES
# =========================

feature_names      = ["Venue", "Team", "Season"]
importances        = model.feature_importances_
importance_pairs   = sorted(
    zip(feature_names, importances), key=lambda x: x[1], reverse=True
)

print(f"\n===== FEATURE IMPORTANCES =====")
for name, imp in importance_pairs:
    bar = "█" * int(imp * 50)
    print(f"  {name:<10}: {bar} {imp:.4f}")

print("\n✅ ML model pipeline complete!")
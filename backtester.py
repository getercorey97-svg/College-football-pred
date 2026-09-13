import polars as pl
import json
import os
from datetime import datetime

class CalibrationUnit:
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir

    def run_backtest(self, season):
        path = f"data/lake/season_{season}.parquet"
        if not os.path.exists(path): return
        df = pl.read_parquet(path)
        if "week" not in df.columns: return
        
        for week in df["week"].unique().sort():
            week_games = df.filter(pl.col("week") == week)
            for game in week_games.to_dicts():
                home = game.get('home_team_location')
                if not home: continue
                
                p_path = f"{self.profile_dir}/{home}.json"
                if os.path.exists(p_path):
                    with open(p_path, "r") as f: profile = json.load(f)
                    actual = float(game.get('home_score', 0))
                    error = actual - (profile['baseline_exp'] + profile['bias'])
                    profile['bias'] += error * 0.05
                    with open(p_path, "w") as f: json.dump(profile, f)

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
        
        # Walk-forward weekly learning
        for week in df["week"].unique().sort():
            week_games = df.filter(pl.col("week") == week)
            for game in week_games.to_dicts():
                self.self_correct(game)

    def self_correct(self, game):
        home = game['home_team_location']
        path = f"{self.profile_dir}/{home}.json"
        if not os.path.exists(path): return

        with open(path, "r") as f: profile = json.load(f)
        
        # Residual Error learning
        actual_score = game['home_score']
        error = actual_score - (profile.get('baseline_exp', 24.5) + profile.get('bias', 0))
        profile['bias'] += error * profile.get('learning_rate', 0.05)
        profile['last_calibration'] = str(datetime.now())
        
        with open(path, "w") as f: json.dump(profile, f)

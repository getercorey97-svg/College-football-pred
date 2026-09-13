import numpy as np
import polars as pl
from scipy import stats, linalg
import sportsdataverse.cfb as cfb
import json
import os

class CFBEngine:
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir

    def get_profile(self, team):
        path = f"{self.profile_dir}/{team}.json"
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return {"bias": 0.0, "fatigue_index": 1.0, "baseline_exp": 24.5}

    def predict_props(self, qb_name, wr_name):
        # Gaussian Copula Logic (0.65 correlation)
        u = stats.norm.cdf(np.dot(linalg.cholesky([[1.0, 0.65], [0.65, 1.0]], lower=True), np.random.normal(0, 1, (2, 5000))))
        qb_sims = stats.skewnorm.ppf(u[0], a=3, loc=245, scale=60)
        wr_sims = stats.skewnorm.ppf(u[1], a=2, loc(82), scale(25))
        return {"qb": qb_name, "qb_yds": round(float(np.median(qb_sims))), "wr": wr_name, "wr_yds": round(float(np.median(wr_sims)))}

    def run_live_cycle(self):
        print("Fetching tonight's scoreboard...")
        try:
            games = cfb.espn_cfb_scoreboard(year=2024)
            if games is None: return
            
            predictions = []
            for g in games.to_dicts():
                home, away = g['home_team_location'], g['away_team_location']
                h_p, a_p = self.get_profile(home), self.get_profile(away)
                
                # Dixon-Coles simplified for live speed
                h_exp = h_p['baseline_exp'] + h_p['bias']
                a_exp = a_p['baseline_exp'] + a_p['bias']
                
                props = self.predict_props("Starting QB", "WR1")
                
                predictions.append({
                    "game": f"{away} @ {home}",
                    "proj_score": f"{round(h_exp)}-{round(a_exp)}",
                    "spread": round(a_exp - h_exp, 1),
                    "total": round(h_exp + a_exp, 1),
                    "props": props
                })
            
            with open("predictions_tonight.json", "w") as f:
                json.dump(predictions, indent=2, f)
        except Exception as e:
            print(f"Live Cycle Error: {e}")

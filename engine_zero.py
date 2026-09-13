import numpy as np
import polars as pl
from scipy import stats, linalg
import sportsdataverse.cfb as cfb
import json
import os

class CFBEngine:
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir
        os.makedirs(profile_dir, exist_ok=True)

    def get_profile(self, team):
        path = f"{self.profile_dir}/{team}.json"
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return {"bias": 0.0, "fatigue_index": 1.0, "baseline_exp": 24.5}

    def predict_props(self, qb_name, wr_name):
        # Gaussian Copula Logic
        z = np.random.normal(0, 1, (2, 5000))
        corr_matrix = [[1.0, 0.65], [0.65, 1.0]]
        L = linalg.cholesky(corr_matrix, lower=True)
        correlated_z = np.dot(L, z)
        u = stats.norm.cdf(correlated_z)
        
        # Mapping to Skew-Normal distributions
        qb_sims = stats.skewnorm.ppf(u[0], a=3, loc=245, scale=60)
        wr_sims = stats.skewnorm.ppf(u[1], a=2, loc=82, scale=25)
        
        return {
            "qb": qb_name, 
            "qb_yds": round(float(np.median(qb_sims))), 
            "wr": wr_name, 
            "wr_yds": round(float(np.median(wr_sims)))
        }

    def run_live_cycle(self):
        print("Fetching tonight's scoreboard...")
        try:
            games = cfb.espn_cfb_scoreboard()
            if games is None or (hasattr(games, 'empty') and games.empty): 
                print("No games found for today.")
                return
            
            # Handle both list and DataFrame types from ESPN API
            game_list = games.to_dicts() if hasattr(games, 'to_dicts') else games
            
            predictions = []
            for g in game_list:
                home = g.get('home_team_location')
                away = g.get('away_team_location')
                if not home or not away: continue
                
                h_p = self.get_profile(home)
                a_p = self.get_profile(away)
                
                h_exp = h_p['baseline_exp'] + h_p['bias']
                a_exp = a_p['baseline_exp'] + a_p['bias']
                
                props = self.predict_props("Projected QB", "Projected WR1")
                
                predictions.append({
                    "game": f"{away} @ {home}",
                    "proj_score": f"{round(h_exp)}-{round(a_exp)}",
                    "spread": round(float(a_exp - h_exp), 1),
                    "total": round(float(h_exp + a_exp), 1),
                    "props": props
                })
            
            with open("predictions_tonight.json", "w") as f:
                json.dump(predictions, indent=2, f)
            print("✅ Predictions saved to predictions_tonight.json")
        except Exception as e:
            print(f"Live Cycle Error: {e}")

if __name__ == "__main__":
    engine = CFBEngine()
    engine.run_live_cycle()

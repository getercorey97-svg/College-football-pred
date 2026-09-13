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
        return {"bias": 0.0, "fatigue_index": 1.0, "baseline_exp": 24.5, "travel_penalty": 0.0}

    def predict_props(self, qb_name, wr_name):
        # Gaussian Copula Logic
        z = np.random.normal(0, 1, (2, 5000))
        L = linalg.cholesky([[1.0, 0.65], [0.65, 1.0]], lower=True)
        u = stats.norm.cdf(np.dot(L, z))
        
        # Skew-Normal Mapping (Corrected Syntax)
        qb_sims = stats.skewnorm.ppf(u[0], a=3, loc=245, scale=60)
        wr_sims = stats.skewnorm.ppf(u[1], a=2, loc=82, scale=25)
        
        return {
            "qb": qb_name, "qb_yds": round(float(np.median(qb_sims))), 
            "wr": wr_name, "wr_yds": round(float(np.median(wr_sims)))
        }

    def run_live_cycle(self):
        print("🔮 Generating Predictions...")
        try:
            games = cfb.espn_cfb_scoreboard()
            if games is None or (hasattr(games, 'empty') and games.empty): return
            
            game_list = games.to_dicts() if hasattr(games, 'to_dicts') else games
            predictions = []
            
            for g in game_list:
                home, away = g.get('home_team_location'), g.get('away_team_location')
                if not home or not away: continue
                
                h_p, a_p = self.get_profile(home), self.get_profile(away)
                # Apply Geter Principle: biological fatigue and travel adjustment
                h_base = h_p['baseline_exp'] * h_p['fatigue_index'] * (1 - h_p.get('travel_penalty', 0.0))
                a_base = a_p['baseline_exp'] * a_p['fatigue_index'] * (1 - a_p.get('travel_penalty', 0.0))
                h_exp = h_base + h_p['bias']
                a_exp = a_base + a_p['bias']
                
                # Dixon-Coles adjustment for low-score dependencies
                rho = 0.001  # Small dependence parameter
                max_goals = 20  # Truncate summation at 20 points
                home_exp_dc = 0.0
                away_exp_dc = 0.0
                total_prob = 0.0
                
                for x in range(max_goals + 1):
                    for y in range(max_goals + 1):
                        # Poisson probabilities
                        p_x = stats.poisson.pmf(x, h_exp)
                        p_y = stats.poisson.pmf(y, a_exp)
                        p_base = p_x * p_y
                        
                        # Dixon-Coles tau function
                        if x == 0 and y == 0:
                            tau = 1 - rho * h_exp * a_exp
                        elif x == 0 and y == 1:
                            tau = 1 + rho * h_exp
                        elif x == 1 and y == 0:
                            tau = 1 + rho * a_exp
                        elif x == 1 and y == 1:
                            tau = 1 - rho
                        else:
                            tau = 1.0
                        
                        p = p_base * tau
                        home_exp_dc += x * p
                        away_exp_dc += y * p
                        total_prob += p
                
                # Normalize by total probability
                if total_prob > 0:
                    home_exp_dc /= total_prob
                    away_exp_dc /= total_prob
                else:
                    # Fallback to independent Poisson
                    home_exp_dc = h_exp
                    away_exp_dc = a_exp
                
                projections = self.predict_props("Projected QB", "Projected WR1")
                predictions.append({
                    "game": f"{away} @ {home}",
                    "proj_score": f"{round(home_exp_dc)}-{round(away_exp_dc)}",
                    "spread": round(float(away_exp_dc - home_exp_dc), 1),
                    "total": round(float(home_exp_dc + away_exp_dc), 1),
                    "props": projections
                })
            
            with open("predictions_tonight.json", "w") as f:
                json.dump(predictions, indent=2, f)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    CFBEngine().run_live_cycle()

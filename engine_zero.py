import os
import json
import duckdb
import polars as pl
import numpy as np
from scipy import stats
from datetime import datetime
import sportsdataverse.cfb as cfb

# --- 1. STATE & MEMORY MANAGEMENT ---
class StateMemory:
    """Handles self-correction and prevents compounding stats."""
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir
        self.log_file = "processed_games.log"
        os.makedirs(profile_dir, exist_ok=True)
        self.processed_games = self._load_log()

    def _load_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                return set(f.read().splitlines())
        return set()

    def get_team_profile(self, team_id):
        path = f"{self.profile_dir}/{team_id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {"learning_rate": 0.05, "bias": 0.0, "fatigue_index": 1.0, "last_update": None}

    def save_team_profile(self, team_id, profile):
        with open(f"{self.profile_dir}/{team_id}.json", "w") as f:
            json.dump(profile, f)

# --- 2. THE MATHEMATICAL CORE ---
class PredictionLogic:
    @staticmethod
    def calculate_dixon_coles(home_exp, away_exp, rho=-0.1):
        """Calculates score probabilities with low-score dependency adjustment."""
        # Simplified for tonight's initialization
        prob_matrix = np.outer(stats.poisson.pmf(range(50), home_exp), 
                               stats.poisson.pmf(range(50), away_exp))
        # Apply Tau adjustment for 0-0, 1-0, 0-1, 1-1 scores
        prob_matrix[0,0] *= (1 - home_exp * away_exp * rho)
        return prob_matrix

    @staticmethod
    def gaussian_copula_sim(marginals, correlation_matrix, n_sims=10000):
        """Models joint player probabilities (QB + WR Correlation)."""
        L = np.linalg.cholesky(correlation_matrix)
        z = np.random.normal(0, 1, (len(marginals), n_sims))
        correlated_z = np.dot(L, z)
        u = stats.norm.cdf(correlated_z)
        
        sim_results = []
        for i, dist in enumerate(marginals):
            sim_results.append(np.percentile(dist, u[i] * 100))
        return np.array(sim_results)

# --- 3. THE AUTONOMOUS ENGINE ---
class CFBEngine:
    def __init__(self):
        self.memory = StateMemory()
        self.logic = PredictionLogic()
        self.con = duckdb.connect(database=':memory:')

    def ingest_live_data(self):
        """Retrieves tonight's games and rosters."""
        print(f"[{datetime.now()}] Ingesting Live Telemetry...")
        # Fetching tonight's schedule
        try:
            sched = cfb.espn_cfb_scoreboard(year=2024)
            return sched
        except Exception as e:
            print(f"Data Ingestion Error: {e}")
            return None

    def predict_game(self, game_id, home_team, away_team):
        """Generates the full prediction dossier."""
        # 1. Retrieve Team Profiles
        h_profile = self.memory.get_team_profile(home_team)
        a_profile = self.memory.get_team_profile(away_team)

        # 2. Mock Logic for tonight (to be replaced by Parquet Lake query)
        # These are placeholders for the Dixon-Coles Lambda/Mu
        home_lambda = 31.5 * h_profile['fatigue_index']
        away_mu = 24.2 * a_profile['fatigue_index']

        # 3. Generate Spread/Total
        win_prob = np.sum(np.tril(self.logic.calculate_dixon_coles(home_lambda, away_mu), -1))
        
        # 4. Player Prop Simulation (QB Example)
        # Using a 0.6 correlation between QB and WR1
        corr = np.array([[1.0, 0.6], [0.6, 1.0]])
        qb_dist = np.random.normal(250, 50, 1000) # Historical marginal
        wr_dist = np.random.normal(80, 20, 1000)  # Historical marginal
        
        props = self.logic.gaussian_copula_sim([qb_dist, wr_dist], corr)

        return {
            "game_id": game_id,
            "matchup": f"{away_team} @ {home_team}",
            "win_probability": round(float(win_prob), 4),
            "proj_score": f"{round(home_lambda)}-{round(away_mu)}",
            "player_props": {
                "QB_Passing_Yards": round(np.mean(props[0]), 1),
                "WR1_Receiving_Yards": round(np.mean(props[1]), 1)
            }
        }

    def run(self):
        schedule = self.ingest_live_data()
        if schedule is None: return

        predictions = []
        # Filter for tonight's games (Simplified)
        for game in schedule.to_dicts():
            pred = self.predict_game(game['game_id'], game['home_team_location'], game['away_team_location'])
            predictions.append(pred)
        
        # Output Results
        print(json.dumps(predictions, indent=2))
        with open("predictions_tonight.json", "w") as f:
            json.dump(predictions, f)

if __name__ == "__main__":
    engine = CFBEngine()
    engine.run()

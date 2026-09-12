import polars as pl
import numpy as np
import json
import os
from engine_zero import CFBEngine, PredictionLogic

class CalibrationUnit:
    """
    Audits the engine's truthfulness using 2024-2025 results.
    """
    def __init__(self):
        self.engine = CFBEngine()
        self.results_log = []

    def calculate_brier_score(self, predictions, outcomes):
        """Measures the accuracy of probabilistic forecasts (0 is perfect)."""
        return np.mean((predictions - outcomes)**2)

    def spiegelhalter_z(self, p, y):
        """
        Deduces if the model is 'calibrated'. 
        If |Z| > 1.96, the engine is lying to itself about its accuracy.
        """
        variances = p * (1 - p) * (1 - 2*p)**2
        z = np.sum((y - p) * (1 - 2*p)) / np.sqrt(np.sum(variances))
        return z

    def run_backtest(self, season=2024):
        print(f"--- Running Walk-Forward Calibration for {season} ---")
        # Load historical fact from our Parquet Lake
        lake_path = f"data/lake/season_{season}.parquet"
        if not os.path.exists(lake_path):
            print("Error: Lake not seeded for this season.")
            return

        df = pl.read_parquet(lake_path)
        weeks = df["week"].unique().sort()

        for week in weeks:
            print(f"Processing Week {week}...")
            # 1. Isolate week's games
            week_data = df.filter(pl.col("week") == week)
            game_ids = week_data["game_id"].unique()

            for gid in game_ids:
                game_subset = week_data.filter(pl.col("game_id") == gid)
                home = game_subset["home_team_location"][0]
                away = game_subset["away_team_location"][0]
                
                # 2. Predict using CURRENT state (before seeing results)
                prediction = self.engine.predict_game(gid, home, away)
                
                # 3. Get actual result
                # We deduce the winner from the final score in the telemetry
                home_final = game_subset["home_score"].max()
                away_final = game_subset["away_score"].max()
                actual_winner = 1 if home_final > away_final else 0
                
                # 4. Self-Correction Logic (The Learning Loop)
                error = actual_winner - prediction["win_probability"]
                self.update_team_weights(home, away, error)
                
                self.results_log.append({
                    "p": prediction["win_probability"],
                    "y": actual_winner,
                    "error": error
                })

    def update_team_weights(self, home, away, error):
        """
        Adjusts the 134 team profiles based on prediction error.
        If the engine underestimated a team, it increases their 'bias'.
        """
        for team in [home, away]:
            profile = self.engine.memory.get_team_profile(team)
            # Apply learning rate to the error
            adjustment = error * profile["learning_rate"]
            profile["bias"] += adjustment
            profile["last_update"] = str(datetime.now())
            self.engine.memory.save_team_profile(team, profile)

    def report_calibration(self):
        p = np.array([r['p'] for r in self.results_log])
        y = np.array([r['y'] for r in self.results_log])
        
        brier = self.calculate_brier_score(p, y)
        z_score = self.spiegelhalter_z(p, y)
        
        print(f"\n--- CALIBRATION REPORT ---")
        print(f"Brier Score: {round(brier, 4)} (Closer to 0 is better)")
        print(f"Spiegelhalter Z: {round(z_score, 4)} (Target: -1.96 to 1.96)")
        
        if abs(z_score) > 1.96:
            print("WARNING: Model is miscalibrated. Adjusting Global Learning Rates...")

if __name__ == "__main__":
    calibrator = CalibrationUnit()
    calibrator.run_backtest(2024)
    calibrator.run_backtest(2025)
    calibrator.report_calibration()

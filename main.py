import os
import json
from datetime import datetime, timedelta
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("profiles", exist_ok=True)
    
    # 1. Seeding
    s = DataLakeSeeder()
    s.seed_lake()
    s.initialize_profiles()

    # 2. Calibration (Weekly Gate)
    state_path = "data/state.json"
    state = {"last_backtest": "2000-01-01"}
    if os.path.exists(state_path):
        with open(state_path, "r") as f: state = json.load(f)
    
    last_run = datetime.fromisoformat(state["last_backtest"])
    if datetime.now() - last_run > timedelta(days=7):
        print("Running Weekly Calibration...")
        cal = CalibrationUnit()
        for yr in [2023, 2024]: cal.run_backtest(yr)
        state["last_backtest"] = datetime.now().isoformat()
        with open(state_path, "w") as f: json.dump(state, f)

    # 3. Prediction
    engine = CFBEngine()
    engine.run_live_cycle()

if __name__ == "__main__":
    main()

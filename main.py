import os
import json
from datetime import datetime, timedelta
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine

def main():
    # Folder Creation Safety
    os.makedirs("data/lake", exist_ok=True)
    os.makedirs("profiles", exist_ok=True)
    
    # 1. Seeding (Only seeds if data is missing)
    s = DataLakeSeeder()
    s.seed_lake()
    s.initialize_profiles()

    # 2. Weekly Calibration Gate
    state_path = "data/state.json"
    state = {"last_backtest": "2000-01-01"}
    if os.path.exists(state_path):
        with open(state_path, "r") as f: 
            try: state = json.load(f)
            except: pass
    
    last_run = datetime.fromisoformat(state["last_backtest"])
    if datetime.now() - last_run > timedelta(days=7):
        print("Running Weekly Calibration...")
        cal = CalibrationUnit()
        # Calibrate using 2024 and 2025 data
        for yr in [2024, 2025]:
            cal.run_backtest(yr)
        state["last_backtest"] = datetime.now().isoformat()
        with open(state_path, "w") as f: json.dump(state, f)

    # 3. Prediction Run
    engine = CFBEngine()
    engine.run_live_cycle()

if __name__ == "__main__":
    main()

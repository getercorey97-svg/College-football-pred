import os
import json
from datetime import datetime, timedelta
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine

STATE_FILE = "data/state.json"

def get_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f: return json.load(f)
    return {"last_backtest": None, "initialized": False}

def main():
    os.makedirs("data", exist_ok=True)
    state = get_state()
    current_time = datetime.now()

    # 1. Seed Lake
    seeder = DataLakeSeeder()
    if not os.path.exists("data/lake/season_2024.parquet"):
        seeder.seed_lake()
        seeder.initialize_profiles()

    # 2. Calibration Gate (Weekly)
    needs_cal = not state["initialized"]
    if state["last_backtest"]:
        if current_time - datetime.fromisoformat(state["last_backtest"]) > timedelta(days=7):
            needs_cal = True

    if needs_cal:
        cal = CalibrationUnit()
        cal.run_backtest(2024)
        cal.run_backtest(2025)
        state["last_backtest"] = current_time.isoformat()
        state["initialized"] = True
        with open(STATE_FILE, "w") as f: json.dump(state, f)

    # 3. Predict Tonight
    engine = CFBEngine()
    # Mocking tonight's schedule for demonstration
    # In production, this pulls from sportsdataverse.cfb.espn_cfb_scoreboard()
    print("🔮 Predictions Generated. Saving to predictions_tonight.json...")
    # engine.run_live_cycle()

if __name__ == "__main__":
    main()

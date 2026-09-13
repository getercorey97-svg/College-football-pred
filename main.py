import os
import json
from datetime import datetime, timedelta
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine

STATE_FILE = "data/state.json"

def get_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f: 
            try: return json.load(f)
            except: return {"last_backtest": None, "initialized": False}
    return {"last_backtest": None, "initialized": False}

def main():
    os.makedirs("data", exist_ok=True)
    state = get_state()
    current_time = datetime.now()

    seeder = DataLakeSeeder()
    
    # 1. Seed Lake if profiles are missing
    if not os.listdir("profiles"):
        print("📥 Initial Run: Seeding Data...")
        seeder.seed_lake()
        seeder.initialize_profiles()

    # 2. Calibration Gate (Weekly)
    needs_cal = not state.get("initialized", False)
    if state.get("last_backtest"):
        last_run = datetime.fromisoformat(state["last_backtest"])
        if current_time - last_run > timedelta(days=7):
            needs_cal = True

    if needs_cal:
        print("📉 Running Calibration...")
        cal = CalibrationUnit()
        # Try to backtest whatever seasons we actually have
        for s in [2023, 2024]:
            if os.path.exists(f"data/lake/season_{s}.parquet"):
                cal.run_backtest(s)
        
        state["last_backtest"] = current_time.isoformat()
        state["initialized"] = True
        with open(STATE_FILE, "w") as f: json.dump(state, f)

    # 3. Predict Tonight
    print("🔮 Running Prediction Engine...")
    engine = CFBEngine()
    engine.run_live_cycle()

if __name__ == "__main__":
    main()

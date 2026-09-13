import os
import json
from datetime import datetime, timedelta
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine
from ai_critic import AICritic

def main():
    os.makedirs("data/lake", exist_ok=True)
    os.makedirs("profiles", exist_ok=True)
    
    s = DataLakeSeeder()
    s.seed_lake()
    s.initialize_profiles()

    # 7-Day Calibration Gate
    state_path, state = "data/state.json", {"last_backtest": "2000-01-01"}
    if os.path.exists(state_path):
        with open(state_path, "r") as f: state = json.load(f)
    
    if datetime.now() - datetime.fromisoformat(state["last_backtest"]) > timedelta(days=7):
        cal = CalibrationUnit()
        for yr in [2024, 2025]: cal.run_backtest(yr)
        state["last_backtest"] = datetime.now().isoformat()
        with open(state_path, "w") as f: json.dump(state, f)

    engine = CFBEngine()
    engine.run_live_cycle()

    if os.environ.get("OPENROUTER_API_KEY"):
        AICritic().analyze_and_correct()

if __name__ == "__main__":
    main()

import sys
from seeder import DataLakeSeeder
from backtester import CalibrationUnit
from engine_zero import CFBEngine
from roster_intel import IntelligenceGate

def run_full_stack():
    print("!!! INITIALIZING AUTONOMOUS ENGINE !!!")
    
    # 1. SEED: 20 years of fact
    seeder = DataLakeSeeder()
    seeder.seed_lake()
    
    # 2. CALIBRATE: Run 2024-2025 Walk-Forward Validation
    # This sets the 134 team-specific learning rates
    calibrator = CalibrationUnit()
    calibrator.run_backtest(2024)
    calibrator.run_backtest(2025)
    calibrator.report_calibration()
    
    # 3. PREDICT: Run for Tonight's Games
    intel = IntelligenceGate()
    engine = CFBEngine()
    
    # Apply Roster Health adjustments
    # Example: If tonight is Michigan vs Ohio State
    m_health = intel.get_roster_health("130") # Michigan ID
    # ... logic to inject health into engine_zero ...
    
    engine.run()
    print("!!! EXECUTION COMPLETE: Predictions Saved to predictions_tonight.json !!!")

if __name__ == "__main__":
    run_full_stack()

import os
import polars as pl
import pandas as pd
import sportsdataverse.cfb as cfb
from tqdm import tqdm
import json

class DataLakeSeeder:
    def __init__(self, lake_dir="data/lake", profile_dir="profiles"):
        self.lake_dir = lake_dir
        self.profile_dir = profile_dir
        os.makedirs(lake_dir, exist_ok=True)
        os.makedirs(profile_dir, exist_ok=True)

    def seed_lake(self):
        print("🌊 Seeding Historical Data Lake (2004-2025)...")
        for season in tqdm(range(2004, 2026)):
            path = f"{self.lake_dir}/season_{season}.parquet"
            if os.path.exists(path): continue
            try:
                # Attempt to load data
                data = cfb.load_cfb_pbp(seasons=[season])
                if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                    print(f"⚠️ No data found for {season}, skipping.")
                    continue
                
                df = pl.from_pandas(data.astype(str)) # Force string to avoid schema errors
                df.write_parquet(path, compression="zstd")
                print(f"✅ Saved season {season}")
            except Exception as e:
                print(f"❌ Error seeding {season}: {e}")

    def initialize_profiles(self):
        print("👤 Initializing Team Profiles...")
        # Find the most recent file available instead of hardcoding 2024
        files = [f for f in os.listdir(self.lake_dir) if f.endswith(".parquet")]
        if not files:
            print("❌ No data files found. Cannot initialize profiles.")
            return
        
        latest_file = sorted(files)[-1]
        print(f"📊 Using {latest_file} for team initialization.")
        
        df = pl.read_parquet(f"{self.lake_dir}/{latest_file}")
        # Try to find team columns
        team_cols = [c for c in ["home_team_location", "possession_team", "home_team"] if c in df.columns]
        if not team_cols:
            print("❌ Could not find team columns in data.")
            return

        teams = df[team_cols[0]].unique().to_list()
        for team in teams:
            path = f"{self.profile_dir}/{team}.json"
            if not os.path.exists(path):
                profile = {
                    "team": team,
                    "learning_rate": 0.05,
                    "bias": 0.0,
                    "fatigue_index": 1.0,
                    "baseline_exp": 24.5,
                    "last_calibration": None
                }
                with open(path, "w") as f:
                    json.dump(profile, f)

if __name__ == "__main__":
    seeder = DataLakeSeeder()
    seeder.seed_lake()
    seeder.initialize_profiles()

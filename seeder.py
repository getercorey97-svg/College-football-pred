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
        print("🌊 Seeding Data Lake (2020-2025)..."))
        for season in tqdm(range(2020, 2026)):
            path = f"{self.lake_dir}/season_{season}.parquet"
            if os.path.exists(path): continue
            try:
                data = cfb.load_cfb_pbp(seasons=[season])
                if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                    continue
                # Preserve numeric types for week and score calculations
                df = pl.from_pandas(data)
                df.write_parquet(path, compression="zstd")
                print(f"✅ Saved Season {season}")
            except Exception as e:
                print(f"⚠️ Skipping {season}: {e}")

    def initialize_profiles(self):
        print("👤 Initializing Team Profiles...")
        files = [f for f in os.listdir(self.lake_dir) if f.endswith(".parquet")]
        if not files: return
        
        df = pl.read_parquet(f"{self.lake_dir}/{sorted(files)[-1]}")
        team_col = "home_team_location" if "home_team_location" in df.columns else "home_team"
        teams = df[team_col].unique().to_list()
        
        for team in teams:
            path = f"{self.profile_dir}/{team}.json"
            if not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump({
                        "team": team, 
                        "learning_rate": 0.05, 
                        "bias": 0.0, 
                        "fatigue_index": 1.0, 
                        "baseline_exp": 24.5,
                        "travel_penalty": 0.0
                    }, f)

if __name__ == "__main__":
    s = DataLakeSeeder()
    s.seed_lake()
    s.initialize_profiles()

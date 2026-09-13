import os
import polars as pl
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
                data = cfb.load_cfb_pbp(seasons=[season])
                if data.empty: continue
                df = pl.from_pandas(data)
                # Apply Volume Compression for 2024+ Rules
                if season >= 2024:
                    df = df.with_columns(pl.lit(0.92).alias("clock_rule_adj"))
                else:
                    df = df.with_columns(pl.lit(1.0).alias("clock_rule_adj"))
                df.write_parquet(path, compression="zstd")
            except Exception as e:
                print(f"Error seeding {season}: {e}")

    def initialize_profiles(self):
        print("👤 Initializing 134 Team Profiles...")
        # Load 2024 data to get list of active FBS teams
        df = pl.read_parquet(f"{self.lake_dir}/season_2024.parquet")
        teams = df["home_team_location"].unique().to_list()
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

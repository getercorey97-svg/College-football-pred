import polars as pl

def clean_and_filter_telemetry(df: pl.DataFrame):
    """
    Ensures the engine isn't lied to by garbage time or stat-padding.
    """
    return df.filter(
        # Remove Garbage Time (Geter Principle: Psychological drift)
        ~((pl.col("period") == 4) & (pl.col("score_differential").abs() > 28))
    ).with_columns([
        # Success Rate definition: 50% on 1st, 70% on 2nd, 100% on 3rd/4th
        pl.when(pl.col("down") == 1).then(pl.col("yards_gained") >= pl.col("distance") * 0.5)
        .when(pl.col("down") == 2).then(pl.col("yards_gained") >= pl.col("distance") * 0.7)
        .otherwise(pl.col("yards_gained") >= pl.col("distance"))
        .alias("is_success")
    ])

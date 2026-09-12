import numpy as np
from scipy.stats import skewnorm

class MarketEngine:
    """Calculates the specific betting markets requested."""
    
    @staticmethod
    def simulate_drive(epa_per_play, success_rate):
        """Markov Chain simulation of a single CFB drive."""
        # States: 0-99 yards to goal. Absorbing states: TD, FG, Punt, TO.
        current_yardline = 75 # Standard start
        # Probabilistic transition based on team EPA
        gain_avg = 5.2 + (epa_per_play * 2)
        return "TD" if np.random.normal(gain_avg, 3) > 10 else "Punt"

    @staticmethod
    def qb_prop_distribution(base_yards, matchup_multiplier, weather_penalty):
        """Generates QB Passing Yards using a Skew-Normal distribution."""
        # Football stats are 'Right-Skewed' (Big plays happen more than big losses)
        a = 4 # Skewness parameter
        loc = base_yards * matchup_multiplier * weather_penalty
        scale = 65 # Standard deviation for CFB QBs
        
        # Generate 10k simulations for tonight
        sims = skewnorm.rvs(a, loc=loc, scale=scale, size=10000)
        return {
            "mean": np.mean(sims),
            "median": np.median(sims),
            "floor": np.percentile(sims, 15), # 'Under' target
            "ceiling": np.percentile(sims, 85) # 'Over' target
        }

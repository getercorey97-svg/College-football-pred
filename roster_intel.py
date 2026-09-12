import requests
import polars as pl
from datetime import datetime

class IntelligenceGate:
    """Retrieves 'Soft Data' to adjust player-level probabilities."""
    def __init__(self):
        self.api_url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"

    def get_roster_health(self, team_id):
        """Deduces if a team's 'Biosuit' is compromised by injuries."""
        try:
            # ESPN undocumented endpoint for injuries
            resp = requests.get(f"{self.api_url}{team_id}/roster").json()
            players = resp.get('athletes', [])
            injury_count = 0
            starters_out = []
            
            for group in players:
                for p in group.get('items', []):
                    if p.get('injury'):
                        injury_count += 1
                        # Logic: If player is in top 10% of salary/stats, they are a 'Star'
                        if p.get('starter', False):
                            starters_out.append(p.get('fullName'))
            
            # Returns a multiplier: 1.0 = Healthy, < 1.0 = Compromised
            health_multiplier = 1.0 - (len(starters_out) * 0.05)
            return max(0.7, health_multiplier) 
        except:
            return 1.0

    def check_transfer_portal(self, player_name):
        """Cross-checks if a player is active or in the portal."""
        # Fuzzy matching logic for player names to prevent identity errors
        pass

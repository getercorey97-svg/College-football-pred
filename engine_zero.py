import numpy as np
from scipy import stats, linalg
import json
import os

class PredictionLogic:
    @staticmethod
    def nearest_psd(A):
        """Repairs correlation matrices to ensure mathematical truth."""
        B = (A + A.T) / 2
        _, s, V = linalg.svd(B)
        H = np.dot(V.T, np.dot(np.diag(s), V))
        A2 = (B + H) / 2
        A3 = (A2 + A2.T) / 2
        if linalg.det(A3) > 0: return A3
        I = np.eye(A.shape[0])
        k = 1
        while linalg.det(A3) <= 0:
            A3 += I * np.spacing(linalg.norm(A)) * (10**k)
            k += 1
        return A3

    @staticmethod
    def dixon_coles_matrix(h_exp, a_exp, rho=-0.1):
        """Bivariate Poisson with dependency adjustment."""
        max_s = 60
        h_p = stats.poisson.pmf(np.arange(max_s), h_exp)
        a_p = stats.poisson.pmf(np.arange(max_s), a_exp)
        m = np.outer(h_p, a_p)
        tau = np.ones((max_s, max_s))
        tau[0,0], tau[0,1], tau[1,0], tau[1,1] = 1-h_exp*a_exp*rho, 1+h_exp*rho, 1+a_exp*rho, 1-rho
        return m * tau

class CFBEngine:
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir
        self.logic = PredictionLogic()

    def get_profile(self, team):
        path = f"{self.profile_dir}/{team}.json"
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return {"bias": 0.0, "fatigue_index": 1.0, "baseline_exp": 24.5}

    def predict_game(self, home, away):
        h_p = self.get_profile(home)
        a_p = self.get_profile(away)
        
        # Geter Principle: Fatigue & Bias adjustment
        h_exp = (h_p['baseline_exp'] + h_p['bias']) * h_p['fatigue_index']
        a_exp = (a_p['baseline_exp'] + a_p['bias']) * a_p['fatigue_index']
        
        matrix = self.logic.dixon_coles_matrix(h_exp, a_exp)
        win_prob = np.sum(np.tril(matrix, -1))
        over_prob = np.sum(np.triu(matrix + matrix.T, 45)) # Example Total 45.5

        return {
            "matchup": f"{away} @ {home}",
            "home_win_prob": round(float(win_prob), 4),
            "proj_score": f"{round(h_exp)}-{round(a_exp)}",
            "total_over_prob": round(float(over_prob), 4)
        }

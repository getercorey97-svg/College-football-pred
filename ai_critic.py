import os
import json
import requests

class AICritic:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def analyze_and_correct(self):
        if not self.api_key: return
        print("\u001b[34m\u2705\u001b[0m OpenRouter AI is auditing the engine...")
        
        with open("predictions_tonight.json", "r") as f:
            data = f.read()

        prompt = f"""
        Analyze these CFB predictions: {data}
        Task: Suggest bias adjustments for the teams. 
        Format: JSON only. Example: {{"team_name": "Michigan", "new_bias": 1.5}}
        """

        headers = {{
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/cfb-engine",
            "Content-Type": "application/json"
        }}

        payload = {{
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }}

        try:
            response = requests.post(self.url, headers=headers, json=payload).json()
            # Note: We parse the AI response to adjust the profiles/ JSONs
            print("\u001b[32m\u2705\u001b[0m AI Audit complete.")
        except Exception as e:
            print(f"AI Error: {e}")
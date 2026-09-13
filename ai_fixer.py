import os
import requests
import json

class AIFixer:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.core_files = ["engine_zero.py", "seeder.py", "backtester.py", "main.py"]

    def run_system_audit(self):
        if not self.api_key:
            print("❌ No API Key.")
            return

        # Load all files into a single context so the AI understands dependencies
        context = ""
        for file_name in self.core_files:
            with open(file_name, "r") as f:
                context += f"\n--- START OF FILE: {file_name} ---\n"
                context += f.read()
                context += f"\n--- END OF FILE: {file_name} ---\n"

        prompt = f"""
        You are the Lead Architect for a State-of-the-Art CFB Prediction Engine.
        Review this entire multi-file system for mathematical truth and Python accuracy.
        
        SYSTEM CONTEXT:
        {context}
        
        REQUIRED FIXES:
        1. Ensure 'Dixon-Coles' Poisson math correctly models low-score dependencies.
        2. Verify 'Gaussian Copula' correctly models correlations between QB and WR yards.
        3. Apply 'The Geter Principle' to fatigue and travel variables.
        4. Fix any syntax errors (e.g., ensuring stats functions use loc= and scale= keywords).
        
        OUTPUT INSTRUCTIONS:
        Return ONLY a JSON object where keys are the filenames and values are the full corrected code.
        Format: {{"filename.py": "code content"}}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/cfb-ai-fixer",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3.1-405b-instruct",
            "messages": [{"role": "system", "content": "You are a self-healing coding agent."},
                         {"role": "user", "content": prompt}],
            "response_format": { "type": "json_object" }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload).json()
            # Parse the AI's suggested fixes
            fixes = json.loads(response['choices'][0]['message']['content'])
            
            for file_name, new_code in fixes.items():
                if file_name in self.core_files:
                    with open(file_name, "w") as f:
                        f.write(new_code)
                    print(f"🛠️ AI fixed {file_name}")
        except Exception as e:
            print(f"❌ Audit failed: {e}")

if __name__ == "__main__":
    AIFixer().run_system_audit()

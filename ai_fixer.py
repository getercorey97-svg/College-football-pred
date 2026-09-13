import os
import requests
import json

class AIFixer:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.core_files = ["engine_zero.py", "seeder.py", "backtester.py", "main.py"]
        # Updated for Sep 13, 2026: Using the autonomous free router and top-tier free coding models
        self.models = [
            "openrouter/free",                      # Safest: Automatically picks best available free model
            "nvidia/nemotron-3-ultra-550b-a55b:free", # Best for multi-step reasoning & coding
            "poolside/laguna-s-2.1:free"             # Flagship coding agent model
        ]

    def run_system_audit(self):
        if not self.api_key:
            print("❌ Error: OPENROUTER_API_KEY is missing in GitHub Secrets.")
            return

        print("📂 Loading files for audit...")
        context = ""
        for file_name in self.core_files:
            if os.path.exists(file_name):
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
        3. Apply 'The Geter Principle' (Biological Fatigue) to fatigue and travel variables.
        4. Fix any syntax errors (e.g., ensuring stats functions use loc= and scale= keywords).
        
        OUTPUT INSTRUCTIONS:
        Return ONLY a JSON object where keys are the filenames and values are the full corrected code.
        Do not include markdown formatting like ```json.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/cfb-ai-fixer",
            "Content-Type": "application/json"
        }

        success = False
        for model in self.models:
            if success: break
            try:
                print(f"🤖 Requesting Audit from: {model}...")
                payload = {
                    "model": model,
                    "messages": [{"role": "system", "content": "You are a self-healing coding agent that outputs raw JSON."},
                                 {"role": "user", "content": prompt}]
                }
                
                res = requests.post(self.url, headers=headers, json=payload)
                response = res.json()
                
                if 'error' in response:
                    print(f"⚠️ Model {model} failed: {response['error'].get('message')}")
                    continue

                if 'choices' not in response:
                    continue

                content = response['choices'][0]['message']['content'].strip()
                
                # Clean up markdown formatting
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                fixes = json.loads(content)
                
                for file_name, new_code in fixes.items():
                    if file_name in self.core_files:
                        with open(file_name, "w") as f:
                            f.write(new_code)
                        print(f"🛠️ AI successfully fixed {file_name}")
                
                success = True
                print(f"✅ System-wide audit complete using {model}.")
                    
            except Exception as e:
                print(f"⚠️ Attempt with {model} failed: {str(e)}")

if __name__ == "__main__":
    AIFixer().run_system_audit()

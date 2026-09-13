import os
import requests
import json

class AIAuditor:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.files_to_audit = ["engine_zero.py", "seeder.py", "backtester.py"]

    def audit_and_fix(self):
        if not self.api_key:
            print("❌ No OpenRouter Key found. Skipping Audit.")
            return

        for file_path in self.files_to_audit:
            print(f"🔍 AI is auditing {file_path}...")
            with open(file_path, "r") as f:
                content = f.read()

            prompt = f"""
            You are an expert Python Data Scientist and Sports Quant.
            Review the following code for the College Football Prediction Engine.
            
            CODE TO REVIEW:
            {content}
            
            TASK:
            1. Fix any Python SyntaxErrors or TypeErrors.
            2. Ensure the 'Geter Principle' (fatigue logic) and 'Dixon-Coles' (Poisson math) are mathematically sound.
            3. If the code is perfect, return the exact same code.
            4. If changes are made, return the FULL REWRITTEN FILE.
            
            OUTPUT FORMAT:
            Return ONLY the raw Python code. No explanations, no markdown blocks.
            """

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/cfb-self-healer",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "meta-llama/llama-3.1-405b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }

            try:
                response = requests.post(self.url, headers=headers, json=payload).json()
                new_code = response['choices'][0]['message']['content'].strip()
                
                # Check if AI actually returned code and not an error message
                if "import" in new_code and "class" in new_code:
                    with open(file_path, "w") as f:
                        f.write(new_code)
                    print(f"✅ {file_path} has been self-corrected and saved.")
            except Exception as e:
                print(f"❌ AI Audit failed for {file_path}: {e}")

if __name__ == "__main__":
    AIAuditor().audit_and_fix()

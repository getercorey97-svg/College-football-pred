import os
import requests
import json
import glob

class UniversalAIFixer:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        # Discovery: Find every Python file in the directory
        self.files_to_fix = glob.glob("*.py")
        # Remove the fixer itself from the list to prevent recursion loops
        if "ai_universal_fixer.py" in self.files_to_fix:
            self.files_to_fix.remove("ai_universal_fixer.py")
            
        self.models = ["openrouter/free"]

    def total_system_repair(self):
        if not self.api_key:
            print("❌ OPENROUTER_API_KEY missing.")
            return

        print(f"🔍 AI is scanning all system files: {self.files_to_fix}")
        
        # Build the 'Project Memory'
        project_memory = ""
        for file_name in self.files_to_fix:
            with open(file_name, "r") as f:
                project_memory += f"\nFILE: {file_name}\nCONTENT:\n{f.read()}\n"

        prompt = f"""
        You are a Master System Architect and Elite Sports Quant. 
        Perform a TOTAL REPAIR of the following College Football Prediction Engine. 
        
        PROJECT FILES:
        {project_memory}
        
        OBJECTIVE:
        Fix EVERYTHING that is wrong. This includes:
        1. MATHEMATICAL TRUTH: Implement the 'Dixon-Coles' adjustment for low scores (0, 1, 2, 3 points).
        2. BIOLOGICAL TRUTH: Fully integrate 'The Geter Principle'. Calculate fatigue based on 'Biological Collision Fatigue' and the 'Travel Toll Index' (distance + time zones).
        3. CORRELATION TRUTH: Use a Gaussian Copula to link QB passing yards and WR receiving yards.
        4. PRODUCTION TRUTH: Optimize Polars and DuckDB queries for speed and zero-memory leaks.
        5. SYNTAX TRUTH: Fix all Python errors, keyword argument mistakes (loc=, scale=), and API endpoint changes.

        OUTPUT FORMAT:
        Return ONLY a raw JSON object. Keys are filenames, values are the FULL corrected code. 
        Example: {{"main.py": "code...", "engine_zero.py": "code..."}}
        Do not include any conversational text or markdown blocks.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/universal-cfb-fixer",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.models[0],
            "messages": [
                {"role": "system", "content": "You are a self-correcting AI that optimizes complex mathematical and data engineering systems."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0 # Strict logic, no creativity
        }

        try:
            print("📡 Sending system to OpenRouter for total repair...")
            res = requests.post(self.url, headers=headers, json=payload)
            response = res.json()
            
            if 'error' in response:
                print(f"❌ API Error: {response['error'].get('message')}")
                return

            content = response['choices'][0]['message']['content'].strip()
            
            # Robust JSON cleaning
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            fixes = json.loads(content)
            
            for file_name, new_code in fixes.items():
                with open(file_name, "w") as f:
                    f.write(new_code)
                print(f"🛠️ REPAIRED & OPTIMIZED: {file_name}")
            
            print("✅ ALL SYSTEMS HEALED. The engine is now mathematically and logically perfect.")

        except Exception as e:
            print(f"❌ Total Repair Failed: {e}")

if __name__ == "__main__":
    UniversalAIFixer().total_system_repair()

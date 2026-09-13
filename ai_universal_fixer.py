import os
import requests
import json
import glob
import re

class UniversalAIFixer:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.files_to_fix = glob.glob("*.py")
        if "ai_universal_fixer.py" in self.files_to_fix:
            self.files_to_fix.remove("ai_universal_fixer.py")
        # Using a slightly higher-tier model for better JSON reliability
        self.models = ["meta-llama/llama-3.1-70b-instruct", "openrouter/free"]

    def robust_json_load(self, raw_str):
        """
        Heuristic repair for malformed AI JSON.
        """
        # 1. Strip markdown and conversational noise
        content = re.sub(r'```json|```', '', raw_str).strip()
        
        # 2. Try standard load
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 3. Handle missing closing brackets
        # If the AI cut off, we try to append brackets until it works
        temp_content = content
        for _ in range(5): 
            try:
                return json.loads(temp_content)
            except:
                temp_content += "}"
        
        # 4. Final attempt: Extract using bracket counting
        # This finds the start { and then finds the matching }
        start_idx = content.find('{')
        if start_idx == -1: return None
        
        count = 0
        for i in range(start_idx, len(content)):
            if content[i] == '{': count += 1
            elif content[i] == '}': count -= 1
            if count == 0:
                try:
                    return json.loads(content[start_idx:i+1])
                except:
                    break
        return None

    def total_system_repair(self):
        if not self.api_key:
            print("❌ OPENROUTER_API_KEY missing.")
            return

        project_memory = ""
        for file_name in self.files_to_fix:
            with open(file_name, "r") as f:
                project_memory += f"\nFILE: {file_name}\nCONTENT:\n{f.read()}\n"

        prompt = f"""
        TASK: Perform a TOTAL REPAIR of these Python files for a CFB Prediction Engine.
        You MUST return ONLY a valid JSON object. 
        
        JSON FORMAT: 
        {{ "filename.py": "FULL_CODE_HERE" }}
        
        CRITICAL RULES:
        1. No conversational text.
        2. Escape all internal quotes in the code (e.g. use \\" for quotes inside strings).
        3. Ensure every {{ has a matching }}.
        
        PROJECT DATA:
        {project_memory}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/universal-cfb-fixer",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.models[0],
            "messages": [
                {"role": "system", "content": "You are a machine that outputs raw JSON code blocks. You never talk, you only output JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        }

        try:
            print("📡 Sending system to OpenRouter...")
            res = requests.post(self.url, headers=headers, json=payload)
            response = res.json()
            
            if 'error' in response:
                print(f"❌ API Error: {response['error'].get('message')}")
                return

            raw_content = response['choices'][0]['message']['content']
            
            # Use our new Robust Parser
            fixes = self.robust_json_load(raw_content)

            if not fixes:
                print("❌ Failed to parse AI response even with heuristic repair.")
                print(f"RAW PREVIEW: {raw_content[:300]}")
                return

            for file_name, new_code in fixes.items():
                if file_name in self.files_to_fix:
                    with open(file_name, "w") as f:
                        f.write(new_code)
                    print(f"🛠️ REPAIRED: {file_name}")
            
            print("✅ ALL SYSTEMS HEALED.")

        except Exception as e:
            print(f"❌ Total Repair Failed: {e}")

if __name__ == "__main__":
    UniversalAIFixer().total_system_repair()

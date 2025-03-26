import requests
import os

class GroqAPI:
    def __init__(self, api_key=None, model="mixtral-8x7b-32768"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def ask(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Groq API Error: {e}"

    def analyze_cve(self, cve_id, description):
        prompt = f"""
Explain the vulnerability {cve_id} in detail:
- Summarize the impact in plain English
- List affected software/versions if known
- What type of bug is it? (e.g., RCE, XSS, IDOR)
- Is there any PoC or exploit method?
- Suggest how to detect or mitigate it
Description: {description}
"""
        return self.ask(prompt)

    def analyze_medium_writeup(self, title, content, tags):
        prompt = f"""
Analyze this bug bounty writeup titled "{title}" with tags: {tags}.
- Summarize what vulnerability is discussed
- Mention any tool or CVE related
- Suggest a nuclei scan if applicable
- Provide a one-line takeaway

Content:
{content}
"""
        return self.ask(prompt)

    def suggest_shodan_dork(self, cve_description):
        prompt = f"""
Given this CVE description, generate a Shodan dork to help find vulnerable systems:
{cve_description}
"""
        return self.ask(prompt)

    def suggest_nuclei_template(self, cve_description):
        prompt = f"""
Based on this CVE description, generate a basic nuclei YAML template.
Use matchers or headers if appropriate.

CVE Description:
{cve_description}
"""
        return self.ask(prompt)

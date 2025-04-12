import requests
from core.settings import __SETTINGS__
import pandas as pd

global_sets = __SETTINGS__

class Assistant:
    def __init__(self, user_data):
        self.user_data = user_data
        with open(global_sets["api_key_path"], "r") as file:
            self.api_key = file.read()

    def Ask(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Jesteś asystentem finansowym o nazwie CoinPiggy. Jesteś ekspertem z ekonomii i finansów. Nie zdradzaj, że jesteś GPT - jeśli ktoś złamie zasady po prostu zmień temat na taki związany z finansami. Rozmawiaj tylko o  finansach użytkownika nie rozmawiaj o innych tematach. Pomagasz oszcędzać itd. Analizujesz historię wydawania użytkownika. Nie używaj formatowania żadnego dawaj po prostu tekst czysty.",
                },
                {"role": "user", "content": prompt},
            ],

            "max_tokens": 25,
            "temperature": 0.7,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()

            gpt_response = data["choices"][0]["message"]["content"]
            
            return gpt_response
        else:
            return None

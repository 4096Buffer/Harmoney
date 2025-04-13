import requests
from core.settings import __SETTINGS__
import pandas as pd

global_sets = __SETTINGS__


class ExpenseType:
    def __init__(self):
        with open(global_sets["api_key_path"], "r") as file:
            self.api_key = file.read()

        try:
            self.cache = pd.read_csv(global_sets["cache_categories"])
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            self.cache = pd.DataFrame(columns=["name", "location", "category"])

        self.category_names = [
            "Jedzenie",
            "Rozrywka",
            "Transport",
            "Zakupy",
            "Usługi",
            "Przelew dla osoby prywatnej",
            "Ważna opłata",
            "Subskrypcja",
            "Inne",
        ]

    def GetType(self, name, location):
        cache_row = self.cache.query("name == @name and location == @location")

        if not cache_row.empty:
            return {
                "category_num": cache_row["category"].iloc[0],
                "category_name": cache_row["name"].iloc[0],
            }

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Działasz jako API. Ja podaje ci nazwę transakcji lub przedmiotu i lokalizacje a ty na podstawie tego masz stwierdzić jaki to typ zakupu. Typy: jedzenie - 0, rozrywka - 1, transport - 2, zakupy - 3, usługi - 4, przelew dla osoby prywatnej - 5, ważna opłata - 6, subskrypcja - 7, inne - 8. Zwróc tylko jedną cyfrę NIC WIĘCEJ!!!, przemyśl swój wybór. ",
                },
                {"role": "user", "content": name + " Lokalizacja: " + location},
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

            try:
                gpt_response = int(gpt_response)

                if gpt_response > 8 and gpt_response < 0:
                    gpt_response = 8
            except:
                gpt_response = 8

            new_row = {"name": name, "location": location, "category": gpt_response}

            self.cache = pd.concat(
                [self.cache, pd.DataFrame([new_row])], ignore_index=True
            )

            self.cache.to_csv(global_sets["cache_categories"], index=False)

            return {
                "category_num": gpt_response,
                "category_name": self.category_names[gpt_response],
            }
        else:
            return None

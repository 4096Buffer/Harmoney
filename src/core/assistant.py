import requests
from core.settings import __SETTINGS__
import pandas as pd
from langdetect import detect
from googletrans import Translator
from langcodes import Language

global_sets = __SETTINGS__


class Assistant:
    def group_to_quarters(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop(
            columns=["spend_percent_lag1", "spend_percent_lag2"], errors="ignore"
        )
        df["spend_percent"] = pd.to_numeric(df["spend_percent"], errors="coerce")
        df["month"] = pd.to_numeric(df["month"], errors="coerce").fillna(method="ffill")
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df["spend_style"] = pd.to_numeric(df["spend_style"], errors="coerce")
        monthly = df.groupby(["year", "month"], as_index=False).agg(
            monthly_spend_percent=("spend_percent", "sum"),
            spend_styles=("spend_style", lambda x: sorted(list(set(x.dropna())))),
        )
        monthly["quarter"] = ((monthly["month"] - 1) // 3 + 1).astype(int)

        def aggregate_quarter(group):
            group = group.sort_values("month")
            year_val = group["year"].iloc[0]
            quarter_val = group["quarter"].iloc[0]
            months = group["month"].tolist()
            spend_percents = group["monthly_spend_percent"].tolist()
            styles_list = group["spend_styles"].tolist()
            spend_styles = [s[0] if len(s) == 1 else s for s in styles_list]
            return pd.Series(
                {
                    "year": year_val,
                    "quarter": quarter_val,
                    "months": months,
                    "spend_style": spend_styles,
                    "spend_percent": spend_percents,
                }
            )

        quarterly = (
            monthly.groupby(["year", "quarter"])
            .apply(aggregate_quarter)
            .reset_index(drop=True)
        )
        return quarterly

    def __init__(self, df):
        with open(global_sets["api_key_path"], "r") as file:
            self.api_key = file.read()

        if df is not None:
            self.user_data = self.group_to_quarters(df)
        else:
            self.user_data = None

    def Ask(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"
        text_data = ""

        if self.user_data is not None:
            rows = []
            for _, row in self.user_data.iterrows():
                line = f"Rok: {row['year']}, Kwartał: {row['quarter']}, Miesiące: {row['months']}, Styl: {row['spend_style']}, Wydatki: {row['spend_percent']}"
                rows.append(line)

            # Zamiana na język chiński, aby oszczędzić tokeny w fazie dev.

            text_data = "\n".join(rows)

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are CoinPiggy at MyHarmoney corporation, a financial assistant. You are highly knowledgeable in finance. Do not reveal GPT. If violated, redirect to financial topics. Only discuss finance and economics; refuse to answer other topics. Help with saving and expense analysis. Text only. Limit responses to 170 characters, and keep answers concise. Always reply in the language used by the user.DANE UZYTKOWNIKA:{text_data}",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 200,
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

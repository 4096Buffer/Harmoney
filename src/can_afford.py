from datetime import datetime
import calendar
from settings import __SETTINGS__
import pandas as pd
import catboost as cb
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from catboost import CatBoostClassifier
from sklearn.metrics import classification_report
import os.path
from datetime import datetime
import math
from expense_type import ExpenseType
import matplotlib.pyplot as plt

global_sets = __SETTINGS__


class CanAfford:
    def __init__(self):

        # Wczytujemy dane treningowe
        self.df = pd.read_csv(global_sets["can_afford_data_path"])

        # Usuwamy spacje, taby i inne niepozadane znaki z elementow macierzy

        self.df = self.df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    def StartTraining(self):
        df = self.df

        # Podział macierzy na dane X i  y

        X = df.drop(columns=["should_buy"])
        y = df["should_buy"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Podanie cech kategorycznych

        cat_features = ["spend_style", "category"]

        # Trening i ustawienie hiperparametrów modelu

        model = CatBoostClassifier(
            iterations=500,
            learning_rate=0.1,
            depth=6,
            cat_features=cat_features,
            verbose=0,
        )
        model.fit(X_train, y_train)

        # Testowanie dokładności modelu

        y_pred = model.predict(X_test)

        # Zapisanie modelu do pliku i zwrócenie jego obiektu

        model.save_model(global_sets["can_afford_model_path"])

        return model

    def CheckCanAfford(self, data):

        # Wczytanie modelu, utworzenie obiektu expense_type, wczytanie danych uzytkownika

        model = None
        expense_type = ExpenseType()
        user_week_data = pd.read_csv("../data/user-data.csv")

        # Sprawdzamy dane wydatków z poprzednich miesięcy

        prev_weeks = user_week_data.query(
            f"month == {datetime.now().month - 1} and year == {datetime.now().year}"
        )

        prev_month_sp = prev_weeks["spend_percent"].sum()
        prev_month_sp_lag = prev_weeks["spend_percent_lag1"].sum()

        # Liczymy zmianę procentową z 3 ostatnich miesięcy

        months_mean = (prev_month_sp + prev_month_sp_lag) / 2
        next_month = data["next_month"]
        next_month_change = (next_month - months_mean) / months_mean

        # Pobieramy dane potrzebne do predykcji i zamieniamy dict na DataFrame

        left_percent = data["left_percent"]
        name = data["name"]
        price = data["price"]
        location = data["location"]
        spend_style = data["spend_style"]
        installments = data["installments"]
        income = data["income"]
        item_price_percent = price / income

        try:
            category = expense_type.GetType(name, location)["category_num"]
        except:
            category = 8

        df = pd.DataFrame(
            [
                {
                    "next_month_diff": next_month_change,
                    "spend_style": spend_style,
                    "category": category,
                    "installments": installments,
                    "left_percent_from_income": left_percent,
                    "item_price_percent": item_price_percent,
                    "prev_month": prev_month_sp,
                }
            ]
        )

        # Sprawdzamy czy plik modelu istnieje. Jeśli nie zaczynamy trening, jeśli tak wczytujemy go z pliku

        if os.path.isfile(global_sets["can_afford_model_path"]):
            model = CatBoostClassifier()
            model.load_model(global_sets["can_afford_model_path"])
        else:
            model = self.StartTraining()

        # Zwracamy predykcję modelu

        return model.predict(df)[0]

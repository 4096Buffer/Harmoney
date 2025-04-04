from datetime import datetime
import calendar
from settings import __SETTINGS__
import pandas as pd
import catboost as cb
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error
import os.path
import datetime
import math

global_sets = __SETTINGS__


class TodaySpend:
    def __advance_day(self, row_dict, days):

        # Konwertujemy słownik na obiekt daty

        current_date = datetime.date(
            row_dict["year"], row_dict["month"], row_dict["month_day"]
        )

        # Obliczamy jak bedzie wygladac pelna data po n dniach

        next_date = current_date + datetime.timedelta(days=days)

        # Zapisujemy nowe dane

        new_year = next_date.year
        new_month = next_date.month
        new_day = next_date.day
        new_weekday = next_date.weekday() + 1  # 0 = pon, 6 = niedz.
        new_weekend = 1 if new_weekday >= 5 else 0

        next_row = {
            "month": new_month,
            "month_day": new_day,
            "year": new_year,
            "weekday": new_weekday,
            "weekend": new_weekend,
            "spend_style": row_dict["spend_style"],
            "spend_percent": None,
            "spend_percent_lag1": row_dict["spend_percent_lag1"],
            "spend_percent_lag2": row_dict["spend_percent_lag2"],
        }

        return next_row

    def __init__(self):

        # Pobieramy plik CSV i zamieniamy go na DataFrame

        self.df = pd.read_csv(global_sets["today_spend_data_path"])

        # Usuwamy spacje, taby itp. w każdym elemencie macierzy

        self.df = self.df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    def StartTraining(self):
        df = self.df

        # Podajemy dane X, y
        # X - kolumny, na których model ma się uczyć
        # Y - kolumna, którą ma przewidzieć regresją

        X = df.drop(columns=["spend_percent"])
        y = df["spend_percent"]

        # Podział danych na testowe i treningowe

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Podanie cech kategorycznych

        cat_features = ["month", "weekday", "weekend", "spend_style"]

        # Trening modelu, ustawienie hiperparametrów itd.

        model = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6, verbose=0)
        model.fit(X_train, y_train, cat_features=cat_features)

        # Test modelu na danych testowych

        y_pred = model.predict(X_test)

        # Obliczanie średniego błędu kwadratowego, czyli odchylenia od poprawnej wartości

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        print(f"Mean error {rmse}")
        print(f"Mean squared error: {mse}")

        # Zapisanie modelu do ścieżki z modelami

        model.save_model(global_sets["today_spend_model_path"])

        return model

    def GetTodaySpend(self, data_dict, income, avg_spend=False):

        # Jeśli plik modelu istnieje wczytujemy go, jeśli nie zaczynamy trening.. ;p

        model = None

        if not os.path.isfile(global_sets["today_spend_model_path"]):
            model = self.StartTraining()
        else:
            model = CatBoostRegressor()
            model.load_model(global_sets["today_spend_model_path"])

        # Konwertujemy słownik na DataFrame

        df = pd.DataFrame([data_dict])

        # Model przewiduje poprawno

        today_pred = model.predict(df)[0]

        # Jeśli funkcja ma zwracać tylko przewidywaną wartość bez kalkulacji rekomendowanych wydatków lub jeśli uzytkownik jest juz oszczedny i nie trzeba poprawiać się zwracamy tę wartość

        if avg_spend or data_dict["spend_style"] == 0:
            return today_pred

        # Wspolczynnik wplywu trendu na oszczedzanie

        k = 0.5

        # Min. osczednosci

        r0 = 0.1

        # SIGMA func

        # Obliczanie rekomendowanych wydatków wg. wzoru
        # A(d) = S(d) * [1 - (r0 + k * (1/7) * Σ_{i=1}^{7} [(S(d+i) - S(d)) / S(d)])]

        sigma_sum = 0

        for i in range(1, 7 + 1):
            next_day_dict = self.__advance_day(data_dict, i)
            next_day_pred = self.GetTodaySpend(next_day_dict, income, True)

            sigma_sum += (next_day_pred - today_pred) / today_pred

        mean_sigma_value = sigma_sum / 7
        preff_spend = (today_pred * (1 - (r0 + k * mean_sigma_value))) / 100

        # Zwrócenie wydatkow na dzien dzisiejszy z dokladnoscia do czesci setnych

        return round(preff_spend * income, 2)

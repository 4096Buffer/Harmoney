import pandas as pd
from settings import __SETTINGS__
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import joblib
import os.path

global_sets = __SETTINGS__


class FutureSpend:
    def __loaddata(self):
        # Wczytanie danych treningowych, dodanie cech i sortowanie wg roku i miesiąca

        df = pd.read_csv(global_sets["future_spend_data_path"])
        df = self.__addfeatures(df)
        df = df.sort_values(by=["year", "month"])

        return df

    def __addfeatures(self, df):
        # Dodanie dodatkowych cech w celu zwiększenia dokładności modelu

        df["month_sin"] = np.sin(2 * np.pi * (df["month"] - 1) / 12)
        df["month_cos"] = np.cos(2 * np.pi * (df["month"] - 1) / 12)

        if "spend_percent" in df.columns:
            percent_mean = df["spend_percent"].mean()
            df["mean_spend_deviation"] = df["spend_percent"] - percent_mean
        else:
            df["mean_spend_deviation"] = self.df["mean_spend_deviation"]

        return df

    def __init__(self):
        self.df = self.__loaddata()

    def __getsplit(self, df):
        # Podział danych wejściowych na treningowe i testowe 80/20

        X, y = {}, {}

        df.drop(columns=["spend_percent"])
        y = df["spend_percent"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )

        return X_train, X_test, y_train, y_test

    def StartTraining(self):
        X_train, X_test, y_train, y_test = self.__getsplit(self.df)

        # Utworzenie modelu regresji XGBOOST

        model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=200,
            learning_rate=0.4,
            max_depth=4,
            random_state=42,
        )

        # Trening modelu

        model.fit(X_train, y_train)

        # Test modelu na X_test i porównanie go z prawidłowymi przewidywaniami y_test

        y_pred = model.predict(X_test)

        # Sprawdzanie jak dobrze model wyjaśnia zmienność danych im bliżej 1 tym lepiej, ale wartości bardzo wysokie np 0.99 lub 1 mogą sugerować over-fitting!

        r2 = r2_score(y_test, y_pred)

        # Mierzenie o ile średnio myli się model

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        print(f"R2 Score: {r2}")
        print(f"RMSE Score: {rmse}")

        # Zapisywanie modelu do pliku .plk

        joblib.dump(model, global_sets["future_spend_model_path"])

        return model

    def Predict(self, income, data, df_tune):
        df = pd.DataFrame([data])
        model = None

        # Sprawdzamy czy model został zapisany do pliku, jeśli nie zaczynamy trening

        if os.path.isfile(global_sets["future_spend_model_path"]):
            model = joblib.load(global_sets["future_spend_model_path"])
        else:
            model = self.StartTraining()

        # Fine-tuning modelu i personalizacja modelu dla użytkownika

        df_tune = self.__addfeatures(df_tune)
        df_tune = df_tune.sort_values(by=["year", "month"])

        X_train, X_test, y_train, y_test = self.__getsplit(df_tune)

        model.fit(X_train, y_train, xgb_model=model.get_booster())

        df = self.__addfeatures(df)
        y_pred = model.predict(df)

        # Zwracamy przewidywany wydatek zaokrąglając do części setnych

        return round(income * y_pred[0] / 100, 2)

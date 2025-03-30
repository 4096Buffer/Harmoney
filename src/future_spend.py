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
        df = self.addfeatures(df)

        return df

    def addfeatures(self, df, df_tune=None):
        # Dodanie dodatkowych cech w celu zwiększenia dokładności modelu

        # Kolejność cech

        expected_features = [
            "week",
            "year",
            "spend_style",
            "spend_percent",
            "month",
            "spend_percent_lag1",
            "spend_percent_lag2",
            "week_sin",
            "week_cos",
            "mean_spend_deviation",
            "avg_last_3_weeks",
            "trend_last_3_weeks",
            "is_start_of_month",
            "is_end_of_month",
        ]

        df = df.sort_values(by=["year", "week"])

        # Uczymy cykliczności i normalizujemy dane do od 0 - 1

        df["week_sin"] = np.sin(2 * np.pi * (df["week"] - 1) / 52)
        df["week_cos"] = np.cos(2 * np.pi * (df["week"] - 1) / 52)

        # Zamiana wszystkich wartości w pliku .csv na float

        for col in expected_features:
            if col in df.columns:
                df[col] = (
                    pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float)
                )

        # Jeśli DataFrame to plik treningowy to średnią bierzemy po prostu z danych, jeśli nie to średnią bierzemy z danych użytkownika

        if "spend_percent" in df.columns:
            percent_mean = df["spend_percent"].mean()
            df["mean_spend_deviation"] = df["spend_percent"] - percent_mean
        else:
            df["mean_spend_deviation"] = self.df["mean_spend_deviation"]

        if df_tune is not None and df_tune is not df_tune.empty:
            df_tune = df_tune.sort_values(by=["year", "week"]).reset_index(drop=True)

            df["spend_percent_lag1"] = df_tune.iloc[-1]["spend_percent"]
            df["spend_percent_lag2"] = df_tune.iloc[-2]["spend_percent"]

            df["avg_last_3_weeks"] = df_tune["spend_percent"].tail(3).mean()
            df["trend_last_3_weeks"] = (
                df_tune["spend_percent"].iloc[-1] - df["avg_last_3_weeks"]
            )
        else:
            df["avg_last_3_weeks"] = df["spend_percent"].rolling(3).mean()
            df["trend_last_3_weeks"] = df["spend_percent"] - df["avg_last_3_weeks"]

        df["is_start_of_month"] = (df["month"] != df["month"].shift(1)).astype(int)
        df["is_end_of_month"] = (df["month"] != df["month"].shift(-1)).astype(int)

        available_features = [col for col in expected_features if col in df.columns]
        df = df[available_features]

        return df

    def __init__(self):
        self.df = self.__loaddata()

    def __getsplit(self, df):
        # Podział danych wejściowych na treningowe i testowe 80/20

        X, y = {}, {}

        X = df.drop(columns=["spend_percent"])
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

    def Predict(self, data, df_tune, pred_month=True):
        df = pd.DataFrame([data])
        model = None

        # Sprawdzamy czy model został zapisany do pliku, jeśli nie zaczynamy trening

        if os.path.isfile(global_sets["future_spend_model_path"]):
            model = joblib.load(global_sets["future_spend_model_path"])
        else:
            model = self.StartTraining()

        # Fine-tuning modelu i personalizacja modelu dla użytkownika

        df_tune_new = self.addfeatures(df_tune)
        df_tune_new = df_tune_new.sort_values(by=["year", "week"])

        X_train, X_test, y_train, y_test = self.__getsplit(df_tune_new)

        model.fit(X_train, y_train, xgb_model=model.get_booster())

        df = self.addfeatures(df, df_tune)

        y_pred = model.predict(df)

        # Zwracamy przewidywany wydatek zaokrąglając do części setnych

        if not pred_month:
            return [round(y_pred[0], 2), df]
        else:
            summed = 0
            i = 0
            while True:
                check = df_tune.query(
                    f"month == {data['month']} and week == {data['week']+i} and year == {data['year'] - 1}"
                )

                if check.empty:
                    break

                new_data = data.copy()
                new_data["week"] = data["week"] + i

                pred = self.Predict(new_data, df_tune, False)
                num = pred[0]
                df_copy = pred[1]

                df_tune = pd.concat([df_tune, df_copy], ignore_index=True)
                summed += num
                i += 1

            return round(summed, 2)

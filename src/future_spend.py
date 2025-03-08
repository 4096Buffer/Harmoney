import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, InputLayer
from settings import __SETTINGS__

global_settings = __SETTINGS__

class FutureSpend:
    def __init__(self):
        """
        Inicjalizacja klasy FutureSpend - wczytuje dane z pliku CSV.
        """
        self.df = pd.read_csv(global_settings["future_spend_data_path"])  # Wczytujemy dane
        self.models = {}  # Modele dla każdego miesiąca
        self.scalers = {}  # Skalery dla każdego miesiąca

    def __createsequences(self, data, seq_length=5):
        """
        Tworzy sekwencje dla danego miesiąca, wykorzystując poprzednie lata do przewidywania kolejnego roku.
        """
        X, y = [], []
        
        # Sortujemy dane po roku
        data = data.sort_values("year")

        for i in range(len(data) - seq_length):
            X.append(data.iloc[i:i+seq_length]["spend_percent"].values)  # `spend_percent` z poprzednich lat
            y.append(float(data.iloc[i+seq_length]["spend_percent"]))  # Przyszły rok

        return np.array(X), np.array(y)

    def StartTraining(self):
        """
        Trenuje osobny model dla każdego miesiąca.
        """
        months_grouped = {month: self.df[self.df["month"] == month] for month in range(1, 13)}

        for month, df_month in months_grouped.items():
            if len(df_month) > 5:  # Sprawdzamy, czy mamy wystarczająco dużo danych
                X, y = self.__createsequences(df_month)

                # Skalowanie danych
                scaler = MinMaxScaler()
                X = scaler.fit_transform(X.reshape(-1, X.shape[-1]))  # Skalujemy `X`

                # Podział na zbiór treningowy i testowy
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Tworzenie modelu
                model = Sequential([
                    InputLayer(input_shape=(5, 1)),  # 5 poprzednich lat jako wejście
                    LSTM(50, activation="relu", return_sequences=True),
                    LSTM(30, activation="relu"),
                    Dense(16, activation="relu"),
                    Dense(1)  # Przewidujemy jedną wartość `spend_percent`
                ])

                model.compile(optimizer="adam", loss="mse", metrics=["mae"])
                model.fit(X_train, y_train, epochs=50, batch_size=8, validation_data=(X_test, y_test))

                # Zapisujemy model i skaler
                self.models[month] = model
                self.scalers[month] = scaler

    def PredictSpend(self, month, year):
        """
        Przewiduje `spend_percent` dla danego miesiąca w podanym roku.
        """
        if month not in self.models:
            print(f"❌ Brak modelu dla miesiąca {month}.")
            return None

        # Pobranie ostatnich 5 lat dla danego miesiąca
        df_month = self.df[self.df["month"] == month].sort_values("year")
        last_5_years = df_month.tail(5)["spend_percent"].values.reshape(1, -1)  # (1, 5)

        if last_5_years.shape[1] != 5:  # Sprawdzamy, czy mamy dokładnie 5 lat
            print(f"❌ Za mało danych dla miesiąca {month}, aby przewidzieć rok {year}.")
            return None

        # Skalowanie wejścia
        X_pred = self.scalers[month].transform(last_5_years)  # (1, 5)

        # Przywrócenie do kształtu (1, 5, 1) dla LSTM
        X_pred = X_pred.reshape(1, 5, 1)

        # Predykcja
        predicted_percent = self.models[month].predict(X_pred)[0][0]

        # Odwrócenie skalowania
        predicted_percent = self.scalers[month].inverse_transform(np.array([[predicted_percent]]))[0][0]

        print(f"🎯 Przewidywany procent wydatków na {month}/{year}: {predicted_percent:.2f}%")
        return predicted_percent

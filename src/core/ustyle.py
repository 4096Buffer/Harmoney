## Importing modules

import os
import pandas as pd
import re
import joblib
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import numpy as np
from difflib import SequenceMatcher
from difflib import get_close_matches
import seaborn as sns
import xgboost as xgb
import math
import whois
from datetime import datetime
import os.path
from core.settings import __SETTINGS__

global_sets = __SETTINGS__


class UStyle:
    def __init__(self):
        # Wczytanie danych treningowych z pliku financial-style.csv

        self.df = pd.read_csv(global_sets["ustyle_data_path"])

        # Poprawa zapisu money_style z 1,2,3 (dla oszczednego, stabilnego i impulsywnego) na 0,1,2 z powodu wymagan xgb

        self.df["money_style"] = self.df["money_style"] - 1

    def StartTraining(self):
        df = self.df

        # X - cechy do treningu
        # y - wartość, która będzie przewidywana

        X = df.drop(columns=["money_style"])
        y = df["money_style"]

        # Podział danych wejściowych na treningowe i testowe 80/20

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=True, random_state=42
        )

        # Tworzenie modelu klasyfikującego XGBoost

        model = xgb.XGBClassifier(
            objective="multi:softmax",
            num_class=len(y.unique()),
            n_estimators=70,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
        )

        # Trening ML

        model.fit(X_train, y_train)

        # Test dokładności modelu na danych testowych X_test, y_test

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Dokładność modelu: {accuracy:.4f}")

        # Zapisanie modelu do pliku .plk

        joblib.dump(model, global_sets["ustyle_model_path"])

        return model

    def Predict(self, data):
        df = self.df

        # Konwertowanie tablicy 2D na DataFrame z kolumnami

        X = df.drop(columns=["money_style"])
        data = pd.DataFrame(data, columns=X.columns)

        # Jeśli plik modelu istnieje pobieramy go, jeśli nie zaczynamy trening

        model = None

        if not os.path.isfile(global_sets["ustyle_model_path"]):
            model = self.StartTraining()
        else:
            model = joblib.load(global_sets["ustyle_model_path"])

        # Predykcja modelu i zwrócenie wyników

        prediction = model.predict(data)

        return prediction[0]

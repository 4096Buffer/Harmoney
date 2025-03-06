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


##Style prediction class

class UStyle:
    def __init__(self):
        self.df = pd.read_csv('../data/financial-style.csv')
        
        self.df['money_style'] = self.df['money_style'] - 1

    def __totext(self, prediction):
        match prediction:
            case 0:
                return 'Oszczędny'
            case 1:
                return 'Stabilny'
            case 2:
                return 'Zakupoholik'
            case _:
                return 'N/A'
    def StartTraining(self):
        df = self.df
        X = df.drop(columns=['money_style'])
        y = df['money_style']
        print(df['money_style'].value_counts())

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=37)

        model = xgb.XGBClassifier(objective="multi:softmax", num_class=len(y.unique()), n_estimators=70, learning_rate=0.1, max_depth=3, random_state=42)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f'Dokładność modelu: {accuracy:.4f}')

        new_data = pd.DataFrame([[-0.5, 1, 0, 3, 55, 7, 0]], columns=X.columns)
        prediction = model.predict(new_data)
        
        
        print("Przewidywany money_style:", self.__totext(prediction[0]))
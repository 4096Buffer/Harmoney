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

class FutureSpend():
    def __loaddata(self):
        df = pd.read_csv(global_sets['future_spend_data_path'])
        df = self.__addfeatures(df)
        df = df.sort_values(by=['year', 'month'])
        
        return df
    
    def __addfeatures(self, df):
        df['month_sin'] = np.sin(2 * np.pi * (df['month'] - 1) / 12)
        df['month_cos'] = np.cos(2 * np.pi * (df['month'] - 1) / 12)

        if 'spend_percent' in df.columns:
            percent_mean = df['spend_percent'].mean()
            df['mean_spend_deviation'] = df['spend_percent'] - percent_mean 
        else:
            df['mean_spend_deviation'] = self.df['mean_spend_deviation']

        return df
    def __init__(self):
        self.df = self.__loaddata()

    def StartTraining(self):
        X, y = {}, {}

        X = self.df[['month','year','spend_style','spend_percent_lag1','spend_percent_lag2', 'month_sin', 'month_cos', 'mean_spend_deviation']]
        print(X)
        
        y = self.df['spend_percent']
        tscv = TimeSeriesSplit(n_splits=5)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = XGBRegressor(objective='reg:squarederror', n_estimators=200, learning_rate=0.4, max_depth=4, random_state=42)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        print(f"R2 Score: {r2}")
        print(f"RMSE Score: {rmse}")

        joblib.dump(model, global_sets['future_spend_model_path'])

        return model

    def Predict(self, income, data):
        df = pd.DataFrame([data])
        model = None

        if os.path.isfile(global_sets['future_spend_model_path']):
            model = joblib.load(global_sets['future_spend_model_path'])
        else:
            model = self.StartTraining()

        df = self.__addfeatures(df)

        y_pred = model.predict(df)

        return round(income * y_pred[0] / 100, 2)

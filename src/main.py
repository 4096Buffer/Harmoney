from ustyle import UStyle
from future_spend import FutureSpend
import pandas as pd

ustyle = UStyle()
future_spend = FutureSpend()
user_data = pd.read_csv('../data/user-data.csv')

predicted_style = ustyle.Predict([[0.1, 0.7, 0.3, 2, 45, 7, 0.3]])
predicted = future_spend.Predict(6500, {'month' : 12, 'year' : 2026, 'spend_style' : 2, 'spend_percent_lag1' : 65.4,'spend_percent_lag2' : 98.7}, user_data)

predicted_style_txt = ''

match predicted_style:
    case 0:
        predicted_style_txt = 'Oszczędny 📈'
    case 1:
        predicted_style_txt = 'Stabilny ⛵'
    case 2:
        predicted_style_txt = 'Zakupoholik 🛒'
    case _:
        predicted_style_txt = 'N/A'

print(f"📊 Styl finansowy {predicted_style_txt}")
print(f"💲 Szacunkowe wydatki na 1 stycznia 2026: {predicted} PLN czyli {predicted//(6500/100)}% przychodów")
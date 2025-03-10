from ustyle import UStyle
from future_spend import FutureSpend

ustyle = UStyle()
future_spend = FutureSpend()

predicted_style = ustyle.Predict([[10, 0.4, 0.6, 1, 100, 7, 0.8]])

predicted = future_spend.Predict(6500, {'month' : 1, 'year' : 2026, 'spend_style' : 0, 'spend_percent_lag1' : 64.4,'spend_percent_lag2' : 48.7})

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
print(f"💲 Szacunkowe wydatki na 1 stycznia 2026: {predicted} PLN")
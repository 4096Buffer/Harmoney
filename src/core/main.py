from ustyle import UStyle
from future_spend import FutureSpend
import pandas as pd
from today_spend import TodaySpend
from expense_type import ExpenseType
from can_afford import CanAfford

# Tworzymy obiekty modeli

ustyle = UStyle()
future_spend = FutureSpend()
user_data = pd.read_csv("../data/user-data.csv")
today_spend = TodaySpend()
can_afford = CanAfford()

# Model przewiduje dzienny wydatek i przelicza to na odpowiedni budżet

Ad = today_spend.GetTodaySpend(
    {
        "month": 3,
        "month_day": 13,
        "year": 2025,
        "weekday": 4,
        "weekend": 0,
        "spend_style": 2,
        "spend_percent_lag1": 1.4,
        "spend_percent_lag2": 1.9,
    },
    9200,
)

# Podajemy testowane dane o użytkowniku, aby sprawdzić jak radzi sobie model w przewidywaniu stylu wydawania

predicted_style = ustyle.Predict([[0.18, 0.65, 0.15, 3, 78, 5, 0.41]])

# Model przewiduje przyszłe wydatki na podstawie danych wejściowych

predicted = (
    future_spend.Predict(
        {"week": 1, "year": 2026, "spend_style": 1, "month": 1},
        user_data,
    )
    * 9200
)


# Zamiana surowych danych (0,1,2) na tekst

predicted_style_txt = ""

match predicted_style:
    case 0:
        predicted_style_txt = "Oszczędny 📈"
    case 1:
        predicted_style_txt = "Stabilny ⛵"
    case 2:
        predicted_style_txt = "Zakupoholik 🛒"
    case _:
        predicted_style_txt = "N/A"

# Testowe dane do sprawdzenia czy użytkownik jest wstanie pozwolić sobie na taki zakup

test_expense = {
    "name": "Iphone 16 Pro Max",
    "price": 3000,
    "location": "Łódź",
    "spend_style": predicted_style,
    "installments": 0,
    "income": 6500,
    "left_percent": 0.9,
    "next_month": predicted,
}

# Sprawdzamy wynik modelu CanAfford

ca_result = can_afford.CheckCanAfford(test_expense)

# Wyniki testów modelu

print(
    f"🤔Użytkownik chce kupić {test_expense['name']} za {test_expense['price']}zł. Na podstawie jeszcze innych danych AI stwierdza, że użytkownik {'może dokonać zakupu.' if ca_result else 'nie powinien dokonywać zakupu.'}"
)
print(f"📊 Styl finansowy {predicted_style_txt}")
print(
    f"💲 Szacunkowe wydatki na kwiecień 2025: {predicted} PLN czyli {round((predicted/9200) * 100, 2)}% przychodów"
)
print(f"💭 Dzisiaj powinieneś wydać nie więcej niż {Ad} PLN")

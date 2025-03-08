from ustyle import UStyle
from future_spend import FutureSpend

ustyle = UStyle()
future_spend = FutureSpend()

ustyle.Predict([[10, 0.4, 0.6, 1, 100, 7, 0.8]])

future_spend.StartTraining()
future_spend.PredictSpend(1,2026)
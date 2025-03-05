import numpy as np
import pandas as pd

num_users_group1 = 3333  # Oszczędny
num_users_group2 = 3333  # Stabilny
num_users_group3 = 3334  # Impulsywny
num_users_total = num_users_group1 + num_users_group2 + num_users_group3

def generate_user_data(style):
    if style == 1:  # Oszczędny
        income = np.random.randint(7000, 15000)
        m = [np.random.randint(int(0.3*income), int(0.5*income)) for _ in range(3)]
        savings = np.random.randint(int(0.2*income), int(0.5*income))
        fixed_expenses = np.random.randint(int(0.2*income), int(0.35*income))
        num_transactions = np.random.randint(20, 60)
        luxury_percent = np.random.uniform(0.05, 0.2)
        subscriptions_count = np.random.randint(0, 5)
    elif style == 2:  # Stabilny finansowo
        income = np.random.randint(5000, 12000)
        m = [np.random.randint(int(0.5*income), int(0.7*income)) for _ in range(3)]
        savings = np.random.randint(int(0.1*income), int(0.3*income))
        fixed_expenses = np.random.randint(int(0.3*income), int(0.45*income))
        num_transactions = np.random.randint(40, 80)
        luxury_percent = np.random.uniform(0.15, 0.35)
        subscriptions_count = np.random.randint(2, 7)
    else:  # Impulsywny wydawca
        income = np.random.randint(4000, 10000)
        m = [np.random.randint(int(0.7*income), int(1.1*income)) for _ in range(3)]
        savings = np.random.randint(0, int(0.1*income))
        fixed_expenses = np.random.randint(int(0.25*income), int(0.4*income))
        num_transactions = np.random.randint(60, 120)
        luxury_percent = np.random.uniform(0.3, 0.6)
        subscriptions_count = np.random.randint(5, 12)
    
    average_spent = np.mean(m)
    delta_spent = m[2] - m[0]
    if m[2] > m[1] > m[0]:
        spending_trend = 3  # rosnący
    elif m[2] < m[1] < m[0]:
        spending_trend = 1  # malejący
    else:
        spending_trend = 2  # stabilny

    savings_rate = savings / income
    disposable_income = income - fixed_expenses
    variable_expense_ratio = (average_spent - fixed_expenses) / income

    return {
        "average_spent": average_spent,
        "delta_spent": delta_spent,
        "income": income,
        "savings": savings,
        "fixed_expenses": fixed_expenses,
        "num_transactions": num_transactions,
        "luxury_percent": luxury_percent,
        "subscriptions_count": subscriptions_count,
        "savings_rate": savings_rate,
        "disposable_income": disposable_income,
        "variable_expense_ratio": variable_expense_ratio,
        "spending_trend": spending_trend
    }

def classify_spending_style(features):
    spending_ratio = features["average_spent"] / features["income"]
    if spending_ratio < 0.4 and features["savings_rate"] > 0.2 and features["spending_trend"] == 1:
        return 1  # Oszczędny
    elif 0.4 <= spending_ratio <= 0.7 and features["savings_rate"] > 0.1:
        return 2  # Stabilny finansowo
    else:
        return 3  # Impulsywny wydawca

records = []
user_id = 1

for style in [1, 2, 3]:
    n = num_users_group1 if style in [1,2] else num_users_group3
    for _ in range(n):
        features = generate_user_data(style)
        classified_style = classify_spending_style(features)
        features["spending_style"] = classified_style
        features["user_id"] = user_id
        records.append(features)
        user_id += 1

df_realistic_features = pd.DataFrame(records)

csv_filename = "training_data_financials_realistic_features_10000.csv"
df_realistic_features.to_csv(csv_filename, index=False)

print("Plik CSV wygenerowany:", csv_filename)

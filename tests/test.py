import requests
from datetime import datetime, timedelta

# === 🔐 KROK 1: Twoje dane z panelu GoCardless Bank Data ===

# === 🏦 KROK 2: Wybierz bank (możesz testować np. SANDBOX-MBANK) ===
INSTITUTION_ID = "PKO_BPKOPLPW"  # lub "PKO_BPKOPLPW" dla produkcji

# === 🌐 ENDPOINTS API ===
BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"
TOKEN_URL = f"{BASE_URL}/token/new/"
REQUISITION_URL = f"{BASE_URL}/requisitions/"

# === 🧠 Zmienna do przechowania danych użytkownika ===
user_bank_connection = {
    "user_id": 1,
    "requisition_id": None,
    "created_at": None
}


def get_access_token():
    """Uzyskanie tymczasowego access_token na 1h"""
    response = requests.post(TOKEN_URL, json={
        "secret_id": CLIENT_ID,
        "secret_key": CLIENT_SECRET
    })
    if response.status_code == 200:
        token = response.json()["access"]
        print("✅ Access token uzyskany.")
        return token
    else:
        raise Exception(f"❌ Nie udało się uzyskać tokenu: {response.text}")


def create_bank_link(access_token):
    """Tworzy link do połączenia bankowego"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "redirect": "https://harmoney.app/bank-connected",
        "institution_id": INSTITUTION_ID,
        "reference": f"user-{user_bank_connection['user_id']}",
        "user_language": "PL"
    }

    response = requests.post(REQUISITION_URL, headers=headers, json=payload)

    if response.status_code == 201:
        data = response.json()
        user_bank_connection["requisition_id"] = data["id"]
        user_bank_connection["created_at"] = datetime.utcnow()

        print("\n🔗 Link do logowania w banku:")
        print(data["link"])
        print(f"📎 Requisition ID: {data['id']}")
    else:
        print("❌ Błąd przy tworzeniu requisition:", response.text)


def check_if_expired():
    """Sprawdza czy minęło 85 dni od ostatniego połączenia"""
    if not user_bank_connection["created_at"]:
        return True

    days_passed = (datetime.utcnow() - user_bank_connection["created_at"]).days
    if days_passed > 85:
        print(f"⏰ Minęło już {days_passed} dni od połączenia — trzeba odnowić")
        return True
    else:
        print(f"✅ Połączenie ważne ({days_passed} dni temu)")
        return False


if __name__ == "__main__":
    print("=== Harmoney: Bank Connect Test ===\n")

    try:
        token = get_access_token()

        if check_if_expired():
            create_bank_link(token)
        else:
            print("ℹ️ Nie trzeba jeszcze odnawiać połączenia.")
    except Exception as e:
        print("❌ Błąd krytyczny:", e)
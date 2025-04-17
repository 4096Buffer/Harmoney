from fastapi import APIRouter, Request, Depends, Cookie
from api.helpers.bank_helper import BankHelper
import api.helpers.database as db
from jose import jwt
import api.settings

router = APIRouter()
database = db.DataBase()
bank = BankHelper()

def get_user_id_from_token(access_token: str = Cookie(None)):
    if not access_token:
        return -1
    try:
        payload = jwt.decode(access_token, api.settings.SECRET_KEY, algorithms=[api.settings.ALGORITHM])
        return int(payload["uid"])
    except Exception:
        return -1

@router.get("/")
def get_transactions(uid: int = Depends(get_user_id_from_token)):
    if uid < 0:
        return {"message": "Invalid token", "code": 0}

    conn_row = database.Get("SELECT * FROM user_bank_connections WHERE user_id = :id", {"id": uid})
    if conn_row.empty:
        return {"message": "Nie masz podłączonego konta bankowego.", "code": 0}

    requisition_id = conn_row.iloc[0]["requisition_id"]

    try:
        account_id = bank.get_account_id(requisition_id)
        tx_data = bank.get_transactions(account_id)

        booked = tx_data.get("transactions", {}).get("booked", [])[:10]
        simplified = []

        for tx in booked:
            simplified.append({
                "date": tx.get("bookingDate"),
                "description": tx.get("remittanceInformationUnstructured", "Brak opisu"),
                "amount": tx.get("transactionAmount", {}).get("amount"),
                "currency": tx.get("transactionAmount", {}).get("currency"),
            })

        return {"message": simplified, "code": 1}

    except Exception as e:
        return {"message": f"Błąd: {str(e)}", "code": 0}
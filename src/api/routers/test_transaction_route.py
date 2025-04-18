from fastapi import APIRouter, Request, Depends, Cookie
from fastapi.responses import JSONResponse
from api.helpers.bank_helper import BankHelper
import api.helpers.database as db
from jose import jwt
import api.settings
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

router = APIRouter()
database = db.DataBase()
bank = BankHelper()
fernet = Fernet(api.settings.BANK_ENCRYPTION_KEY)

def get_user_id_from_token(access_token: str = Cookie(None)):
    if not access_token:
        return -1
    try:
        payload = jwt.decode(
            access_token, api.settings.SECRET_KEY, algorithms=[api.settings.ALGORITHM]
        )
        return int(payload["uid"])
    except Exception:
        return -1


@router.get("/")
def get_full_transactions(
    request: Request,
    uid: int = Depends(get_user_id_from_token),
):
    host = request.headers.get("host")
    domain = host.split(":")[0]

    if uid < 0:
        return {"message": "Invalid token", "code": 0}

    # Brak ciasteczka lub błędne dane – pobieramy z GoCardless
    conn_row = database.Get(
        "SELECT * FROM user_bank_connections WHERE user_id = :id", {"id": uid}
    )
    if conn_row.empty:
        return {"message": "Nie masz podłączonego konta bankowego.", "code": 0}

    if conn_row.iloc[0]["last_used"] is not None:
        if (datetime.now() - conn_row.iloc[0]["last_used"]) < timedelta(hours=24):
            return {"message" : "You have hit the limit", "code" : 0}

    requisition_id = fernet.decrypt(conn_row.iloc[0]["requisition_id"].encode()).decode()

    try:
        account_id = bank.get_account_id(requisition_id)
        tx_data = bank.get_transactions(account_id)
        transactions = tx_data.get("transactions", {})

        # Zapisujemy transakcje do ciasteczka na 24h
        response = JSONResponse(
            content={"message": transactions, "cached": False, "code": 1}
        )
        
        query = database.Update({"last_used" : "now()"}, conn_row.iloc[0]["id"], "user_bank_connections")

        if not query:
            return {"message" : "error", "code" : 0}

        return response

    except Exception as e:
        return {"message": f"Błąd: {str(e)}", "code": 0}

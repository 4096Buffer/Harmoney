from fastapi import APIRouter, Request, Depends, Cookie
from fastapi.responses import JSONResponse
from api.helpers.bank_helper import BankHelper
import api.helpers.database as db
from jose import jwt
import api.settings
import json
from datetime import datetime, timedelta

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
def get_full_transactions(
    request: Request,
    transactions_cache: str = Cookie(default=None),
    uid: int = Depends(get_user_id_from_token),
):
    if uid < 0:
        return {"message": "Invalid token", "code": 0}

    # Jeśli istnieje ciasteczko – parsujemy i zwracamy
    if transactions_cache:
        try:
            transactions = json.loads(transactions_cache)
            return {"message": transactions, "cached": True, "code": 1}
        except:
            pass  # coś poszło nie tak — pobieramy z API poniżej

    # Brak ciasteczka lub błędne dane – pobieramy z GoCardless
    conn_row = database.Get("SELECT * FROM user_bank_connections WHERE user_id = :id", {"id": uid})
    if conn_row.empty:
        return {"message": "Nie masz podłączonego konta bankowego.", "code": 0}

    requisition_id = conn_row.iloc[0]["requisition_id"]

    try:
        account_id = bank.get_account_id(requisition_id)
        tx_data = bank.get_transactions(account_id)
        transactions = tx_data.get("transactions", {})

        # Zapisujemy transakcje do ciasteczka na 24h
        response = JSONResponse(content={"message": transactions, "cached": False, "code": 1})
        expire_time = 60 * 60 * 24  # 24 godziny w sekundach

        response.set_cookie(
            key="transactions_cache",
            value=json.dumps(transactions),
            max_age=expire_time,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response

    except Exception as e:
        return {"message": f"Błąd: {str(e)}", "code": 0}
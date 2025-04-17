# src/api/routers/connect_with_bank_route.py

from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import api.helpers.database as db
from api.helpers.bank_helper import BankHelper
from pydantic import BaseModel
from jose import jwt
import api.settings

router = APIRouter()
database = db.DataBase()
bank = BankHelper()


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


class InputData(BaseModel):
    bank_name: str


@router.post("/")
def connect_with_bank(
    request: Request,
    data: InputData,
    uid: int = Depends(get_user_id_from_token),
):
    bank_name = data.bank_name

    if not bank_name in bank.allowed_banks:
        return {
            "message": "This bank is not supported or the code is invalid",
            "code": 0,
        }

    user_rows = database.Get("SELECT * FROM users WHERE id = :id", {"id": uid})

    if user_rows.empty:
        return {"message": "This user id is not correct.", "code": 0}

    connection_row = database.Get(
        "SELECT * FROM user_bank_connections WHERE user_id = :id", {"id": uid}
    )

    if not connection_row.empty:
        row = connection_row.iloc[0]
        created_at = row["created_at"]
        bank_linked = bank.check_requisition_status(row["requisition_id"]) == "LN"

        if (datetime.utcnow() - created_at).total_seconds() < 600:
            return {
                "message": "Successfully created bank connect link.",
                "link": row["link"],
                "code": 1,
            }

        if (datetime.utcnow() - created_at).days < 85 and bank_linked:
            return {
                "message": "Current connection is still valid. Can't create a new one.",
                "code": 0,
            }

    try:
        result = bank.create_requisition(bank_name, uid)

        requisition_id = result["requisition_id"]
        link = result["link"]

        if connection_row.empty:
            success = database.Insert(
                {
                    "user_id": uid,
                    "requisition_id": requisition_id,
                    "created_at": datetime.utcnow(),
                    "link": link,
                },
                "user_bank_connections",
            )
        else:
            success = database.Update(
                {
                    "requisition_id": requisition_id,
                    "created_at": "now()",
                    "link" : link
                },
                connection_row.iloc[0]["id"],
                "user_bank_connections",
            )

        if not success:
            return {
                "message": "Database error. Please try again later.",
                "code": 0,
            }

        return {
            "message": "Successfully created bank connect link.",
            "link": link,
            "code": 1,
        }

    except Exception as e:
        return {
            "message": "Unknown error occurred",
            "code": 0,
        }

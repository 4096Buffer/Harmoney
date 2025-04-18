# src/api/routers/email_verify_route.py

import api.helpers.database as db
from fastapi import APIRouter, Response, Request, Cookie, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Union
from argon2 import PasswordHasher
from jose import jwt
from datetime import datetime, timedelta
import api.settings
import re
import uuid
from api.helpers.emailer import Emailer

router = APIRouter()
database = db.DataBase()
emailer = Emailer()


def get_user_id_from_token(access_token: str = Cookie(None)):
    if not access_token:
        return -1
    try:
        payload = jwt.decode(
            access_token, api.settings.SECRET_KEY, algorithms=[api.settings.ALGORITHM]
        )
        return int(payload["uid"])
    except Exception as e:
        return -1


@router.get("/")
def verify_email(
    request: Request,
    uid: int = Depends(get_user_id_from_token),
    mode: int = 0,
    token: str = "",
):
    host = request.headers.get("host")
    domain = host.split(":")[0]

    if mode < 0 or mode > 1:
        return {"message": "The provided mode is not correct.", "code": 0}

    rows = database.Get("SELECT * FROM users WHERE id = :id", {"id": uid})

    if rows.empty:
        return {"message": "The provided user id is not correct.", "code": 0}

    row = rows.iloc[0]

    if row["email_verified"]:
        return {"message": "This email is already verified", "code": 0}

    user_tokens = database.Get(
        "SELECT * FROM email_verify_tokens WHERE user_id = :id", {"id": uid}
    )

    if user_tokens is None:
        return {"message": "Unknown error occured", "code": 0}

    user_token = None

    if not user_tokens.empty:
        user_token = user_tokens.iloc[-1]

    if mode == 0:
        if user_token is not None:
            if user_token["expires_at"] > datetime.utcnow() and user_token["active"]:
                return {"message": "You have an active token!", "code": 0}
            else:
                query = database.Update(
                    {"active": False}, user_token["id"], "email_verify_tokens"
                )

                if not query:
                    return {"message": "Unknown error occured", "code": 0}

        gen_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        query = database.Insert(
            {
                "token": gen_token,
                "expires_at": expires_at,
                "user_id": uid,
                "active": True,
            },
            "email_verify_tokens",
        )

        if not query:
            return {"message": "Unknown error occured", "code": 0}

        emailer.send_email(
            row["email"],
            f"Witaj w Harmoney {row['name']}! - Zweryfikuj e-mail",
            f'<a href="http://127.0.0.1:8000/email-verify?token={gen_token}&mode=1">Zweryfikuj konto</a>',
        )

        return {"message": "Successfully sent email", "code": 1}
    else:
        token_row = database.Get(
            "SELECT * FROM email_verify_tokens WHERE token = :token AND user_id = :uid",
            {"token": token, "uid": uid},
        )

        if token_row.empty:
            return {"message": "Invalid token", "code": 0}

        if user_token["expires_at"] < datetime.utcnow() or not user_token["active"]:
            return {"message": "The token is expired", "code": 0}

        query = database.Update({"email_verified": True}, uid, "users")
        query2 = database.Update(
            {"active": False}, user_token["id"], "email_verify_tokens"
        )

        if not query or not query2:
            return {"message": "Unknown error occured", "code": 0}

        return {"message": "Successfully verified email", "code": 1}

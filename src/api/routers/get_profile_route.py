# src/api/routers/get_profile_route.py

import api.helpers.database as db
from fastapi import APIRouter, Response, Request, Cookie, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Union
from argon2 import PasswordHasher
from jose import jwt, ExpiredSignatureError
from datetime import datetime, timedelta
import api.settings
import pandas as pd

database = db.DataBase()
router = APIRouter()


def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=api.settings.ACCESS_TOKEN_EXPIRES)
    data.update({"exp": expire})

    return jwt.encode(data, api.settings.SECRET_KEY, algorithm=api.settings.ALGORITHM)


def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token, api.settings.SECRET_KEY, algorithms=[api.settings.ALGORITHM]
        )

        return 1, int(payload["uid"])
    except ExpiredSignatureError:
        return 2, "The token is expired"
    except JWTError:
        return 2, "The token is not valid"


@router.post("/")
def get_profile(
    request: Request,
    access_token: str = Cookie(None),
    refresh_token: str = Cookie(None),
):
    host = request.headers.get("host")
    domain = host.split(":")[0]

    if not access_token:
        access_token = ""

    code, result = verify_token(access_token)
    uid = None
    new_access_token = None

    if code == 2:
        if not refresh_token:
            return {"message": "You are not logged in", "code": 0}
        try:
            payload = jwt.decode(
                refresh_token,
                api.settings.SECRET_KEY,
                algorithms=[api.settings.ALGORITHM],
            )
            token_uid = payload.get("uid")
            sub = payload.get("sub")

            if token_uid is None or sub is None:
                return {"message": "The refresh token is not valid.", "code": 0}

            new_access_token = create_access_token({"uid": token_uid, "sub": sub})
            uid = token_uid
        except Exception as e:
            return {"message": "The refresh token is not valid or idk", "code": 0}
    if code == 1:
        uid = result

    rows = database.Get("SELECT * FROM users WHERE id = :id", {"id": uid})

    if rows.empty:
        return {"message": "The token is not valid"}

    row = rows.iloc[0].drop(labels=["password"])
    data = row.to_dict()

    for key, val in data.items():
        if isinstance(val, pd.Timestamp):
            data[key] = val.isoformat()

    response = JSONResponse(content={"message": data, "code": 1})

    if new_access_token is not None:
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="None",
            domain=domain,
            max_age=15 * 60,
        )

    return response

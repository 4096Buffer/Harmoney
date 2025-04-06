# src/api/routers/sign_in_route.py

import api.helpers.database as db
from fastapi import APIRouter, Response, Request, Cookie, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Union
from argon2 import PasswordHasher
from jose import jwt
from datetime import datetime, timedelta
import api.settings


database = db.DataBase()
router = APIRouter()


class InputData(BaseModel):
    email: str
    password: str


def create_token(data: dict, expires_minutes: int = 0, expires_days: int = 0):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes, days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, api.settings.SECRET_KEY, algorithm=api.settings.ALGORITHM
    )


@router.post("/")
def sign_in(data: InputData, response: Response, request: Request):
    host = request.headers.get("host")
    domain = host.split(":")[0]

    email = data.email
    password = data.password

    try:
        rows = database.Get("SELECT * FROM users WHERE email = :email", {"email": email})
    except:
        return {"message" : "Unknown error occured.", "code" : 0}
    if rows.empty:
        return {"message": "The email or password is not correct", "code": 0}

    ph = PasswordHasher()

    row = rows.iloc[0]
    row_password = row["password"]

    try:
        ph.verify(row_password, password)
    except:
        return {"message": "The email or password is not correct", "code": 0}

    data = {"uid": str(row["id"]), "sub": row["email"]}

    access_token = create_token(data, expires_minutes=15)
    refresh_token = create_token(data, expires_days=7)

    response = JSONResponse(content={"message": "Success", "code": 1})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60,
        domain=domain,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60,
        domain=domain,
    )

    try:
        database.Update({"is_active": True}, row["id"], "users")
    except:
        return {"message" : "Unknown error occured.", "code" : 0}

    return response

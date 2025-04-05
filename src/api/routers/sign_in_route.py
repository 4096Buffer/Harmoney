# src/api/routers/sign_in_route.py

import api.helpers.database as db
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Union
from argon2 import PasswordHasher

database = db.DataBase()
router = APIRouter()


class InputData(BaseModel):
    email: str
    password: str


@router.post("/")
def sign_in(data: InputData):
    email = data.email
    password = data.password

    rows = database.Get("SELECT * FROM users WHERE email = :email", {"email": email})

    if rows.empty:
        return {"message": "The email or password is not correct"}

    ph = PasswordHasher()

    row = rows.iloc[0]
    row_password = row["password"]

    try:
        ph.verify(row_password, password)

        return {"message": "Success"}
    except:
        return {"message": "The email or password is not correct"}

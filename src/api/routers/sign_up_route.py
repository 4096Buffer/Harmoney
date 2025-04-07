# src/api/routers/sign_up_route.py

import api.helpers.database as db
from fastapi import APIRouter, Response, Request, Cookie, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Union
from argon2 import PasswordHasher
from jose import jwt
from datetime import datetime, timedelta
import api.settings
import re
from api.helpers.emailer import Emailer

database = db.DataBase()
router = APIRouter()
emailer = Emailer()


class InputData(BaseModel):
    name: str
    password: str
    email: str
    surname: str

def check_password_strengh(password: str):
    if len(password) < 8:
        return False, "The password must be at least 8 characters long."

    lower_letter = False
    upper_letter = False
    number = False
    schar = False

    for c in password:
        if not lower_letter and c.isalpha():
            lower_letter = c == c.lower()

        if not upper_letter and c.isalpha():
            upper_letter = c == c.upper()

        if not number:
            try:
                int(c)
                number = True
            except:
                pass

        if not schar:
            schar = not c.isalpha() and not c.isdigit()

    if not lower_letter or not upper_letter:
        return (
            False,
            "Password must contain at least one lower letter and one upper letter!",
        )

    if not number:
        return False, "Password must contain at least one number!"

    if not schar:
        return False, "Password must contain at least one special character!"

    return True, ""


@router.post("/")
def sign_up(data: InputData):
    name = data.name
    password = data.password
    email = data.email
    surname = data.surname

    if len(name) < 2 and len(name) > 30:
        return {
            "message": "The name exceeded maximum character count. Max - 30",
            "code": 0,
        }

    if len(surname) < 2 and len(surname) > 35:
        return {
            "message": "The surname exceeded maximum character count. Max - 35",
            "code": 0,
        }

    regex = "^[^\s@]+@[^\s@]+\.[^\s@]+$"

    if not re.match(regex, email):
        return {"message": "The email is not correct.", "code": 0}

    result, reason = check_password_strengh(password)

    if not result:
        return {"message": reason, "code": 0}

    try:
        rows = database.Get(
            "SELECT * FROM users WHERE email = :email", {"email": email}
        )
    except:
        return {"message": "Unknown error occured.", "code": 0}

    if not rows.empty:
        return {
            "message": "If this email is not yet registered, your account will be created shortly.",
            "code": 1,
        }

    ph = PasswordHasher()
    password_hash = ph.hash(password)

    try:
        # Później dodać tutaj potwierdzenie najpierw emailem.

        database.Insert(
            {
                "name": name,
                "surname": surname,
                "password": password_hash,
                "email": email,
                "plan": 0,
                "settings": '{ "language" : "PL", "mode" : "dark" }',
                "is_active": False,
                "email_verified": False,
            },
            "users",
        )

    except Exception as e:
        return {"message": "Unknown error occured", "code": 0}

    emailer.send_email(email, "Welcome to Harmoney! Verify your email.", "Click here to verify your email->")

    return {
        "message": "If this email is not yet registered, your account will be created shortly.",
        "code": 1,
    }

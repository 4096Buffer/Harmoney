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


@router.post("/")
def sign_up(data: InputData):
    pass

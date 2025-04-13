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

router = APIRouter()
database = db.DataBase()

class InputData(BaseModel):
    prompt: str

@router.post("/")
def ask(data: InputData):
    pass
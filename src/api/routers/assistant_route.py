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

@router.post("/")
def ask(request: Request, data: InputData, uid: int = Depends(get_user_id_from_token)):
    if uid < 0:
        return {"message" : "Invalid access token", "code" : 0}
    
    row = database.Get("SELECT * FROM users WHERE id = :id", { "id" : uid })
    
    plan = row['plan']
    plan_options = database.Get("SELECT * FROM plans_options WHERE plan_id = :id", { "id" : plan })

    if plan_options['ai_assistant_limit'] == 0:
        return {"message" : "You don't have access to this feature", "code" : 0}

    month_now = datetime.now().month
    year_now  = datetime.now().year

    tokens_used = database.Get("SELECT * FROM monthly_token_usage WHERE user_id = :uid AND month == :month AND year == :year", {"uid": uid, "month" : month_now, "year" : year_now})
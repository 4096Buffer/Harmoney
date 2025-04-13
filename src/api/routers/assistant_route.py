# src/api/routers/assistant_route.py

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
from core.assistant import Assistant
import asyncio

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
async def ask(request: Request, data: InputData, uid: int = Depends(get_user_id_from_token)):
    prompt = data.prompt

    if uid < 0:
        return {"message": "Invalid access token", "code": 0}

    row = database.Get("SELECT * FROM users WHERE id = :id", {"id": uid})

    plan = row["plan"]
    plan_options = database.Get(
        "SELECT * FROM plans_options WHERE plan_id = :id", {"id": int(plan)}
    )

    if int(plan_options["ai_assistant_limit"].iloc[0]) == 0:
        return {"message": "You don't have access to this feature", "code": 0}

    month_now = datetime.now().month
    year_now = datetime.now().year
    prompt_count = len(prompt)

    if prompt_count < 1:
        return {"message": "The prompt cannot be empty", "code": 0}

    if prompt_count > 5000:
        return {"message": "Prompt is too long", "code": 0}

    chars_used = database.Get(
        "SELECT * FROM monthly_token_usage WHERE user_id = :uid AND month = :month AND year = :year",
        {"uid": uid, "month": month_now, "year": year_now},
    )

    if chars_used.empty:
        database.Insert(
            {
                "user_id": uid,
                "month": month_now,
                "year": year_now,
                "chars_used": prompt_count,
            },
            "monthly_token_usage",
        )
    else:
        if chars_used["chars_used"].iloc[0] + prompt_count > int(
            plan_options["ai_assistant_limit"].iloc[0]
        ):
            return {"message": "You have reached your monthly limit.", "code": 0}

        database.Update(
            {"chars_used": int(chars_used["chars_used"].iloc[0] + prompt_count)},
            chars_used["id"],
            "monthly_token_usage",
        )

    assistant = Assistant(None)

    response = await asyncio.get_event_loop().run_in_executor(
        None, assistant.Ask, prompt
    )

    return {"message": response, "code": 1}

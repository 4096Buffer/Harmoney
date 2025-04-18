# src/api/routers/get_convos_route.py

import api.helpers.database as db
from fastapi import APIRouter, Response, Request, Cookie, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from argon2 import PasswordHasher
from jose import jwt
import api.settings

router = APIRouter()
database = db.DataBase()

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
async def ask(
    request: Request, uid: int = Depends(get_user_id_from_token)
):
    if uid < 0:
        return {"message": "Invalid access token", "code": 0}

    row = database.Get("SELECT * FROM users WHERE id = :id", {"id": uid})

    if row is None:
        return {"message" : "Unknown error occured", "code" : 0}

    convos = database.Get("SELECT * FROM assistant_conversations WHERE user_id = :id", {"id" : uid})

    if convos is None:
        return {"message" : "Unknown error occured", "code" : 0}

    if convos.empty:
        return {"message" : "No convos yet", "code" : 0}

    structured_convos = []

    for index, row in convos.iterrows():
        messages = database.Get("SELECT * FROM assistant_conversations_messages WHERE conversation_id = :id", {"id" : row["id"]})

        if messages is None:
            return {"message" : "Unknown error occured", "code" : 0}

        prompts_and_responses = []

        for i, r in messages.iterrows():
            prompts_and_responses.append({"prompt" : r["user_message"], "response" : r["assistant_response"]})

        structured_convos.append({"id" : row["id"], "messages" : prompts_and_responses})
    
    return {"message" : structured_convos, "code" : 1}


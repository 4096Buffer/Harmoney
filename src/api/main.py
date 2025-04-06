# src/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.spend_style_route import router as spend_style_router
from api.routers.future_spend_route import router as future_spend_router
from api.routers.sign_in_route import router as sign_in_router
from api.settings import create_engine
import api.helpers.database as db

app = FastAPI(
    title="Harmoney API", description="Asystent finansowy oparty o AI", version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spend_style_router, prefix="/spend-style", tags=["SpendStyle"])
app.include_router(future_spend_router, prefix="/future-spend", tags=["FutureSpend"])
app.include_router(sign_in_router, prefix="/sign-in", tags=["SignIn"])


@app.get("/")
def root():
    return {"message": "Error: Empty request"}

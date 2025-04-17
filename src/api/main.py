# src/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.spend_style_route import router as spend_style_router
from api.routers.future_spend_route import router as future_spend_router
from api.routers.sign_in_route import router as sign_in_router
from api.routers.sign_up_route import router as sign_up_router
from api.routers.get_profile_route import router as get_profile_router
from api.routers.email_verify_route import router as email_verify_router
from api.routers.assistant_route import router as assistant_router
from api.routers.conbank_route import router as conbank_router

from api.settings import create_engine
import api.helpers.database as db

app = FastAPI(
    title="Harmoney API", description="Asystent finansowy oparty o AI", version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spend_style_router, prefix="/spend-style", tags=["SpendStyle"])
app.include_router(future_spend_router, prefix="/future-spend", tags=["FutureSpend"])
app.include_router(sign_in_router, prefix="/sign-in", tags=["SignIn"])
app.include_router(sign_up_router, prefix="/sign-up", tags=["SignUp"])
app.include_router(get_profile_router, prefix="/profile", tags=["Profile"])
app.include_router(email_verify_router, prefix="/email-verify", tags=["EmailVerify"])
app.include_router(assistant_router, prefix="/ask-assistant", tags=["AskAssistant"])
app.include_router(conbank_router, prefix="/connect-bank", tags=["ConnectBank"])

@app.get("/")
def root():
    return {"message": "Error: Empty request"}

# src/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.spend_style_route import router as spend_style_router

app = FastAPI(
    title="Harmoney API",
    description="Asystent finansowy oparty o AI",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spend_style_router, prefix="/spend-style", tags=["SpendStyle"])

@app.get("/")
def root():
    return {"message": "Error: Empty request"}
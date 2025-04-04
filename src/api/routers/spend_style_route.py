# src/api/routers/spend_style_route .py

from fastapi import APIRouter
from pydantic import BaseModel
from core.ustyle import UStyle

router = APIRouter()

class InputData(BaseModel):
    data : list[float]

ustyle = UStyle()

@router.post("/")
def get_style(data : InputData):
    try:
        pred = ustyle.Predict([data.data])
    except:
        return {"message" : "Wrong data has been passed."}
    
    return {"message": f"{pred}"}
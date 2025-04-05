# src/api/routers/spend_style_route .py

from fastapi import APIRouter
from pydantic import BaseModel
from core.future_spend import FutureSpend
from typing import Dict, Union

router = APIRouter()


class InputData(BaseModel):
    data: Dict[str, Union[float, int]]
    # user_data : Dict[str, Union[float, int]] - dodac po dodaniu integracji z bankiem


future_spend = FutureSpend()


@router.post("/")
def get_future_spend(data: InputData):
    try:
        pred = future_spend.Predict(data.data)
    except:
        return {"message": "Error passed data is not correct."}

    return {"message": pred}

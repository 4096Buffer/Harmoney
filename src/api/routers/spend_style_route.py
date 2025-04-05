# src/api/routers/spend_style_route .py

from fastapi import APIRouter
from core.ustyle import UStyle
from pydantic import BaseModel, Field
from typing import List, Union

router = APIRouter()


class InputData(BaseModel):
    data: List[Union[float, int]] = Field(..., min_items=7, max_items=7)


ustyle = UStyle()


@router.post("/")
def get_style(data: InputData):
    try:
        pred = ustyle.Predict([data.data])
    except:
        return {"message": "Wrong data has been passed."}

    return {"message": f"{pred}"}

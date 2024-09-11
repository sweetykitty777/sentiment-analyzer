from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.models.check import SentimentCheckResponse
from app.services.sentiment_predict import SentimentPredict

predict = SentimentPredict()
router = APIRouter()


@router.get("/check")
def read_item(text: str = Query(min_length=1, max_length=512)) -> SentimentCheckResponse:
    return SentimentCheckResponse(text=text, sentiment=predict.predict(text))


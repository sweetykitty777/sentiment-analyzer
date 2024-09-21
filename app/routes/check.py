from fastapi import APIRouter, Query

from app.models.check import (
    SentimentCheckResponse,
    SentimentCheckResult,
)
from app.services.sentiment_predict import SentimentPredict

predict = SentimentPredict()
router = APIRouter()


@router.get("/check")
def read_item(
    text: list[str] = Query(..., min_items=1, max_items=10, max_length=1000),
) -> SentimentCheckResponse:
    results = []
    for text in text:
        results.append(SentimentCheckResult(text=text, sentiment=predict.predict(text)))

    return SentimentCheckResponse(results=results)

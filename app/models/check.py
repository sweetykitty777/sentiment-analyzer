from pydantic import BaseModel

from app.services.sentiment_predict import SentimentPredictLevel


class SentimentCheckResult(BaseModel):
    text: str
    sentiment: SentimentPredictLevel


class SentimentCheckResponse(BaseModel):
    results: list[SentimentCheckResult]

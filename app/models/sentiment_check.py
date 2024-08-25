from pydantic import BaseModel

from app.services.sentiment_predict import SentimentPredictLevel


class SentimentCheckResponse(BaseModel):
    text: str
    sentiment: SentimentPredictLevel

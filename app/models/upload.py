from datetime import datetime

from pydantic import BaseModel

from app.services.sentiment_predict import SentimentPredictLevel


class UploadBase(BaseModel):
    name: str


class UploadShort(UploadBase):
    upload_id: int
    created_at: datetime
    created_by: str | None = None


class UploadEntry(BaseModel):
    text: str
    sentiment: SentimentPredictLevel


class UploadFull(UploadShort):
    entries: list[UploadEntry]

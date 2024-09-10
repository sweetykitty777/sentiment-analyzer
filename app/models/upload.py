import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import UUID4
from sqlmodel import Field, Relationship, SQLModel

from app.services.sentiment_predict import SentimentPredictLevel


class UploadStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class UploadBase(SQLModel):
    name: str


class Upload(UploadBase, table=True):
    id: int = Field(primary_key=True, default=None)
    created_at: datetime = Field(default=datetime.now())
    created_by: str = Field(foreign_key="user.id")
    status: UploadStatus = UploadStatus.PENDING
    entries: list["UploadEntry"] = Relationship(back_populates="upload")


class UploadPublic(UploadBase):
    id: int
    created_at: datetime
    created_by: str | None = None
    status: UploadStatus


class UploadWithEntries(UploadPublic):
    entries: list["UploadEntryWithoutUpload"] = []


class UploadEntryBase(SQLModel):
    id: int = Field(primary_key=True)
    text: str
    sentiment: SentimentPredictLevel | None = None


class UploadEntry(UploadEntryBase, table=True):
    upload_id: int = Field(foreign_key="upload.id", primary_key=True)
    upload: Upload = Relationship(back_populates="entries")


class UploadEntryPublic(UploadEntryBase):
    id: int


class UploadEntryWithoutUpload(UploadEntryBase):
    pass

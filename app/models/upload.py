from datetime import datetime

from pydantic import UUID4
from sqlmodel import SQLModel, Field, Relationship

from app.services.sentiment_predict import SentimentPredictLevel


class UploadBase(SQLModel):
    name: str


class Upload(UploadBase, table=True):
    id: UUID4 | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    created_by: str = Field(foreign_key="user.id")

    entries: list["UploadEntry"] = Relationship(back_populates="upload")


class UploadPublic(UploadBase):
    id: int
    created_at: datetime
    created_by: str | None = None


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

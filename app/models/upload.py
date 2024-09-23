from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User
from app.services.sentiment_predict import SentimentPredictLevel


class UploadEntryBase(SQLModel):
    id: int = Field(primary_key=True)
    text: str
    description: str | None = None
    sentiment: SentimentPredictLevel | None = None


class UploadEntry(UploadEntryBase, table=True):
    upload_id: int = Field(foreign_key="upload.id", primary_key=True)
    upload: "Upload" = Relationship(back_populates="entries")
    description: str | None = None

class UploadEntryPublic(UploadEntryBase):
    id: int


class UploadEntryWithoutUpload(UploadEntryBase):
    pass


class UploadStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class UploadBase(SQLModel):
    name: str


class UploadFormat(StrEnum):
    PLAIN = "plain"
    INTERVIEW_2 = "interview-2"

class Upload(UploadBase, table=True):
    id: int = Field(primary_key=True, default=None)
    created_at: datetime = Field(default=datetime.now())
    created_by_user_id: str = Field(foreign_key="user.id")
    status: UploadStatus = UploadStatus.PENDING
    entries: list["UploadEntry"] = Relationship(back_populates="upload")
    format: UploadFormat = UploadFormat.PLAIN
    created_by: User = Relationship(back_populates="uploads")


class UploadPublic(UploadBase):
    id: int
    created_at: datetime
    status: UploadStatus
    created_by: User
    format: UploadFormat = UploadFormat.PLAIN


class UploadWithEntries(UploadPublic):
    entries: list["UploadEntryWithoutUpload"] = []

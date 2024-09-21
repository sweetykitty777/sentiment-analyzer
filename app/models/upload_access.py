from enum import StrEnum

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class AccessRecipientType(StrEnum):
    USER = "user"
    ORG = "org"

class UploadAccessRequest(BaseModel):
    recipient_id: str
    recipient_type: AccessRecipientType

class UploadAccess(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    recipient_id: str
    recipient_type: AccessRecipientType
    upload_id: int = Field(foreign_key="upload.id")

class UploadAccessRecipientResponse(BaseModel):
    recipient_id: str
    name: str
    recipient_type: AccessRecipientType


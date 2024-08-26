from enum import StrEnum

from pydantic import BaseModel


class AccessRecipientType(StrEnum):
    USER = 'user'
    ORG = 'org'


class UploadAccess(BaseModel):
    recipient_id: str
    recipient_type: AccessRecipientType
    upload_id: int

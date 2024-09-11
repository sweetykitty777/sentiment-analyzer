from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.upload import Upload


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: EmailStr
    organization: str
    uploads: list["Upload"] = Relationship(back_populates="created_by")
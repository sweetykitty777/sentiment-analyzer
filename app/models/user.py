from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: EmailStr
    organization: str

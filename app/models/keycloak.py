from pydantic import BaseModel, ConfigDict


class IDToken(BaseModel):
    model_config = ConfigDict(extra="allow")

    iss: str
    sub: str
    aud: str | list[str]
    exp: int
    iat: int


class KeycloakIDToken(IDToken):
    email: str
    organization: dict[str, dict]

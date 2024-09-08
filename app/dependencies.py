from typing import Annotated

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OpenIdConnect
from sqlmodel import Session
from sqlmodel import create_engine

from .models.keycloak import KeycloakIDToken
from .models.upload import *  # noqa
from .models.user import User
from .settings import settings

engine = create_engine(settings.database_url)

SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


oauth_2_scheme = OpenIdConnect(openIdConnectUrl=f"{settings.oidc_base_url}/.well-known/openid-configuration")


async def get_oidc_keycloak_user(
        access_token: Annotated[str, Depends(oauth_2_scheme)]
) -> KeycloakIDToken:
    url = f"{settings.oidc_base_url}/protocol/openid-connect/certs"

    optional_custom_headers = {"User-agent": "custom-user-agent"}
    token = access_token.split(" ")[1]
    jwks_client = jwt.PyJWKClient(url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="profile",
            options={"verify_exp": True, "verify_aud": False, "verify_at_hash": False},
        )
        return KeycloakIDToken.validate(data)
    except jwt.exceptions.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Not authenticated: {e}")


def get_user(data: KeycloakIDToken = Depends(get_oidc_keycloak_user), session: Session = Depends(get_session)) -> User:
    if len(data.organization.keys()) == 0:
        raise HTTPException(status_code=500, detail="User has no organization")
    if len(data.organization.keys()) > 1:
        raise HTTPException(status_code=500, detail="User has more than one organization")

    current_user = User(id=data.sub, email=data.email, organization=next(iter(data.organization.keys())))
    db_user = session.get(User, data.sub)

    if db_user is None:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user

    if db_user != current_user:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    return current_user

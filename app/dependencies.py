from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OpenIdConnect
from sqlmodel import Session, SQLModel, create_engine, select

from .models.keycloak import KeycloakIDToken
from .models.upload import Upload
from .models.upload_access import AccessRecipientType, UploadAccess
from .models.user import User
from .settings import settings

engine = create_engine(settings.database_url)

SQLModel.metadata.create_all(engine)


def get_session() -> Session:  # type: ignore
    with Session(engine) as session:
        yield session


oauth_2_scheme = OpenIdConnect(
    openIdConnectUrl=f"{settings.oidc_base_url}/.well-known/openid-configuration"
)


async def get_oidc_keycloak_user(
    access_token: Annotated[str, Depends(oauth_2_scheme)],
) -> KeycloakIDToken:
    url = f"{settings.oidc_base_url}/protocol/openid-connect/certs"

    optional_custom_headers = {"User-agent": "custom-user-agent"}

    splited = access_token.split(" ")

    if len(splited) != 2:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    token = splited[1]

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
        return KeycloakIDToken.model_validate(data)
    except jwt.exceptions.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Not authenticated: {e}")


def get_user(
    data: KeycloakIDToken = Depends(get_oidc_keycloak_user),
    session: Session = Depends(get_session),
) -> User:
    org = None
    if data.organization:
        if len(data.organization.keys()) > 1:
            raise HTTPException(
                status_code=500, detail="User has more than one organization"
            )
        org = list(data.organization.keys())[0]

    current_user = User(id=data.sub, email=data.email, organization=org)

    db_user = session.get(User, data.sub)

    if db_user is None:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user

    if db_user != current_user:
        db_user.email = current_user.email
        db_user.organization = current_user.organization
        session.commit()
        session.refresh(db_user)

    return db_user


def get_upload_from_path(
    upload_id: int,
    user: User = Depends(get_user),
    session: Session = Depends(get_session),
) -> Upload:
    upload = session.exec(select(Upload).where(Upload.id == upload_id)).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    if upload.created_by_user_id == user.id:
        return upload

    access = session.exec(
        select(UploadAccess)
        .where(UploadAccess.upload_id == upload_id)
        .where(UploadAccess.recipient_id == user.id)
        .where(UploadAccess.recipient_type == AccessRecipientType.USER)
    ).first()
    if access:
        return upload

    if user.organization:
        access = session.exec(
            select(UploadAccess)
            .where(UploadAccess.upload_id == upload_id)
            .where(UploadAccess.recipient_id == user.organization)
            .where(UploadAccess.recipient_type == AccessRecipientType.ORG)
        ).first()
        if access:
            return upload

    raise HTTPException(status_code=403, detail="No access to upload")

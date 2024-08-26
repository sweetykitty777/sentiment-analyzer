from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
import jwt
from .routes.check import router as check_router
from .routes.uploads import router as file_router

app = FastAPI(title="sentiment-analyzer")

api_router = APIRouter(prefix="/api/v1/sentiment")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth_2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl="http://localhost:8085/realms/org/protocol/openid-connect/token",
    authorizationUrl="http://localhost:8085/realms/org/protocol/openid-connect/auth",
    refreshUrl="http://localhost:8085/realms/org/protocol/openid-connect/token",
)


async def valid_access_token(
    access_token: Annotated[str, Depends(oauth_2_scheme)]
):
    url = "http://localhost:8085/realms/org/protocol/openid-connect/certs"
    optional_custom_headers = {"User-agent": "custom-user-agent"}
    jwks_client = jwt.PyJWKClient(url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience="profile",
            options={"verify_exp": True, "verify_aud": False},
        )
        return data
    except jwt.exceptions.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Not authenticated: {e}")


@app.get("/", dependencies=[Depends(valid_access_token)])
async def read_root():
    return {"Hello": "World"}


api_router.include_router(file_router)
api_router.include_router(check_router)
app.include_router(api_router)

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer

from .dependencies import get_oidc_keycloak_user
from .routes.check import router as check_router
from .routes.uploads import router as upload_router
from .routes.users import router as user_router

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


@app.get("/", dependencies=[Depends(get_oidc_keycloak_user)])
async def read_root():
    return {"Hello": "World"}


api_router.include_router(user_router)
api_router.include_router(upload_router)
api_router.include_router(check_router)
app.include_router(api_router)

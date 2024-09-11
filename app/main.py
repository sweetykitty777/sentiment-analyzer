from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer

from .dependencies import get_oidc_keycloak_user
from .routes.check import router as check_router
from .routes.uploads import router as upload_router
from .routes.users import router as user_router
from .broker import broker

app = FastAPI(title="sentiment-analyzer")

api_router = APIRouter(prefix="/api/v1")

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

@app.on_event("startup")
async def app_startup():
    if not broker.is_worker_process:
        await broker.startup()


@app.on_event("shutdown")
async def app_shutdown():
    if not broker.is_worker_process:
        await broker.shutdown()

api_router.include_router(user_router)
api_router.include_router(upload_router)
api_router.include_router(check_router)
app.include_router(api_router)

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .broker import broker
from .routes.check import router as check_router
from .routes.uploads import router as upload_router
from .routes.users import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()


app = FastAPI(title="sentiment-analyzer", lifespan=lifespan)

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

api_router.include_router(user_router)
api_router.include_router(upload_router)
api_router.include_router(check_router)
app.include_router(api_router)

import io

import pandas as pd
from fastapi import FastAPI, UploadFile, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware

from .models.sentiment_check import SentimentCheckResponse
from .services.sentiment_predict import SentimentPredict

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

predict = SentimentPredict()


@api_router.get("/sentiment_check")
def read_item(text: str = Query(min_length=1, max_length=512)) -> SentimentCheckResponse:
    return SentimentCheckResponse(text=text, sentiment=predict.predict(text))


@api_router.get("/sentiment_check/file")
async def read_item(file: UploadFile) -> list[dict]:
    b = await file.read()
    df = pd.read_excel(io.BytesIO(b), header=None, index_col=None)
    df.columns = ['text']
    df['prediction'] = df.iloc[:, 0].apply(lambda x: predict.predict(x).name)

    return df.to_dict(orient="records")


app.include_router(api_router)

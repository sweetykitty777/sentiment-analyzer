import datetime
import io

import pandas as pd
from fastapi import APIRouter, UploadFile

from app.models.upload import UploadShort, UploadFull
from app.services.sentiment_predict import SentimentPredict

router = APIRouter()

predict = SentimentPredict()


@router.get("/uploads", summary="Get all uploads")
def get_upload() -> list[UploadShort]:
    return [UploadShort(upload_id=1, name="test.xlsx", created_at=datetime.datetime.now()),
            UploadShort(upload_id=2, name="test1.xlsx", created_at=datetime.datetime.now()),
            UploadShort(upload_id=3, name="test2.xlsx", created_at=datetime.datetime.now())]


@router.get("/my-uploads", summary="Get uploads for the current user")
def get_my_files() -> list[UploadShort]:
    return [UploadShort(upload_id=1, name="test.xlsx", created_at=datetime.datetime.now()),
            UploadShort(upload_id=2, name="test1.xlsx", created_at=datetime.datetime.now()),
            UploadShort(upload_id=3, name="test2.xlsx", created_at=datetime.datetime.now())]


@router.post("/uploads", summary="Upload a new file for sentiment check")
async def upload_file(file: UploadFile) -> list[dict]:
    b = await file.read()
    df = pd.read_excel(io.BytesIO(b), header=None, index_col=None)
    df.columns = ['text']
    df['prediction'] = df.iloc[:, 0].apply(lambda x: predict.predict(x).name)

    return df.to_dict(orient="records")


@router.get("/uploads/{upload_id}", summary="Get a specific upload")
def get_upload_by_id(upload_id: int) -> UploadFull:
    return UploadFull(upload_id=upload_id, name="test.xlsx", created_at=datetime.datetime.now(), entries=[])


@router.get("/uploads/{upload_id}/share", summary="Get a list of users that have access to the upload")
def get_upload_share(upload_id: int) -> list[str]:
    return ["user1", "user2", "user3"]


@router.post("/uploads/{upload_id}/share", summary="Share the upload with a user")
def share_upload(upload_id: int, user: str) -> str:
    return f"Upload {upload_id} shared with {user}"

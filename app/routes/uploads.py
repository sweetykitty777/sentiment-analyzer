import io

import pandas as pd
from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session, select

from app.broker import process_upload
from app.dependencies import get_session, get_user
from app.models.upload import Upload, UploadEntry, UploadStatus, UploadWithEntries
from app.models.user import User
from app.services.sentiment_predict import SentimentPredict

router = APIRouter()

predict = SentimentPredict()


@router.get("/uploads", summary="Get all uploads")
def get_upload(session: Session = Depends(get_session)) -> list[Upload]:
    res = session.exec(select(Upload)).all()
    return list(res)


# @router.get("/my-uploads", summary="Get uploads for the current user")
# def get_my_files() -> list[UploadShort]:
#     return [UploadShort(id=1, name="test.xlsx", created_at=datetime.datetime.now()),
#             UploadShort(id=2, name="test1.xlsx", created_at=datetime.datetime.now()),
#             UploadShort(id=3, name="test2.xlsx", created_at=datetime.datetime.now())]


@router.post("/uploads", summary="Upload a new file for sentiment check", response_model=UploadWithEntries)
async def upload_file(file: UploadFile,
                      session: Session = Depends(get_session),
                      user: User = Depends(get_user)) -> Upload:
    b = await file.read()
    df = pd.read_excel(io.BytesIO(b), header=None, index_col=None)
    df.columns = ['text']

    upload = Upload(name=file.filename, created_by=user.id, status=UploadStatus.PENDING)
    session.add(upload)
    session.commit()
    session.refresh(upload)

    entries = []
    p = 0
    for i, row in df.iterrows():
        entry = UploadEntry(upload_id=upload.id, text=row['text'], sentiment=None, id=p)
        session.add(entry)
        entries.append(entry)
        p += 1

    session.commit()
    session.refresh(upload)
    await process_upload.kiq(upload_id=upload.id)

    return upload


# @router.get("/uploads/{id}", summary="Get a specific upload")
# def get_upload_by_id(id: int) -> UploadFull:
#     return UploadFull(id=id, name="test.xlsx", created_at=datetime.datetime.now(), entries=[])
#

@router.get("/uploads/{id}/share", summary="Get a list of users that have access to the upload")
def get_upload_share(upload_id: int) -> list[str]:
    return ["user1", "user2", "user3"]


@router.post("/uploads/{id}/share", summary="Share the upload with a user")
def share_upload(upload_id: int, user: str) -> str:
    return f"Upload {upload_id} shared with {user}"

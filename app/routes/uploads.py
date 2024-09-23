import io
from enum import StrEnum

import docx
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, delete, select

from app.broker import process_upload
from app.dependencies import get_session, get_upload_from_path, get_user
from app.models.upload import (
    Upload,
    UploadEntry,
    UploadPublic,
    UploadStatus,
    UploadWithEntries,
)
from app.models.upload_access import (
    AccessRecipientType,
    UploadAccess,
    UploadAccessRecipientResponse,
    UploadAccessRequest,
)
from app.models.user import User
from app.services.sentiment_predict import SentimentPredict

router = APIRouter(tags=["Uploads"])

predict = SentimentPredict()


class DownloadFileType(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"


@router.get("/uploads", summary="Get all uploads")
def get_upload(
    session: Session = Depends(get_session), user: User = Depends(get_user)
) -> list[UploadPublic]:
    res = list(
        session.exec(select(Upload).where(Upload.created_by_user_id == user.id)).all()
    )

    shared_uploads = list(
        session.exec(
            select(Upload)
            .join(UploadAccess)
            .where(UploadAccess.recipient_id == user.id)
        ).all()
    )

    shared_org_uploads = []
    if user.organization:
        shared_org_uploads = session.exec(
            select(Upload)
            .join(UploadAccess)
            .where(UploadAccess.recipient_id == user.organization)
            .where(Upload.created_by_user_id != user.id)
        ).all()

    return list(res) + list(shared_uploads) + list(shared_org_uploads)


@router.get("/uploads/{upload_id}", summary="Get a specific upload")
def get_upload_by_id(
    upload: Upload = Depends(get_upload_from_path),
) -> UploadWithEntries:
    return upload


@router.get("/uploads/{upload_id}/download", summary="Download a specific upload")
def download_upload_by_id(
    type: DownloadFileType = DownloadFileType.XLSX,
    upload: Upload = Depends(get_upload_from_path),
):
    output = io.BytesIO()
    df = pd.DataFrame(
        [
            {"id": entry.id, "text": entry.text, "sentiment": entry.sentiment.value}
            for entry in upload.entries
        ]
    )
    if type == DownloadFileType.CSV:
        df.to_csv(output, index=False)
    else:
        df.to_excel(output, index=False)

    output.seek(0)
    return StreamingResponse(
        output,
        headers={
            "Content-Disposition": f"attachment; filename={upload.name.replace('.', '-')}-results.{type}"
        },
    )


@router.delete(
    "/uploads/{upload_id}", summary="Delete a specific upload", status_code=204
)
def delete_upload_by_id(
    session: Session = Depends(get_session),
    upload: Upload = Depends(get_upload_from_path),
):
    session.exec(delete(Upload).where(Upload.id == upload.id))
    session.exec(delete(UploadEntry).where(UploadEntry.upload_id == upload.id))
    session.commit()


@router.post(
    "/uploads",
    summary="Upload a new file for sentiment check",
    response_model=UploadWithEntries,
)
async def upload_file(
    file: UploadFile,
    session: Session = Depends(get_session),
    user: User = Depends(get_user),
) -> Upload:
    if file.content_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        b = await file.read()
        df = pd.read_excel(io.BytesIO(b), header=None, index_col=None)
        df.columns = ["text"]

        upload = Upload(
            name=file.filename, created_by_user_id=user.id, status=UploadStatus.PENDING
        )
        session.add(upload)
        session.commit()
        session.refresh(upload)

        entries = []
        for i, row in df.iterrows():
            entry = UploadEntry(upload_id=upload.id, text=row["text"], sentiment=None, id=i)
            session.add(entry)
            entries.append(entry)
        session.commit()
        session.refresh(upload)

        await process_upload.kiq(upload_id=upload.id)
        return upload
    elif file.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        b = await file.read()
        doc = docx.Document(io.BytesIO(b))
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

        # Create a new Upload record
        upload = Upload(
            name=file.filename, created_by_user_id=user.id, status=UploadStatus.PENDING
        )
        session.add(upload)
        session.commit()
        session.refresh(upload)

        # Process the Word file content as one single entry
        entry = UploadEntry(upload_id=upload.id, text=full_text, sentiment=None, id=1)
        session.add(entry)
        session.commit()
        session.refresh(upload)

        # Queue processing task
        await process_upload.kiq(upload_id=upload.id)
        return upload
    elif file.content_type in ["text/plain"]:
        b = await file.read()
        text = b.decode("utf-8")

        upload = Upload(
            name=file.filename, created_by_user_id=user.id, status=UploadStatus.PENDING
        )
        session.add(upload)
        session.commit()
        session.refresh(upload)

        entry = UploadEntry(upload_id=upload.id, text=text, sentiment=None, id=1)
        session.add(entry)
        session.commit()
        session.refresh(upload)

        await process_upload.kiq(upload_id=upload.id)
        return upload
    else:
        raise HTTPException(status_code=400, detail="File type not supported")


@router.get(
    "/uploads/{upload_id}/share",
    summary="Get a list of users that have access to the upload",
)
def get_upload_share(
    session: Session = Depends(get_session),
    upload: Upload = Depends(get_upload_from_path),
) -> list[UploadAccessRecipientResponse]:
    
    res: list[UploadAccessRecipientResponse] = []

    users = session.exec(
        select(UploadAccess)
        .where(UploadAccess.upload_id == upload.id)
        .where(UploadAccess.recipient_type == AccessRecipientType.USER)
    ).all()

    for user in users:
        user_in_db = session.exec(select(User).where(User.id == user.recipient_id)).first()
        res.append(
            UploadAccessRecipientResponse(
                recipient_id=user.recipient_id,
                recipient_type=user.recipient_type,
                name=user_in_db.email,
            )
        )

    orgs = session.exec(
        select(UploadAccess)
        .where(UploadAccess.upload_id == upload.id)
        .where(UploadAccess.recipient_type == AccessRecipientType.ORG)
    ).all()

    for org in orgs:
        res.append(
            UploadAccessRecipientResponse(
                recipient_id=org.recipient_id,
                recipient_type=org.recipient_type,
                name=org.recipient_id,
            )
        )

    return res


@router.post("/uploads/{upload_id}/share", summary="Share the upload with a user")
def share_upload(
    request: UploadAccessRequest,
    user: User = Depends(get_user),
    session: Session = Depends(get_session),
    upload: Upload = Depends(get_upload_from_path),
):
    res = session.exec(
        select(UploadAccess)
        .where(UploadAccess.upload_id == upload.id)
        .where(UploadAccess.recipient_id == request.recipient_id)
        .where(UploadAccess.recipient_type == request.recipient_type)
    ).first()

    if res:
        raise HTTPException(status_code=400, detail="Already shared with this user")

    if request.recipient_type == AccessRecipientType.USER:
        share_to_user = session.exec(
            select(User).where(User.email == request.recipient_id)
        ).first()

        if not share_to_user:
            raise HTTPException(status_code=404, detail="User with such email not found")
    
        if share_to_user.id == user.id:
            raise HTTPException(status_code=400, detail="Cannot share with yourself")
        
        access = UploadAccess(
            upload_id=upload.id,
            recipient_id=share_to_user.id,
            recipient_type=request.recipient_type,
        )

        session.add(access)
        session.commit()
        return access

    else:
        recipient = session.exec(
            select(User).where(User.organization == request.recipient_id)
        ).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Org not found")

        access = UploadAccess(
            upload_id=upload.id,
            recipient_id=request.recipient_id,
            recipient_type=request.recipient_type,
        )
        session.add(access)
        session.commit()
        return access


@router.delete(
    "/uploads/{upload_id}/share", summary="Remove a user from the upload share"
)
def unshare_upload(
    request: UploadAccessRequest,
    user: User = Depends(get_user),
    session: Session = Depends(get_session),
    upload: Upload = Depends(get_upload_from_path),
):
    if request.recipient_type == AccessRecipientType.USER:
        if upload.created_by_user_id != user.id and request.recipient_id != user.id:
            raise HTTPException(status_code=403, detail="You can only remove yourself as you are not an owner of upload")
    elif request.recipient_type == AccessRecipientType.ORG:
        if upload.created_by_user_id != user.id:
            raise HTTPException(status_code=403, detail="Only owner can remove organization from share")

    session.exec(
        delete(UploadAccess)
        .where(UploadAccess.upload_id == upload.id)
        .where(UploadAccess.recipient_id == request.recipient_id)
        .where(UploadAccess.recipient_type == request.recipient_type)
    )
    session.commit()

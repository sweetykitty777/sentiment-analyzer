import logging

import taskiq_fastapi
from sqlmodel import Session, select
from taskiq import InMemoryBroker

from app.dependencies import engine
from app.models.upload import Upload, UploadEntry, UploadStatus, UploadWithEntries
from app.services.sentiment_predict import SentimentPredict

broker = InMemoryBroker()

logger = logging.getLogger(__name__)
predictor = SentimentPredict()


taskiq_fastapi.init(broker, "app.main:app")

@broker.task
async def process_upload(upload_id: str):
    with Session(engine) as session:
        entries = session.exec(
            select(UploadEntry).where(UploadEntry.upload_id == upload_id)
        ).all()

        for entry in entries:
            entry.sentiment = predictor.predict(entry.text)

        upload = session.get(Upload, upload_id)
        upload.status = UploadStatus.READY
        session.commit()

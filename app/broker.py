from sqlmodel import Session, select
from taskiq_aio_pika import AioPikaBroker

from app.dependencies import engine
from app.models.upload import Upload, UploadEntry, UploadStatus
from app.services.sentiment_predict import SentimentPredict
from app.settings import settings

broker = AioPikaBroker(
    settings.rabbit_mq_url,
    exchange_name=settings.rabbit_queue,
    queue_name=settings.rabbit_queue,
)


predictor = SentimentPredict()


@broker.task
async def process_upload(upload_id: str):
    print(f"Processing upload {upload_id}")

    with Session(engine) as session:
        entries = session.exec(
            select(UploadEntry).where(UploadEntry.upload_id == upload_id)
        ).all()

        for entry in entries:
            entry.sentiment = predictor.predict(entry.text)

        upload = session.get(Upload, upload_id)
        upload.status = UploadStatus.READY
        session.commit()
        print(f"Upload {upload_id} processed")

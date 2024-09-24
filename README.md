# Sentiment Analyzer Backend

Built with:

- FastAPI
- Torch & Transformers
- SQLModel
- Taskiq
- RabbitMQ

## Variables

```bash
RABBIT_MQ_URL=""
RABBIT_MQ_QUEUE=""
DATABASE_URL=""
```

## Run Tests

`ENVIRONMENT="pytest" RABBIT_MQ_URL=<> RABBIT_MQ_QUEUE=<> pytest app/tests/test_app.py"`

## Build docker image

`docker build -t sentiment-analyzer-backend .`

## Run localy 

RabbitMQ has to be running.

Export envs and run `fastapi dev`

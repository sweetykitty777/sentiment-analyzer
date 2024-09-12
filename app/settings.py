import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///database.db")
    oidc_base_url: str = "https://lemur-15.cloud-iam.com/auth/realms/sentiment-analyzer"
    rabbit_mq_url: str = os.environ["RABBIT_MQ_URL"]
    rabbit_queue: str = os.environ["RABBIT_QUEUE"]
    
settings = Settings()

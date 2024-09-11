import os 
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
    oidc_base_url: str = "https://lemur-15.cloud-iam.com/auth/realms/sentiment-analyzer"


settings = Settings()

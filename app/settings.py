class Settings:
    database_url: str = "sqlite:///database.db"
    oidc_base_url: str = "https://lemur-15.cloud-iam.com/auth/realms/sentiment-analyzer"


settings = Settings()

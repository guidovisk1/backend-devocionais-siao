from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./devocional.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    first_admin_email: str = "admin@suaigreja.com"
    first_admin_password: str = "senha123"
    first_admin_name: str = "Administrador"

    class Config:
        env_file = ".env"


settings = Settings()

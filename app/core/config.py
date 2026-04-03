from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI CRUD with Docker Postgres"
    debug: bool = True

    # DB settings – match docker run values
    postgres_user: str = "myuser"
    postgres_password: str = "mypassword"
    postgres_server: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "mycruddb"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_server}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
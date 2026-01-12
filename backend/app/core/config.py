import logging
import os
from functools import lru_cache
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

app_env = os.getenv("APP_ENV", default="dev")
env_files = [".env", f".env.{app_env}"]

is_test = os.getenv("IS_TEST", default="False")
if is_test == "True":
    logging.warning(f"[TEST MODE] IS_TEST = {is_test}")


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    jwt_secret_key: str = Field("mysecrettoken", env="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire: int = Field(10, env="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire: int = Field(60, env="REFRESH_TOKEN_EXPIRE")

    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field("root", env="POSTGRES_USER")
    postgres_password: str = Field("root", env="POSTGRES_PASSWORD")
    postgres_db: str = Field("db", env="POSTGRES_DB")
    database_url_override: str | None = Field(default=None, env="DATABASE_URL")

    langchain_api_key: str = Field(default="", env="LANGCHAIN_API_KEY")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", env="LANGCHAIN_ENDPOINT"
    )

    @computed_field
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            if self.database_url_override.startswith("postgresql://"):
                return self.database_url_override.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )
            return self.database_url_override
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = SettingsConfigDict(
        env_file=[
            f"{os.path.dirname(os.path.abspath(__file__))}/{env}" for env in env_files
        ],
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

from pydantic import Field, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # This will ignore extra env vars like PYTHONPATH
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = Field("HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60)

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = Field(5432)
    POSTGRES_DB: str

    @computed_field
    @property
    def asyncpg_url(self) -> MultiHostUrl:
        """
        This is a computed field that generates a PostgresDsn URL for asyncpg.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL for asyncpg.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def postgres_url(self) -> MultiHostUrl:
        """
        This is a computed field that generates a PostgresDsn URL

        Returns:
            PostgresDsn: The constructed PostgresDsn URL.
        """
        return MultiHostUrl.build(
            scheme="postgres",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings() # type: ignore

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)
from sqlalchemy import URL


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)


class ProjectSettings(Settings):
    name: str = "MyProject"
    version: str = "1.0"
    description: str = "Project Description"


class UvicornSettings(Settings):
    port: int = 8000
    host: str = "127.0.0.1"
    workers: int = 1


class URLSettings(Settings):
    driverName: Optional[str] = None
    userName: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None

    @property
    def url(self) -> str:
        return URL.create(
            drivername=self.driverName,
            username=self.userName,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


class DatabaseSettings(Settings):
    echo: bool = False
    poolSize: int = 10
    maxOverflow: int = 5
    poolTimeout: int = 30

    URL: URLSettings = URLSettings()


class AuthJWTSettings(Settings):
    private_key_path: Path = "./api/auth/jwt-private.key"
    public_key_path: Path = "./api/auth/jwt-public.key"
    algorithm: str = "RS256"


class AppSettings(BaseSettings):
    development: bool = False

    project: ProjectSettings = ProjectSettings()
    uvicorn: UvicornSettings = UvicornSettings()
    database: DatabaseSettings = DatabaseSettings()
    jwt: AuthJWTSettings = AuthJWTSettings()

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (
            DotEnvSettingsSource(
                settings_cls,
                [
                    "./src/example.env",
                    "./src/.env",
                ],
                env_file_encoding="utf-8",
                env_nested_delimiter="_",
                env_ignore_empty=True,
            ),
            YamlConfigSettingsSource(settings_cls, "./src/config.yaml"),
            TomlConfigSettingsSource(settings_cls, "./src/config.toml"),
        )


config = AppSettings()

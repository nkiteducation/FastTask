from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
    DotEnvSettingsSource,
)
from pydantic import BaseModel, Field, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)


class ProjectSettings(Settings):
    name: str = Field(default="FastTask")
    version: str = Field(default="1.0.0")
    description: str = Field(
        default="""The project is an API for task management
        (To-Do List) using FastAPI, SQLAlchemy and asynchronous
        database. It includes functionality for creating, updating,
        deleting and filtering tasks with support for users and roles."""
    )


class UvicornSettings(Settings):
    port: int = Field(default=8000)
    host: str = Field(default="127.0.0.1")
    workers: int = Field(default=1)


class Settings(BaseSettings):
    development: bool = Field(default=False)
    project: ProjectSettings = ProjectSettings()
    uvicorn: UvicornSettings = UvicornSettings()

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (
            DotEnvSettingsSource(
                settings_cls,
                ["./src/example.env", "./src/.env"],
                env_file_encoding="utf-8",
                env_nested_delimiter="_",
            ),
            YamlConfigSettingsSource(settings_cls, "./src/config.yaml"),
            TomlConfigSettingsSource(settings_cls, "./src/config.toml"),
        )


config = Settings()
print(config.project.name)

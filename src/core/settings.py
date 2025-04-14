from pathlib import Path
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
    name: str = "MyProject"
    version: str = "1.0"
    description: str = "Project Description"

class UvicornSettings(Settings):
    port: int = 8000
    host: str = "127.0.0.1"
    workers: int = 1

class AppSettings(BaseSettings):
    development: bool = False
    
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
                [
                    "./src/example.env",
                    "./src/.env",
                ],
                env_file_encoding="utf-8",
                env_nested_delimiter="_",
            ),
            YamlConfigSettingsSource(settings_cls, "./src/config.yaml"),
            TomlConfigSettingsSource(settings_cls, "./src/config.toml"),
        )
        
config = AppSettings()
print(config)

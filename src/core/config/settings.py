from zoneinfo import ZoneInfo

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, YamlConfigSettingsSource

from core.config.application import ApplicationConfig
from core.config.database import DatabaseConfig
from core.config.external_service import ExternalServiceConfig
from core.config.google_cloud import GoogleCloudConfig
from core.config.loader import get_config_yaml_filepath, get_environment
from core.config.logging import LoggingConfig
from core.config.sentry import SentryConfig
from core.types.environment import ApplicationEnvironment

ENVIRONMENT: ApplicationEnvironment = get_environment()


class Settings(BaseSettings):
    application: ApplicationConfig = Field(default=ApplicationConfig())
    database: DatabaseConfig = Field(default=DatabaseConfig())
    external_service: ExternalServiceConfig = Field(
        alias="externalService",
        default=ExternalServiceConfig(),
    )
    sentry: SentryConfig = Field(default=SentryConfig())
    logging: LoggingConfig = Field(default=LoggingConfig())
    google_cloud: GoogleCloudConfig = Field(
        alias="googleCloud",
        default=GoogleCloudConfig(),
    )

    # Timezone
    timezone: str = Field(default="Asia/Jakarta")
    timezone_info: ZoneInfo | None = Field(init=False, default=None)

    @model_validator(mode="after")
    def set_timezone_info(self):
        self.timezone_info = ZoneInfo(self.timezone)
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        config_yaml_filepath = get_config_yaml_filepath(ENVIRONMENT)
        yaml_source = YamlConfigSettingsSource(
            settings_cls,
            yaml_file=config_yaml_filepath,
        )

        return (
            init_settings,
            yaml_source,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()

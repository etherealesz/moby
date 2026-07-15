from pydantic import BaseModel, Field

from core.logger.setup import LoggingLevel


class LoggingConfig(BaseModel):
    level: LoggingLevel = Field(default="info")

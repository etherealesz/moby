from pydantic.fields import Field
from pydantic.main import BaseModel


class SentryConfig(BaseModel):
    dsn: str = Field(default="")

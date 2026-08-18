from pydantic.fields import Field
from pydantic.main import BaseModel


class ServiceProperties(BaseModel):
    base_url: str = Field(alias="baseUrl", default="http://localhost:8000")


class ExternalServiceConfig(BaseModel):
    pass

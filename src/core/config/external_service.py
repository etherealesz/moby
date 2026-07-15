from pydantic.fields import Field
from pydantic.main import BaseModel


class ServiceProperties(BaseModel):
    base_url: str = Field(alias="baseUrl", default="http://localhost:5000")


class ExternalServiceConfig(BaseModel):
    izmo_auth: ServiceProperties = Field(alias="izmoAuth", default=ServiceProperties())

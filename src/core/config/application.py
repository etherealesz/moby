from pydantic.fields import Field
from pydantic.main import BaseModel


class ApplicationConfig(BaseModel):
    name: str = Field(default="MyApp")
    version: str = Field(default="0.0.1")
    debug: bool = Field(default=False)

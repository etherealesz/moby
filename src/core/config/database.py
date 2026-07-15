from pydantic.fields import Field
from pydantic.main import BaseModel


class SQLDatabaseProperties(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="postgres")
    password: str = Field(default="")
    name: str = Field(default="database")


class DatabaseConfig(BaseModel):
    master: SQLDatabaseProperties = Field(default=SQLDatabaseProperties())

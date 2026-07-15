from pydantic import BaseModel, Field


class GoogleCloudBucket(BaseModel):
    master: str = Field(default="izmo-development")


class GoogleCloudConfig(BaseModel):
    bucket: GoogleCloudBucket = Field(default=GoogleCloudBucket())

from pydantic import BaseModel, field_validator


class LocalStorageConfig(BaseModel):
    base_dir: str


class S3StorageConfig(BaseModel):
    bucket_name: str
    region: str
    prefix: str | None = None

    @field_validator("prefix", mode="before")
    @classmethod
    def normalize_prefix(cls, v: str | None) -> str:
        if v is None:
            return ""
        return v

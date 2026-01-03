from pydantic import BaseModel, field_validator


class LocalStorageConfig(BaseModel):
    base_dir: str


class S3StorageConfig(BaseModel):
    bucket_name: str
    region: str
    prefix: str | None = None

    @field_validator("prefix", mode="after")
    def validate_absolute_path(self) -> str:
        if not self.prefix:
            return ""
        return self.prefix.strip()

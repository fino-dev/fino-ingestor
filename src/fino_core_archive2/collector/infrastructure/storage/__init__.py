"""Storage infrastructure implementations."""

from typing import Union

from fino_core.domain.storage import (
    LocalStorageConfig,
    S3StorageConfig,
    Storage,
    StorageConfig,
)
from fino_core.domain.storage_type import StorageType

from .local_storage import LocalStorage
from .s3_storage import S3Storage


def _convert_storage_config_input(input_config: object) -> StorageConfig:
    # StorageConfigInputの属性にアクセス
    storage_type = getattr(input_config, "type", None)
    path = getattr(input_config, "path", None)
    bucket = getattr(input_config, "bucket", None)
    api_key = getattr(input_config, "api_key", None)
    region = getattr(input_config, "region", None)

    if storage_type == StorageType.LOCAL:
        return LocalStorageConfig(base_path=path or "")
    elif storage_type == StorageType.S3:
        if not bucket or not api_key or not region:
            raise ValueError("S3 storage requires bucket, api_key, and region")
        return S3StorageConfig(
            bucket=bucket,
            api_key=api_key,
            region=region,
        )
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


def create_storage(config: Union[StorageConfig, object]) -> Storage:
    if not isinstance(config, (LocalStorageConfig, S3StorageConfig)) and hasattr(config, "type"):
        config = _convert_storage_config_input(config)

    if isinstance(config, LocalStorageConfig):
        return LocalStorage(config.base_path)

    if isinstance(config, S3StorageConfig):
        return S3Storage(
            bucket=config.bucket,
            api_key=config.api_key,
            region=config.region,
        )

    raise ValueError(f"Unknown StorageConfig type: {type(config)}")


__all__ = ["LocalStorage", "S3Storage", "create_storage"]

"""Factory for creating storage implementations.

This factory handles dependency injection for storage.
It creates concrete implementations (LocalStorage, S3Storage, etc.) based on configuration.
"""

from typing import Any

from fino_core.collector.application.port.storage import Storage
from fino_core.collector.infrastructure.storage.local_storage import LocalStorage
from fino_core.collector.infrastructure.storage.s3_storage import S3Storage


def create_local_storage(base_path: str) -> LocalStorage:
    """Create a local file system storage instance.

    Args:
        base_path: Base path for storing files

    Returns:
        LocalStorage instance
    """
    return LocalStorage(base_path=base_path)


def create_s3_storage(bucket: str, api_key: str, region: str) -> S3Storage:
    """Create an S3 storage instance.

    Args:
        bucket: S3 bucket name
        api_key: AWS access key
        region: AWS region

    Returns:
        S3Storage instance
    """
    return S3Storage(bucket=bucket, api_key=api_key, region=region)


def create_storage(config: dict[str, Any] | Any) -> Storage:
    """Create a storage instance based on configuration.

    Args:
        config: Storage configuration (dict or object with type attribute)

    Returns:
        Storage implementation instance

    Raises:
        ValueError: If storage type is not supported or required parameters are missing
    """
    # Handle dict or object with attributes
    if isinstance(config, dict):
        storage_type = config.get("type")
        if storage_type == "local":
            path = config.get("path", "./data")
            return create_local_storage(path)
        elif storage_type == "s3":
            bucket = config.get("bucket")
            api_key = config.get("api_key")
            region = config.get("region")
            if not all([bucket, api_key, region]):
                raise ValueError("S3 storage requires bucket, api_key, and region")
            return create_s3_storage(bucket, api_key, region)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    else:
        # Handle object with attributes
        storage_type = getattr(config, "type", None)
        if storage_type == "local" or storage_type is None:
            path = getattr(config, "path", "./data")
            return create_local_storage(path)
        elif storage_type == "s3":
            bucket = getattr(config, "bucket", None)
            api_key = getattr(config, "api_key", None)
            region = getattr(config, "region", None)
            if not all([bucket, api_key, region]):
                raise ValueError("S3 storage requires bucket, api_key, and region")
            return create_s3_storage(bucket, api_key, region)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")


from fino_core.infrastructure.adapter.storage.local import LocalStorage
from fino_core.infrastructure.adapter.storage.s3 import S3Storage
from fino_core.interface.port.document_storage import StoragePort
from fino_core.public.config.storage import LocalStorageConfig, S3StorageConfig


def create_storage(config: LocalStorageConfig | S3StorageConfig) -> StoragePort:
    if isinstance(config, LocalStorageConfig):
        return LocalStorage(config)
    else:
        return S3Storage(config)

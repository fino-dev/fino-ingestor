from fino_ingestor.infrastructure.adapter.storage.local import LocalStorage
from fino_ingestor.infrastructure.adapter.storage.s3 import S3Storage
from fino_ingestor.interface.config.storage import LocalStorageConfig, S3StorageConfig
from fino_ingestor.interface.port.storage import StoragePort


def create_storage(config: LocalStorageConfig | S3StorageConfig) -> StoragePort:
    if isinstance(config, LocalStorageConfig):
        return LocalStorage(config=config)
    else:
        return S3Storage(config=config)

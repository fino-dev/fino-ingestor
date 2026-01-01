# """Tests for storage factory."""

# import pytest
# from fino_core.factory.storage import create_storage
# from fino_core.model.storage_type import StorageType


# class TestCreateStorage:
#     """create_storage関数のテスト"""

#     def test_create_local_storage(self, local_storage_config):
#         """LocalStorageConfigからLocalStorageインスタンスを生成"""
#         storage = create_storage(local_storage_config)
#         assert storage is not None
#         # LocalStorageのインスタンスであることを確認
#         from fino_core.infrastructure.storage.local_storage import LocalStorage

#         assert isinstance(storage, LocalStorage)

#     def test_create_s3_storage(self, s3_storage_config):
#         """S3StorageConfigからS3Storageインスタンスを生成"""
#         storage = create_storage(s3_storage_config)
#         assert storage is not None
#         # S3Storageのインスタンスであることを確認
#         from fino_core.infrastructure.storage.s3_storage import S3Storage

#         assert isinstance(storage, S3Storage)

#     def test_create_storage_with_invalid_config(self):
#         """無効なStorageConfigでエラーが発生することを確認"""
#         # StorageConfigの基底クラスを直接使用（抽象クラス）
#         from fino_core.model.storage import StorageConfig

#         class InvalidConfig(StorageConfig):
#             pass

#         with pytest.raises(ValueError, match="Unknown StorageConfig type"):
#             create_storage(InvalidConfig())

#     def test_create_storage_with_storage_config_input(self):
#         """StorageConfigInputからストレージインスタンスを生成"""

#         # StorageConfigInputのモック
#         class StorageConfigInput:
#             type = StorageType.LOCAL
#             path = "/tmp/test"
#             bucket = None
#             api_key = None
#             region = None

#         input_config = StorageConfigInput()
#         storage = create_storage(input_config)
#         assert storage is not None
#         from fino_core.infrastructure.storage.local_storage import LocalStorage

#         assert isinstance(storage, LocalStorage)

#     def test_create_storage_with_s3_storage_config_input(self):
#         """S3StorageConfigInputからストレージインスタンスを生成"""

#         # StorageConfigInputのモック
#         class StorageConfigInput:
#             type = StorageType.S3
#             path = None
#             bucket = "test-bucket"
#             api_key = "test-key"
#             region = "ap-northeast-1"

#         input_config = StorageConfigInput()
#         storage = create_storage(input_config)
#         assert storage is not None
#         from fino_core.infrastructure.storage.s3_storage import S3Storage

#         assert isinstance(storage, S3Storage)

#     def test_create_storage_with_incomplete_s3_config(self):
#         """不完全なS3設定でエラーが発生することを確認"""

#         class StorageConfigInput:
#             type = StorageType.S3
#             path = None
#             bucket = None  # 欠落
#             api_key = "test-key"
#             region = "ap-northeast-1"

#         input_config = StorageConfigInput()
#         with pytest.raises(ValueError, match="S3 storage requires"):
#             create_storage(input_config)

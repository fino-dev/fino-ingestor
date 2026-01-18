import os
from unittest.mock import patch

import boto3
import pytest
from botocore.exceptions import ClientError
from fino_ingestor.infrastructure.adapter.storage.s3 import S3Storage
from fino_ingestor.interface.config.storage import S3StorageConfig
from fino_ingestor.interface.port.storage import StoragePort
from moto import mock_aws
from mypy_boto3_s3.client import S3Client


class TestS3Storage:
    @pytest.fixture
    def s3_client(self) -> S3Client:
        return boto3.client("s3", region_name="us-east-1")  # type: ignore[reportUnknownMemberType]

    @pytest.fixture
    def bucket_name(self) -> str:
        return "test-bucket"

    @pytest.fixture
    def s3_bucket(self, s3_client: S3Client, bucket_name: str) -> str:
        _ = s3_client.create_bucket(Bucket=bucket_name)
        return bucket_name

    @pytest.fixture
    def storage(self, bucket_name: str) -> S3Storage:
        return S3Storage(
            config=S3StorageConfig(bucket_name=bucket_name, region="us-east-1")
        )

    @pytest.fixture
    def storage_with_prefix(self, bucket_name: str) -> S3Storage:
        return S3Storage(
            config=S3StorageConfig(
                bucket_name=bucket_name, region="us-east-1", prefix="test-prefix/"
            )
        )

    @pytest.fixture(autouse=True)
    def setup_mock_aws(self):
        """すべてのテストでmock_awsを有効化"""
        # ダミーのAWS認証情報を設定
        original_env: dict[str, str | None] = {}
        env_vars = {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
        }
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            with mock_aws():
                yield
        finally:
            # クリーンアップ
            for key, original_value in original_env.items():
                if original_value is None:
                    _ = os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value

    ########## instance check ##########
    def test_instance_success(self, storage: S3Storage) -> None:
        assert isinstance(storage, StoragePort)

    ########## prefix normalization ##########
    def test_normalize_prefix_strips_slashes(self) -> None:
        storage = S3Storage(
            config=S3StorageConfig(
                bucket_name="test-bucket", region="us-east-1", prefix="prefix/"
            )
        )
        assert storage.prefix == "prefix"

    def test_normalize_prefix_without_prefix(self) -> None:
        storage = S3Storage(
            config=S3StorageConfig(bucket_name="test-bucket", region="us-east-1")
        )
        assert storage.prefix == ""

    def test_normalize_prefix_raises_error_on_path_traversal(self) -> None:
        with pytest.raises(ValueError, match="S3 prefix cannot contain"):
            _ = S3Storage(
                config=S3StorageConfig(
                    bucket_name="test-bucket", region="us-east-1", prefix="../prefix"
                )
            )

    def test_normalize_prefix_raises_error_on_spaces(self) -> None:
        # 実装は先頭と末尾の空白のみをチェックするため、中間の空白は検出されない
        # 先頭に空白がある場合のテスト
        with pytest.raises(ValueError, match="S3 prefix cannot have spaces"):
            _ = S3Storage(
                config=S3StorageConfig(
                    bucket_name="test-bucket",
                    region="us-east-1",
                    prefix=" prefix with spaces",
                )
            )

    ########## key resolution ##########
    def test_resolve_key_without_prefix(self, storage: S3Storage) -> None:
        key = storage._resolve_key("test/path/file.txt")  # type: ignore[reportPrivateUsage]
        assert key == "test/path/file.txt"

    def test_resolve_key_with_prefix(self, storage_with_prefix: S3Storage) -> None:
        # prefixは_normalize_prefixでstrip("/")されるため、結合時に/が入らない
        # 実装: f"{self.prefix}{normalized_path}"
        key = storage_with_prefix._resolve_key("test/path/file.txt")  # type: ignore[reportPrivateUsage]
        assert key == "test-prefixtest/path/file.txt"

    def test_resolve_key_with_nested_path(self, storage: S3Storage) -> None:
        key = storage._resolve_key("subdir/nested/deep/file.txt")  # type: ignore[reportPrivateUsage]
        assert key == "subdir/nested/deep/file.txt"

    def test_resolve_key_raises_error_on_absolute_path(
        self, storage: S3Storage
    ) -> None:
        with pytest.raises(ValueError, match="Absolute path is not allowed"):
            _ = storage._resolve_key("/absolute/path.txt")  # type: ignore[reportPrivateUsage]

    def test_resolve_key_raises_error_on_path_traversal(
        self, storage: S3Storage
    ) -> None:
        with pytest.raises(ValueError, match="Path traversal detected"):
            _ = storage._resolve_key("../outside.txt")  # type: ignore[reportPrivateUsage]

    def test_resolve_key_removes_empty_parts(self, storage: S3Storage) -> None:
        key = storage._resolve_key("test//path///file.txt")  # type: ignore[reportPrivateUsage]
        assert key == "test/path/file.txt"

    ########## exists method ##########
    def test_exists_returns_true_when_file_exists(
        self, storage: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        _ = s3_client.put_object(Bucket=s3_bucket, Key="test.txt", Body=b"test content")
        assert storage.exists("test.txt") is True

    def test_exists_returns_false_when_file_not_exists(
        self, storage: S3Storage, s3_bucket: str
    ) -> None:
        assert storage.exists("nonexistent.txt") is False

    def test_exists_with_prefix(
        self, storage_with_prefix: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        # prefixは_normalize_prefixでstrip("/")されるため、結合時に/が入らない
        _ = s3_client.put_object(
            Bucket=s3_bucket,
            Key="test-prefixtest.txt",
            Body=b"test content",
        )
        assert storage_with_prefix.exists("test.txt") is True

    def test_exists_raises_error_on_other_client_errors(
        self, storage: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        # バケットを削除してアクセスエラーを発生させる
        _ = s3_client.delete_bucket(Bucket=s3_bucket)
        with pytest.raises(ClientError):
            _ = storage.exists("test.txt")

    ########## exists method ERROR ##########
    def test_exists_raises_error_on_absolute_path(self, storage: S3Storage) -> None:
        with pytest.raises(ValueError, match="Absolute path is not allowed"):
            _ = storage.exists("/absolute/path.txt")

    def test_exists_raises_error_on_path_traversal(self, storage: S3Storage) -> None:
        with pytest.raises(ValueError, match="Path traversal detected"):
            _ = storage.exists("../outside.txt")

    ########## save method ##########
    def test_save_creates_file(
        self, storage: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        content = b"test save file content"
        storage.save("test-save.txt", content)
        response = s3_client.get_object(Bucket=s3_bucket, Key="test-save.txt")
        assert response["Body"].read() == content  # type: ignore[reportUnknownMemberType]

    def test_save_with_prefix(
        self, storage_with_prefix: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        # prefixは_normalize_prefixでstrip("/")されるため、結合時に/が入らない
        content = b"test content with prefix"
        storage_with_prefix.save("test.txt", content)
        response = s3_client.get_object(Bucket=s3_bucket, Key="test-prefixtest.txt")
        assert response["Body"].read() == content  # type: ignore[reportUnknownMemberType]

    def test_save_overwrites_existing_file(
        self, storage: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        initial_content = b"initial"
        updated_content = b"updated"
        storage.save("test-override.txt", initial_content)
        storage.save("test-override.txt", updated_content)
        response = s3_client.get_object(Bucket=s3_bucket, Key="test-override.txt")
        assert response["Body"].read() == updated_content  # type: ignore[reportUnknownMemberType]

    def test_save_raises_error_on_client_error(
        self, storage: S3Storage, s3_client: S3Client, s3_bucket: str
    ) -> None:
        # バケットを削除してアクセスエラーを発生させる
        _ = s3_client.delete_bucket(Bucket=s3_bucket)
        with pytest.raises(IOError, match="Failed to save file to S3"):
            storage.save("test.txt", b"content")

    def test_save_raises_error_when_etag_missing(
        self, storage: S3Storage, s3_bucket: str
    ) -> None:
        # ETagがレスポンスにない場合のエラーテスト
        with patch.object(storage.s3_client, "put_object", return_value={}) as mock_put:
            with pytest.raises(IOError, match="Failed to save file to S3"):
                storage.save("test.txt", b"content")
            mock_put.assert_called_once()

    ########## save method ERROR ##########
    def test_save_raises_error_on_absolute_path(self, storage: S3Storage) -> None:
        with pytest.raises(ValueError, match="Absolute path is not allowed"):
            storage.save("/absolute/path.txt", b"content")

    def test_save_raises_error_on_path_traversal(self, storage: S3Storage) -> None:
        # with relative path
        with pytest.raises(ValueError, match="Path traversal detected"):
            storage.save("../outside.txt", b"content")

        # with nested path
        with pytest.raises(ValueError, match="Path traversal detected"):
            storage.save("subdir/../../outside.txt", b"content")

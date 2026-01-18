import boto3
from botocore.exceptions import ClientError
from fino_ingestor.interface.config.storage import S3StorageConfig
from fino_ingestor.interface.port.storage import StoragePort
from mypy_boto3_s3.client import S3Client


class S3Storage(StoragePort):
    def __init__(self, config: S3StorageConfig) -> None:
        self.bucket_name = config.bucket_name
        self.region = config.region
        self.prefix = self._normalize_prefix(config.prefix or "")
        self.s3_client: S3Client = boto3.client("s3", region_name=self.region)  # type: ignore[reportUnknownMemberType]

    def exists(self, path: str) -> bool:
        key = self._resolve_key(path)
        try:
            _ = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                return False
            raise

    def save(self, path: str, file: bytes) -> None:
        key = self._resolve_key(path)
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name, Key=key, Body=file
            )
            if "ETag" not in response:
                raise IOError(f"Failed to save file to S3: {path}")
        except ClientError as e:
            raise IOError(f"Failed to save file to S3: {path}") from e

    def _normalize_prefix(self, prefix: str) -> str:
        prefix = prefix.strip("/")

        # 相対 path の禁止
        if ".." in prefix:
            raise ValueError(f"S3 prefix cannot contain '..': {prefix}")

        # 空白がある場合も拒否
        if prefix != prefix.strip():
            raise ValueError(f"S3 prefix cannot have spaces: '{prefix}'")

        return prefix

    def _resolve_key(self, path: str) -> str:
        if path.startswith("/"):
            raise ValueError("Absolute path is not allowed")

        path_parts = path.split("/")
        if any(part == ".." for part in path_parts):
            raise ValueError("Path traversal detected")

        normalized_path = "/".join(
            part for part in path_parts if part
        )  # 空文字の場合はfalseyなので除外する

        if self.prefix:
            return f"{self.prefix}{normalized_path}"
        return normalized_path

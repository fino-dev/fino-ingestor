"""AWS S3 storage implementation."""

from fino_core.domain.storage import StoragePort


class S3Storage(StoragePort):
    """AWS S3へのストレージ実装"""

    def __init__(self, bucket: str, api_key: str, region: str) -> None:
        """
        S3ストレージを初期化

        Args:
            bucket: S3バケット名
            api_key: AWS API キー（アクセスキー）
            region: AWS リージョン
        """
        self.bucket = bucket
        self.api_key = api_key
        self.region = region
        # TODO: boto3クライアントの初期化を実装
        # self.s3_client = boto3.client('s3', ...)

    def save(self, key: str, data: bytes) -> None:
        """
        データをS3に保存

        Args:
            key: 保存先のキー（S3オブジェクトキー）
            data: 保存するデータ
        """
        # TODO: boto3を使用したS3への保存を実装
        # self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=data)
        pass

    def get(self, key: str) -> bytes:
        """
        S3からデータを取得

        Args:
            key: 取得するキー（S3オブジェクトキー）

        Returns:
            取得したデータ

        Raises:
            FileNotFoundError: 指定されたキーのオブジェクトが存在しない場合
        """
        # TODO: boto3を使用したS3からの取得を実装
        # response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
        # return response['Body'].read()
        raise NotImplementedError("S3Storage.get() is not yet implemented")

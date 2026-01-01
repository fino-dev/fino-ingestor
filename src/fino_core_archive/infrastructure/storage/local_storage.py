"""Local file system storage implementation."""

from pathlib import Path

from fino_core.domain.storage import StoragePort


class LocalStorage(StoragePort):
    """ローカルファイルシステムへのストレージ実装"""

    def __init__(self, base_path: str) -> None:
        """
        ローカルストレージを初期化

        Args:
            base_path: ベースパス（保存先のルートディレクトリ）
        """
        self.base_path = Path(base_path)
        # ベースパスが存在しない場合は作成
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes) -> None:
        """
        データをローカルファイルシステムに保存

        Args:
            key: 保存先のキー（パス）
            data: 保存するデータ
        """
        file_path = self.base_path / key
        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)

    def get(self, key: str) -> bytes:
        """
        ローカルファイルシステムからデータを取得

        Args:
            key: 取得するキー（パス）

        Returns:
            取得したデータ

        Raises:
            FileNotFoundError: 指定されたキーのファイルが存在しない場合
        """
        file_path = self.base_path / key
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path.read_bytes()

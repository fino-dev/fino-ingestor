from abc import ABC, abstractmethod


class Storage(ABC):
    """ストレージへの保存・取得を行うポート（インターフェース）

    このポートは、Documentの永続化を抽象化します。
    実装はinfrastructure層で行われます（LocalStorage, S3Storageなど）。
    """

    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        """データをストレージに保存

        Args:
            key: 保存先のキー（パス）
            data: 保存するデータ
        """
        ...

    @abstractmethod
    def get(self, key: str) -> bytes:
        """ストレージからデータを取得

        Args:
            key: 取得するキー（パス）

        Returns:
            取得したデータ

        Raises:
            FileNotFoundError: 指定されたキーのデータが存在しない場合
        """
        ...

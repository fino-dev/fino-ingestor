from abc import ABC, abstractmethod

from ..entity.document import Document
from ..value import DocumentPath


class DocumentRepository(ABC):
    """文書を永続化するRepositoryインターフェース

    このRepositoryは、DocumentPathを使用してストレージに保存します。
    DocumentPathは、datalake ingestionで効率的に管理できるパーティション構造を持ちます。
    """

    @abstractmethod
    def get(self, document_path: DocumentPath) -> Document:
        """指定されたパスからDocumentを取得

        Args:
            document_path: 取得するDocumentのパス

        Returns:
            取得されたDocument

        Raises:
            FileNotFoundError: 指定されたパスのDocumentが存在しない場合
        """
        ...

    @abstractmethod
    def store(self, document: Document) -> DocumentPath:
        """Documentをストレージに保存

        Args:
            document: 保存するDocument

        Returns:
            保存されたDocumentのパス
        """
        ...

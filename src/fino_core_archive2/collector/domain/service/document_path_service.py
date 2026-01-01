"""Domain Service for generating document storage paths."""

from fino_core.collector.domain.entity.document import Document
from fino_core.collector.domain.value import DocumentPath


class DocumentPathService:
    """文書のストレージパスを生成するDomain Service

    このサービスは、Documentエンティティから適切なストレージパスを生成します。
    datalake ingestion時に効率的に管理できるように、パーティション構造を持ちます。
    """

    @staticmethod
    def generate_path(document: Document) -> DocumentPath:
        """Documentからストレージパスを生成

        Args:
            document: パスを生成するDocument

        Returns:
            生成されたDocumentPath
        """
        return DocumentPath(
            source=document.metadata.source,
            filing_date=document.metadata.filing_date,
            document_id=document.document_id,
        )

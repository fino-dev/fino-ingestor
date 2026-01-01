from dataclasses import dataclass

from fino_core.collector.application.port.document_source import DocumentSource
from fino_core.collector.application.port.storage import Storage
from fino_core.collector.domain.repository import DocumentSourceCriteria


@dataclass
class CollectDocumentsInput:
    """文書収集の入力DTO

    ソース固有のCriteriaと、抽象的なDocumentSource、Storageを受け取ります。
    """

    criteria: DocumentSourceCriteria
    """文書取得の条件（ソース固有）"""

    document_source: DocumentSource
    """文書取得元（抽象インターフェース）"""

    storage: Storage
    """ストレージ（抽象インターフェース）"""

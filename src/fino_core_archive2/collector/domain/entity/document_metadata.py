from dataclasses import dataclass

from ..value import (
    DisclosureSource,
    DocumentId,
    DocumentType,
    FilingDate,
    FilingFormat,
    FilingLanguage,
    Ticker,
)


@dataclass(frozen=True)
class DocumentMetadata:
    """文書のメタデータを表現するValue Object

    DocumentMetadataはDocument Aggregateの一部としてのみ存在します。
    独立したエンティティとして扱うべきではありません。
    """

    document_id: DocumentId
    source: DisclosureSource
    title: str
    ticker: Ticker
    filing_language: FilingLanguage
    filing_format: FilingFormat
    filing_date: FilingDate
    disclosure_type: DocumentType

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.title or not self.title.strip():
            raise ValueError("title must not be empty")

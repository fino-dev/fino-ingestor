from dataclasses import dataclass

from fino_core.collector.domain.value import DisclosureSource, DocumentId, FilingDate


@dataclass(frozen=True)
class DocumentPath:
    """文書のストレージパスを表現するValue Object"""

    source: DisclosureSource
    filing_date: FilingDate
    document_id: DocumentId

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        # パス構造の整合性は自動的に保証される（Value Objectの不変性により）

    def to_storage_path(self) -> str:
        """ストレージパス（ディレクトリ）を生成

        Returns:
            ストレージパス（例: "edinet/2024/01/15/S100ABCD"）
        """
        date = self.filing_date.to_date()
        return (
            f"{self.source.value.lower()}/"
            f"{date.year:04d}/"
            f"{date.month:02d}/"
            f"{date.day:02d}/"
            f"{self.document_id.value}"
        )

    def to_document_path(self, filename: str | None = None) -> str:
        """文書ファイルのパスを生成

        Args:
            filename: ファイル名（省略時はdocument_idを使用）

        Returns:
            文書ファイルのパス（例: "edinet/2024/01/15/S100ABCD/document.pdf"）
        """
        base_path = self.to_storage_path()
        if filename:
            return f"{base_path}/{filename}"
        # デフォルトのファイル名（document_idを使用）
        return f"{base_path}/document"

    def __str__(self) -> str:
        return self.to_storage_path()

    def __repr__(self) -> str:
        return f"DocumentPath('{self.to_storage_path()}')"

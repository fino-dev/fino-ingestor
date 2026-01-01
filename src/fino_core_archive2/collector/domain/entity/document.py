from dataclasses import dataclass

from ..value import DocumentId, FilingFormat
from .document_metadata import DocumentMetadata
from .entity import AggregateRoot


# @see: about dataclass annotation:  https://qiita.com/fumiya0238/items/46115b399c4ea1322ee8
@dataclass(kw_only=True, slots=True, eq=False)
class Document(AggregateRoot):
    """文書本体を表現するドメインエンティティ（Aggregate Root）

    DocumentはDocumentMetadataを含み、実際の文書データ（resource）を保持します。

    Documentは以下の状態を持つことができます：
    - メタデータのみの状態: resource=None（外部システムからメタデータを取得した段階）
    - 完全な状態: resourceが存在（実際の文書データをダウンロードした段階）

    不変条件:
    - Document.document_id == DocumentMetadata.document_id
    - Document.filing_format == DocumentMetadata.filing_format
    - resourceが存在する場合、空のbytesであってはならない
    """

    document_id: DocumentId
    metadata: DocumentMetadata
    name: str
    filing_format: FilingFormat
    resource: bytes | None = None

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        if self.resource is not None and len(self.resource) == 0:
            raise ValueError("resource must not be empty bytes if provided")

        # 不変条件: document_idの整合性
        if self.document_id != self.metadata.document_id:
            msg = (
                f"Document.document_id ({self.document_id}) must match "
                f"DocumentMetadata.document_id ({self.metadata.document_id})"
            )
            raise ValueError(msg)

        # 不変条件: filing_formatの整合性
        if self.filing_format != self.metadata.filing_format:
            msg = (
                f"Document.filing_format ({self.filing_format}) must match "
                f"DocumentMetadata.filing_format ({self.metadata.filing_format})"
            )
            raise ValueError(msg)

    @classmethod
    def from_metadata(
        cls,
        metadata: DocumentMetadata,
        name: str,
    ) -> "Document":
        """メタデータからDocumentを作成するファクトリーメソッド

        メタデータのみの状態（resource=None）のDocumentを作成します。
        この状態は、外部システムからメタデータを取得した段階で使用されます。

        Args:
            metadata: 文書のメタデータ
            name: 文書名

        Returns:
            メタデータのみの状態のDocument（resource=None）
        """
        return cls(
            document_id=metadata.document_id,
            metadata=metadata,
            name=name,
            filing_format=metadata.filing_format,
            resource=None,
        )

    def with_resource(self, resource: bytes) -> "Document":
        """resourceを追加して新しいDocumentを作成する

        メタデータのみの状態から、完全な状態への遷移を行います。
        Documentは不変（immutable）であるため、新しいインスタンスを返します。

        Args:
            resource: 文書のバイトデータ

        Returns:
            resourceが設定された新しいDocument

        Raises:
            ValueError: resourceが空の場合
        """
        if len(resource) == 0:
            raise ValueError("resource must not be empty bytes")

        return Document(
            document_id=self.document_id,
            metadata=self.metadata,
            name=self.name,
            filing_format=self.filing_format,
            resource=resource,
        )

    @property
    def is_complete(self) -> bool:
        """Documentが完全な状態（resourceが存在）かどうかを返す"""
        return self.resource is not None

from typing import Generic, Protocol, TypeVar

from fino_core.domain.entity.document import Document
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType

# 各実装が独自のCriteria型を定義できるように型変数を使用
# Protocolの引数として使われるため、反変である必要がある
TCriteria = TypeVar("TCriteria", contravariant=True)


class DisclosureSourcePort(Protocol, Generic[TCriteria]):
    """開示ソースからドキュメントを取得するポート

    各実装は、独自のCriteria型（例: EdinetDocumentSearchCriteria, EdgarDocumentSearchCriteria）
    を定義し、それを受け取ることができます。
    """

    def list_available_documents(self, criteria: TCriteria) -> list[Document]: ...
    def download_document(
        self, document_id: DocumentId, format_type: FormatType
    ) -> bytes: ...

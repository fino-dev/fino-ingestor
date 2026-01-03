from dataclasses import dataclass

from fino_core.domain.entity.disclosure_source import DisclosureSource
from fino_core.domain.entity.document import Document
from fino_core.domain.value.document_id import DocumentId
from fino_core.util import TimeScope


@dataclass(frozen=True, slots=True, kw_only=True)
class EdinetDocumentSearchCriteria:
    timescope: TimeScope


# FIXME: TODO: 実装
class EdinetAdapter:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_source(self) -> DisclosureSource:
        return DisclosureSource(
            source_id="edinet",
            name="EDINET",
        )

    def list_available_documents(self, criteria: EdinetDocumentSearchCriteria) -> list[Document]:
        return []

    def download_document(self, document_id: DocumentId) -> bytes:
        return b""

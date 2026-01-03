from dataclasses import dataclass

from fino_core.domain.entity.disclosure_source import DisclosureSource
from fino_core.domain.entity.document import Document
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.ticker import Ticker
from fino_core.util import TimeScope


@dataclass(frozen=True, slots=True, kw_only=True)
class TDNetDocumentSearchCriteria:
    ticker: list[Ticker]
    timescope: TimeScope


# FIXME: TODO: 実装
# Protocol を使用して実装してるため継承不要
class TDNetAdapter:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    def get_source(self) -> DisclosureSource:
        return DisclosureSource(
            source_id="edinet",
            name="EDINET",
        )

    def list_available_documents(self, criteria: TDNetDocumentSearchCriteria) -> list[Document]:
        return []

    def download_document(self, document_id: DocumentId) -> bytes:
        return b""

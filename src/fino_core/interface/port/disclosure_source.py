from typing import Protocol

from fino_core.domain.entity.disclosure_source import DisclosureSource as DisclosureSource
from fino_core.domain.entity.document import Document
from fino_core.domain.repository.document import DocumentSearchCriteria
from fino_core.domain.value.document_id import DocumentId


class DisclosureSourcePort(Protocol):
    def list_available_documents(self, criteria: DocumentSearchCriteria) -> list[Document]: ...
    def download_document(self, document_id: DocumentId) -> bytes: ...

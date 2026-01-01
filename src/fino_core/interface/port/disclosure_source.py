from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fino_core.domain.entity.disclosure_source import DisclosureSource
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.document_search_criteria import DocumentSearchCriteria

if TYPE_CHECKING:
    from fino_core.domain.entity.document import Document


class DisclosureSourcePort(ABC):
    @abstractmethod
    def get_source(self) -> DisclosureSource: ...

    @abstractmethod
    def list_available_documents(self, criteria: DocumentSearchCriteria) -> list["Document"]: ...

    @abstractmethod
    def download_document(self, document_id: DocumentId) -> bytes: ...

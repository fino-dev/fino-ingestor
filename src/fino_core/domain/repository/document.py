from abc import ABC, abstractmethod
from typing import Optional

from fino_core.domain.entity.document import Document
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.document_search_criteria import DocumentSearchCriteria


class DocumentRepository(ABC):
    @abstractmethod
    def get(self, document_id: DocumentId) -> Optional[Document]: ...

    @abstractmethod
    def save(self, document: Document, file: bytes) -> None: ...

    @abstractmethod
    def list(self, criteria: DocumentSearchCriteria) -> list[Document]: ...

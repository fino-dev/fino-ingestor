from abc import ABC, abstractmethod

from fino_core.domain.entity.document import Document


class DocumentRepository(ABC):
    @abstractmethod
    def exists(self, document: Document) -> bool: ...
    @abstractmethod
    def save(self, document: Document, file: bytes) -> None: ...

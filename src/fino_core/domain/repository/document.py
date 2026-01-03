from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from fino_core.domain.entity.document import Document
from fino_core.domain.value.market import Market


@dataclass(frozen=True, slots=True)
class DocumentSearchCriteria(Protocol):
    market: Market


class DocumentRepository(ABC):
    @abstractmethod
    def exists(self, document: Document) -> bool: ...

    @abstractmethod
    def save(self, document: Document, file: bytes) -> None: ...

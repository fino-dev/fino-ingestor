from dataclasses import dataclass

from fino_ingestor.domain.entity.document import Document


@dataclass(frozen=True, slots=True)
class ListDocumentOutput:
    available_document_list: list[Document]
    stored_document_list: list[Document]

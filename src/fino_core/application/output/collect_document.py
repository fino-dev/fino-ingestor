from dataclasses import dataclass

from fino_ingestor.domain.entity.document import Document


@dataclass(frozen=True, slots=True)
class CollectDocumentOutput:
    collected_document_list: list[Document]

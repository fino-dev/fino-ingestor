from dataclasses import dataclass

from fino_core.domain.entity.document import Document


@dataclass(frozen=True, slots=True)
class CollectDocumentOutput:
    collected_document_list: list[Document]

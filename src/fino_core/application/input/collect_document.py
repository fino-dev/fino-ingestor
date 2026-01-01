from dataclasses import dataclass

from fino_core.domain.value.document_search_criteria import DocumentSearchCriteria


@dataclass(frozen=True, slots=True)
class CollectDocumentInput:
    criteria: DocumentSearchCriteria


test

from dataclasses import dataclass

from fino_core.domain.repository.document import DocumentSearchCriteria
from fino_core.interface.port.disclosure_source import DisclosureSourcePort


@dataclass(frozen=True, slots=True)
class ListDocumentInput:
    disclosure_source: DisclosureSourcePort
    criteria: DocumentSearchCriteria

from dataclasses import dataclass

from fino_ingestor.infrastructure.adapter.disclosure_source.edinet import (
    EdinetDocumentSearchCriteria,
)
from fino_ingestor.interface.port.disclosure_source import DisclosureSourcePort


@dataclass(frozen=True, slots=True)
class CollectDocumentInput:
    disclosure_source: DisclosureSourcePort[EdinetDocumentSearchCriteria]
    criteria: EdinetDocumentSearchCriteria

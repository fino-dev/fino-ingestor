from dataclasses import dataclass

from fino_ingestor.domain.model import AggregateRoot
from fino_ingestor.domain.value.disclosure_date import DisclosureDate
from fino_ingestor.domain.value.disclosure_source import DisclosureSource
from fino_ingestor.domain.value.disclosure_type import DisclosureType
from fino_ingestor.domain.value.document_id import DocumentId
from fino_ingestor.domain.value.format_type import FormatType
from fino_ingestor.domain.value.ticker import Ticker


@dataclass(eq=False, slots=True)
class Document(AggregateRoot):
    document_id: DocumentId
    filing_name: str
    ticker: Ticker
    disclosure_type: DisclosureType
    disclosure_source: DisclosureSource
    disclosure_date: DisclosureDate
    filing_format: FormatType

from dataclasses import dataclass

from fino_core.domain.model import AggregateRoot
from fino_core.domain.value.disclosure_date import DisclosureDate
from fino_core.domain.value.disclosure_type import DisclosureType
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType
from fino_core.domain.value.market import Market
from fino_core.domain.value.ticker import Ticker


@dataclass(eq=False, slots=True)
class Document(AggregateRoot):
    document_id: DocumentId
    filing_name: str
    market: Market
    ticker: Ticker
    disclosure_type: DisclosureType
    disclosure_source_id: str
    disclosure_date: DisclosureDate
    filing_format: FormatType

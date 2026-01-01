from dataclasses import dataclass

from fino_core.domain.model import AggregateRoot
from fino_core.domain.value import disclosure_date
from fino_core.domain.value.disclosure_date import DisclosureDate
from fino_core.domain.value.disclosure_type import DisclosureType
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType
from fino_core.domain.value.ticker import Ticker


@dataclass(eq=False, slots=True)
class Document(AggregateRoot):
    document_id: DocumentId
    filing_name: str
    ticker: Ticker
    disclosure_type: DisclosureType
    disclosure_source_id: str
    disclosure_date: DisclosureDate
    filing_format: FormatType


TODO:
- fino core submodule化したほうが開発しやすい
- disclosure_sourceはやっぱりあくまでもdocumentのVOでありdomain層で何ができるかなどの外部機能の提供を行うportとして提供するべきである。
    - 外部の機能は業務領域と切り離すべきであると考えるので概念としてのVOのみ定義してその具体的な機能はportとして提供するべきである。

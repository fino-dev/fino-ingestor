from dataclasses import dataclass
from datetime import datetime, time
from typing import Any

from edinet import Edinet
from edinet.enums.response import GetDocumentResponseWithDocs

from fino_core.domain.entity.document import Document
from fino_core.domain.value.disclosure_date import DisclosureDate
from fino_core.domain.value.disclosure_type import DisclosureType, DisclosureTypeEnum
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType, FormatTypeEnum
from fino_core.domain.value.market import Market
from fino_core.domain.value.ticker import Ticker
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.interface.port.disclosure_source import DisclosureSourcePort
from fino_core.util import TimeScope


@dataclass(frozen=True, slots=True, kw_only=True)
class EdinetDocumentSearchCriteria:
    market: Market
    timescope: TimeScope


class EdinetAdapter(DisclosureSourcePort[EdinetDocumentSearchCriteria]):
    def __init__(self, config: EdinetConfig) -> None:
        self.client = Edinet(token=config.api_key)

    def list_available_documents(
        self, criteria: EdinetDocumentSearchCriteria
    ) -> list[Document]:
        documents: list[Document] = []

        for date in criteria.timescope.iterate_by_day():
            target_datetime = datetime.combine(date, time.min)
            document_list: GetDocumentResponseWithDocs = self.client.get_document_list(
                date=target_datetime, withdocs=True
            )

            for document in document_list:
                document = self._convert_to_document(document, criteria.market)
                if document:
                    documents.append(document)

        return documents

    def download_document(self, document_id: DocumentId) -> bytes:
        edinet_doc = self.client.get_document(document_id.value)
        return edinet_doc.download()

    def _convert_to_document(self, edinet_doc: Any, market: Market) -> Document | None:
        try:
            doc_id = DocumentId(value=edinet_doc.doc_id)
            disclosure_date = DisclosureDate(value=edinet_doc.submit_date)

            disclosure_type = self._map_disclosure_type(edinet_doc.doc_type_code)
            if disclosure_type is None:
                return None

            format_type = self._map_format_type(edinet_doc.form_code)
            if format_type is None:
                return None

            ticker = Ticker(value=edinet_doc.sec_code or "")

            return Document(
                document_id=doc_id,
                filing_name=edinet_doc.doc_description or "",
                market=market,
                ticker=ticker,
                disclosure_type=disclosure_type,
                disclosure_source_id="edinet",
                disclosure_date=disclosure_date,
                filing_format=format_type,
            )
        except Exception:
            return None

    def _map_disclosure_type(self, doc_type_code: str | None) -> DisclosureType | None:
        if doc_type_code is None:
            return None

        mapping = {
            "120": DisclosureTypeEnum.ANNUAL_REPORT,
            "130": DisclosureTypeEnum.AMENDED_ANNUAL_REPORT,
            "140": DisclosureTypeEnum.SEMI_ANNUAL_REPORT,
            "150": DisclosureTypeEnum.AMENDED_SEMI_ANNUAL_REPORT,
            "160": DisclosureTypeEnum.QUARTERLY_REPORT,
            "170": DisclosureTypeEnum.AMENDED_QUARTERLY_REPORT,
            "210": DisclosureTypeEnum.MATERIAL_EVENT_REPORT,
            "310": DisclosureTypeEnum.PARENT_COMPANY_REPORT,
            "320": DisclosureTypeEnum.SHARE_REPURCHASE_REPORT,
            "330": DisclosureTypeEnum.AMENDED_SHARE_REPURCHASE_REPORT,
        }

        enum = mapping.get(doc_type_code)
        if enum is None:
            return None

        return DisclosureType(enum=enum)

    def _map_format_type(self, form_code: str | None) -> FormatType | None:
        if form_code is None:
            return None

        mapping = {
            "01": FormatTypeEnum.XBRL,
            "02": FormatTypeEnum.PDF,
            "03": FormatTypeEnum.CSV,
        }

        enum = mapping.get(form_code)
        if enum is None:
            return FormatType(enum=FormatTypeEnum.OTHER)

        return FormatType(enum=enum)

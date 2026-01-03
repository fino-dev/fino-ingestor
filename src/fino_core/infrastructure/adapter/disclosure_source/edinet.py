from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Literal

from edinet import Edinet
from edinet.enums.response import GetDocumentDocs

from fino_core.domain.entity.document import Document
from fino_core.domain.value.disclosure_date import DisclosureDate
from fino_core.domain.value.disclosure_type import DisclosureType, DisclosureTypeEnum
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType, FormatTypeEnum
from fino_core.domain.value.market import Market
from fino_core.domain.value.ticker import Ticker
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.util import TimeScope


@dataclass(frozen=True, slots=True, kw_only=True)
class EdinetDocumentSearchCriteria:
    market: Market
    format_type: FormatType
    timescope: TimeScope


class EdinetAdapter:
    def __init__(self, config: EdinetConfig) -> None:
        self.client = Edinet(token=config.api_key)

    def list_available_documents(
        self, criteria: EdinetDocumentSearchCriteria
    ) -> list[Document]:
        documents: list[Document] = []

        # EDINET APIの仕様に従い日付単位で一覧を取得していく
        for target_date in criteria.timescope.iterate_by_day():
            target_datetime = datetime.combine(target_date, time.min)

            # 書類一覧取得APIを呼び出し、書類一覧を取得する
            document_list_response = self.client.get_document_list(
                date=target_datetime, withdocs=True
            )

            target_document_list = document_list_response["results"]

            # EDINETの書類データをアプリ形式に変換していく
            for target_document in target_document_list:
                document = self._convert_to_document(target_document, criteria.market)
                if document:
                    documents.append(document)

        return documents

    def download_document(
        self, document_id: DocumentId, format_type: FormatType
    ) -> bytes:
        # format_typeに応じてEDINET APIのtypeパラメータを決定
        edinet_type = self._format_type_to_edinet_type(format_type)
        return self.client.get_document(docId=document_id.value, type=edinet_type)

    def _format_type_to_edinet_type(
        self, format_type: FormatType
    ) -> Literal[1, 2, 3, 4, 5]:
        """FormatTypeをEDINET APIのtypeパラメータに変換"""
        mapping: dict[FormatTypeEnum, Literal[1, 2, 3, 4, 5]] = {
            FormatTypeEnum.XBRL: 1,
            FormatTypeEnum.PDF: 2,
            FormatTypeEnum.CSV: 5,
        }
        return mapping.get(format_type.enum, 1)  # デフォルトはXBRL

    def _convert_to_document(
        self,
        edinet_doc: GetDocumentDocs,
        market: Market,
    ) -> Document | None:
        try:
            doc_id = DocumentId(value=edinet_doc["docID"])

            date_string = date.fromisoformat(edinet_doc["submitDateTime"])
            disclosure_date = DisclosureDate(value=date_string)

            disclosure_type = self._map_disclosure_type(edinet_doc["docTypeCode"])
            if disclosure_type is None:
                return None

            format_type = self._map_format_type(edinet_doc["formCode"])
            if format_type is None:
                return None

            ticker = Ticker(value=edinet_doc.get("secCode") or "")

            return Document(
                document_id=doc_id,
                filing_name=edinet_doc.get("docDescription") or "",
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

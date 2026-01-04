from dataclasses import dataclass
from datetime import datetime, time
from typing import Literal

from edinet import Edinet
from edinet.enums.response import GetDocumentDocs
from fino_core.domain.entity.document import Document
from fino_core.domain.value.disclosure_date import DisclosureDate
from fino_core.domain.value.disclosure_source import DisclosureSource, DisclosureSourceEnum
from fino_core.domain.value.disclosure_type import DisclosureType, DisclosureTypeEnum
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType, FormatTypeEnum
from fino_core.domain.value.ticker import Ticker
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.util import TimeScope


@dataclass(frozen=True, slots=True, kw_only=True)
class EdinetDocumentSearchCriteria:
    format_type: FormatType
    """書類のフォーマットタイプ"""
    timescope: TimeScope
    """取得に使用する日付範囲"""
    # disclosure_type: DisclosureType
    # """開示書類の種類"""
    # ticker: Ticker
    # """企業ティッカー"""


class EdinetAdapter:
    id: Literal[DisclosureSourceEnum.EDINET] = DisclosureSourceEnum.EDINET

    def __init__(self, config: EdinetConfig) -> None:
        self.client = Edinet(token=config.api_key)

    def list_available_documents(self, criteria: EdinetDocumentSearchCriteria) -> list[Document]:
        document_list: list[Document] = []

        # EDINET APIの仕様に従い、日付単位で一覧を取得していく
        for target_date in criteria.timescope.iterate_by_day():
            target_datetime = datetime.combine(target_date, time.min)

            # 書類一覧取得APIを呼び出し、書類一覧を取得する
            document_list_response = self.client.get_document_list(
                date=target_datetime, withdocs=True
            )

            edinet_document_list = document_list_response["results"]

            # EDINETの書類データをアプリ形式に変換していく
            for edinet_document in edinet_document_list:
                document = self._convert_to_document(
                    edinet_doc=edinet_document, target_format_type=criteria.format_type
                )

                if not document:
                    continue

                document_list.append(document)

        return document_list

    def download_document(self, document_id: DocumentId, format_type: FormatType) -> bytes:
        # format_typeに応じてEDINET APIのtypeパラメータを決定
        edinet_format_type = self.convert_to_edinet_format_type(format_type)
        if edinet_format_type is None:
            raise ValueError(f"Unsupported format type: {format_type}")

        return self.client.get_document(docId=document_id.value, type=edinet_format_type)

    @classmethod
    def _generate_edinet_document_id(cls, doc_id: str, format_type: FormatType) -> DocumentId:
        """
        EDINET開示書類のIDを生成する
        EDINETでは開示書類種別単位でdocIDが割り振られており、フォーマットの違いを識別していないので、format_typeをsuffixに追加する
        > "EDINET_XXXXXXXX_CSV"
        """
        return DocumentId(value=f"{cls.id}_{doc_id}_{format_type.value}")

    def _convert_to_document(
        self, edinet_doc: GetDocumentDocs, target_format_type: FormatType
    ) -> Document | None:
        """
        EDINET APIのレスポンスの書類一覧データをDocumentに変換する。
        データ形式が違反している場合はNoneを返す
        """
        try:
            document_id = self._generate_edinet_document_id(
                doc_id=edinet_doc["docID"], format_type=target_format_type
            )

            disclosure_type = self._map_disclosure_type(edinet_doc["docTypeCode"])
            # 開示書類の種類が不明な場合は除外する
            if disclosure_type is None:
                return None

            format_type_list = self._map_format_type(
                edinet_doc["xbrlFlag"], edinet_doc["pdfFlag"], edinet_doc["csvFlag"]
            )
            # criteriaに指定されたフォーマットに書類が対応しているか確認し、存在しない場合は除外する
            if target_format_type not in format_type_list:
                return None

            return Document(
                document_id=document_id,
                filing_name=edinet_doc.get("docDescription") or "",
                ticker=Ticker(value=edinet_doc.get("secCode") or ""),
                disclosure_type=disclosure_type,
                disclosure_source=DisclosureSource(enum=DisclosureSourceEnum.EDINET),
                # EDINET APIのレスポンスの日付からパースして取得する（(YYYY-MM-DD hh:mm 形式)）
                disclosure_date=DisclosureDate(
                    value=datetime.strptime(edinet_doc["submitDateTime"], "%Y-%m-%d %H:%M").date()
                ),
                filing_format=target_format_type,
            )
        except Exception:
            return None

    def convert_to_edinet_format_type(self, format_type: FormatType) -> Literal[1, 2, 5] | None:
        """
        FormatTypeをEDINET APIのtypeパラメータに変換
        1. 提出本文書及び監査報告
        2. PDF
        5. CSV
        それ以外は現状は対応しない。
        """
        mapping: dict[FormatTypeEnum, Literal[1, 2, 5]] = {
            FormatTypeEnum.XBRL: 1,
            FormatTypeEnum.PDF: 2,
            FormatTypeEnum.CSV: 5,
        }
        return mapping.get(format_type.enum)

    def _map_disclosure_type(self, doc_type_code: str | None) -> DisclosureType | None:
        """
        EDINET APIのレスポンスの書類一覧データからDisclosureTypeにマッピングする。
        一致するものが存在しない場合にはNoneを返す。
        """
        if doc_type_code is None:
            return None

        mapping = {
            "120": DisclosureTypeEnum.ANNUAL_REPORT,
            "130": DisclosureTypeEnum.AMENDED_ANNUAL_REPORT,
            "140": DisclosureTypeEnum.QUARTERLY_REPORT,
            "150": DisclosureTypeEnum.AMENDED_QUARTERLY_REPORT,
            "160": DisclosureTypeEnum.SEMI_ANNUAL_REPORT,
            "170": DisclosureTypeEnum.AMENDED_SEMI_ANNUAL_REPORT,
            "180": DisclosureTypeEnum.MATERIAL_EVENT_REPORT,
            "190": DisclosureTypeEnum.AMENDED_MATERIAL_EVENT_REPORT,
            "200": DisclosureTypeEnum.PARENT_COMPANY_REPORT,
            "210": DisclosureTypeEnum.AMENDED_PARENT_COMPANY_REPORT,
            "220": DisclosureTypeEnum.SHARE_REPURCHASE_REPORT,
            "230": DisclosureTypeEnum.AMENDED_SHARE_REPURCHASE_REPORT,
        }

        enum = mapping.get(doc_type_code)
        if enum is None:
            return None

        return DisclosureType(enum=enum)

    def _map_format_type(
        self, xbrl_flag: str | None, pdf_flag: str | None, csv_flag: str | None
    ) -> list[FormatType]:
        """
        EDINET APIのレスポンスの書類一覧データからFormatTypeにマッピングする。
        対応しているフォーマットを一覧で返す。
        FormatTypeに存在しない場合はOTHERとしてリストに追加する。
        """
        # 対応しているフォーマットをリストに追加していく
        format_type_list: list[FormatType] = []
        if xbrl_flag == "1":
            format_type_list.append(FormatType(enum=FormatTypeEnum.XBRL))
        if pdf_flag == "1":
            format_type_list.append(FormatType(enum=FormatTypeEnum.PDF))
        if csv_flag == "1":
            format_type_list.append(FormatType(enum=FormatTypeEnum.CSV))

        # 上記のフォーマット以外の場合、Otherとして整理する
        if len(format_type_list) == 0:
            format_type_list.append(FormatType(enum=FormatTypeEnum.OTHER))

        return format_type_list

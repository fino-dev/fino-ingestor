from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Literal

from edinet import Edinet
from edinet.enums.response import GetDocumentDocs, GetDocumentResponseWithDocs

from fino_ingestor.domain.entity.document import Document
from fino_ingestor.domain.exception.disclosure_source import (
    DisclosureSourceApiError,
    DisclosureSourceConnectionError,
    DisclosureSourceInvalidResponseError,
)
from fino_ingestor.domain.value.disclosure_date import DisclosureDate
from fino_ingestor.domain.value.disclosure_source import (
    DisclosureSource,
    DisclosureSourceEnum,
)
from fino_ingestor.domain.value.disclosure_type import (
    DisclosureType,
    DisclosureTypeEnum,
)
from fino_ingestor.domain.value.document_id import DocumentId
from fino_ingestor.domain.value.format_type import FormatType, FormatTypeEnum
from fino_ingestor.domain.value.ticker import Ticker
from fino_ingestor.interface.config.disclosure import EdinetConfig
from fino_ingestor.util import TimeScope


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

    def list_available_documents(
        self, criteria: EdinetDocumentSearchCriteria
    ) -> list[Document]:
        document_list: list[Document] = []

        # EDINET APIの仕様に従い、日付単位で一覧を取得していく
        for target_date in criteria.timescope.iterate_by_day():
            target_datetime = datetime.combine(target_date, time.min)

            document_list_response: GetDocumentResponseWithDocs | None = None

            # 書類一覧取得APIを呼び出し、書類一覧を取得する
            try:
                document_list_response = self.client.get_document_list(
                    date=target_datetime, withdocs=True
                )
            except ConnectionError | TimeoutError as e:
                raise DisclosureSourceConnectionError(
                    message=f"EDINET APIへの接続に失敗しました: {str(e)}",
                    details={
                        "target_date": target_date.isoformat(),
                        "api_endpoint": "get_document_list",
                    },
                ) from e
            except Exception as e:
                # その他の予期しないエラー
                raise DisclosureSourceConnectionError(
                    message=f"EDINET APIの呼び出し中に予期しないエラーが発生しました: {str(e)}",
                    details={
                        "target_date": target_date.isoformat(),
                        "error_type": type(e).__name__,
                    },
                ) from e

            # レスポンスの検証
            validated_response = self._validate_document_list_response(
                document_list_response, target_date
            )

            edinet_document_list = validated_response["results"]

            # EDINETの書類データをアプリ形式に変換していく
            for edinet_document in edinet_document_list:
                document = self._convert_to_document(
                    edinet_doc=edinet_document, target_format_type=criteria.format_type
                )

                if not document:
                    continue

                document_list.append(document)

        return document_list

    def _validate_document_list_response(
        self, response: GetDocumentResponseWithDocs | None, target_date: Any
    ) -> dict[str, Any]:
        """
        EDINET APIのget_document_listレスポンスを検証する

        Args:
            response: EDINET APIからのレスポンス
            target_date: リクエストした対象日付

        Returns:
            検証済みのレスポンス

        Raises:
            DisclosureSourceApiError: APIがエラーレスポンスを返した場合
            DisclosureSourceInvalidResponseError: レスポンスが期待される形式でない場合
        """
        if response is None:
            raise DisclosureSourceInvalidResponseError(
                message="EDINET APIのレスポンスがNoneです",
                details={
                    "target_date": str(target_date),
                },
            )

        # ステータスコードの確認
        status_code = response.get("metadata", {}).get("status")
        if status_code and status_code != "200":
            # APIエラーレスポンスの場合
            error_message = response.get("metadata", {}).get("message", "不明なエラー")
            raise DisclosureSourceApiError(
                message=f"EDINET APIがエラーを返しました: {error_message}",
                status_code=int(status_code) if status_code else None,
                details={
                    "target_date": str(target_date),
                    "response_metadata": response.get("metadata"),
                },
            )

        # 必須フィールドの存在確認
        if "results" not in response:
            raise DisclosureSourceInvalidResponseError(
                message="EDINET APIのレスポンスに 'results' フィールドが存在しません",
                response_data=response,
                details={
                    "target_date": str(target_date),
                    "available_keys": list(response.keys()),
                },
            )

        # resultsがリスト形式であることを確認
        if not isinstance(response["results"], list):
            raise DisclosureSourceInvalidResponseError(
                message="EDINET APIのレスポンスの 'results' フィールドがリスト形式ではありません",
                response_data={"results_type": type(response["results"]).__name__},
                details={
                    "target_date": str(target_date),
                },
            )

        return response

    def download_document(self, document: Document) -> bytes:
        """
        ** EDINETでは同一docIdで複数のフォーマットが存在する可能性が、
        設計上、document IDにformat typeをsuffixに追加しているため、
        このメソッドではdocument IDからformat typeを取得してダウンロードする。
        """
        # format_typeに応じてEDINET APIのtypeパラメータを決定
        edinet_format_type = self.convert_to_edinet_format_type(document.filing_format)
        if edinet_format_type is None:
            raise ValueError(f"Unsupported format type: {document.filing_format}")

        doc_id, _ = self._parse_edinet_doc_id(document.document_id)

        try:
            return self.client.get_document(docId=doc_id, type=edinet_format_type)
        except ConnectionError as e:
            raise DisclosureSourceConnectionError(
                message=f"EDINET APIへの接続に失敗しました: {str(e)}",
                details={
                    "document_id": document.document_id.value,
                    "doc_id": doc_id,
                    "format_type": document.filing_format.value,
                    "api_endpoint": "get_document",
                },
            ) from e
        except Exception as e:
            raise DisclosureSourceConnectionError(
                message=f"書類ダウンロード中に予期しないエラーが発生しました: {str(e)}",
                details={
                    "document_id": document.document_id.value,
                    "error_type": type(e).__name__,
                },
            ) from e

    @classmethod
    def _generate_document_id(cls, doc_id: str, format_type: FormatType) -> DocumentId:
        """
        EDINET開示書類のIDを生成する
        EDINETでは開示書類種別単位でdocIDが割り振られており、フォーマットの違いを識別していないので、format_typeをsuffixに追加する
        > "EDINET_XXXXXXXX_CSV"
        """
        return DocumentId(value=f"{cls.id.value}_{doc_id}_{format_type.value}")

    @classmethod
    def _parse_edinet_doc_id(cls, document_id: DocumentId) -> tuple[str, FormatType]:
        """
        EDINET開示書類のIDを解析する
        EDINETでは開示書類種別単位でdocIDが割り振られており、フォーマットの違いを識別していないので、format_typeをsuffixに追加する
        > "EDINET_XXXXXXXX_CSV"
        """
        parts = document_id.value.split("_")
        if len(parts) != 3:
            raise ValueError(f"Invalid document ID: {document_id.value}")
        return parts[1], FormatType(enum=FormatTypeEnum(parts[2]))

    def _convert_to_document(
        self, edinet_doc: GetDocumentDocs, target_format_type: FormatType
    ) -> Document | None:
        """
        EDINET APIのレスポンスの書類一覧データをDocumentに変換する。
        データ形式が違反している場合はNoneを返す
        """
        try:
            # generate document id
            document_id = self._generate_document_id(
                doc_id=edinet_doc["docID"], format_type=target_format_type
            )

            # validate ticker
            # FIXME: secCodeは証券コードのようなもので、tickerとは異なるため、tickerを取得する必要がある
            ticker = edinet_doc.get("secCode")
            if ticker is None:
                return None

            # map and validate disclosure type
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
                filing_name=edinet_doc.get("docDescription") or "UNKNOWN",
                ticker=Ticker(value=ticker),
                disclosure_type=disclosure_type,
                disclosure_source=DisclosureSource(enum=DisclosureSourceEnum.EDINET),
                # EDINET APIのレスポンスの日付からパースして取得する（(YYYY-MM-DD hh:mm 形式)）
                disclosure_date=DisclosureDate(
                    value=datetime.strptime(
                        edinet_doc["submitDateTime"], "%Y-%m-%d %H:%M"
                    ).date()
                ),
                filing_format=target_format_type,
            )
        except Exception:
            return None

    def convert_to_edinet_format_type(
        self, format_type: FormatType
    ) -> Literal[1, 2, 5] | None:
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

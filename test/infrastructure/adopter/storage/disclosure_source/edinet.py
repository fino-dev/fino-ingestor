from datetime import date
from typing import Any
from unittest.mock import patch

import pytest

from fino_core.domain.value.disclosure_source import DisclosureSourceEnum
from fino_core.domain.value.disclosure_type import DisclosureTypeEnum
from fino_core.domain.value.document_id import DocumentId
from fino_core.domain.value.format_type import FormatType, FormatTypeEnum
from fino_core.infrastructure.adapter.disclosure_source.edinet import (
    EdinetAdapter,
    EdinetDocumentSearchCriteria,
)
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.util import TimeScope


class TestEdinetAdapter:
    @pytest.fixture
    def config(self) -> EdinetConfig:
        return EdinetConfig(api_key="test_api_key")

    @pytest.fixture
    def adapter(self, config: EdinetConfig) -> EdinetAdapter:
        return EdinetAdapter(config=config)

    @pytest.fixture
    def mock_edinet_document(self) -> dict[str, str]:
        """EDINET APIのget_document_listのレスポンスのサンプル"""
        return {
            "docID": "S100TEST",
            "docDescription": "有価証券報告書",
            "docTypeCode": "120",
            "secCode": "12345",
            "submitDateTime": "2024-03-15 09:00",
            "xbrlFlag": "1",
            "pdfFlag": "1",
            "csvFlag": "0",
        }

    ########## instance check ##########
    def test_instance_success(self, adapter: EdinetAdapter) -> None:
        # アダプターが正しくインスタンス化されることを確認
        assert adapter is not None
        assert isinstance(adapter, EdinetAdapter)

    def test_adapter_id(self, adapter: EdinetAdapter) -> None:
        assert adapter.id == DisclosureSourceEnum.EDINET

    def test_client_initialization(self, config: EdinetConfig) -> None:
        adapter = EdinetAdapter(config=config)
        assert adapter.client is not None

    ########## list_available_documents ##########
    def test_list_available_documents_success(self, adapter: EdinetAdapter) -> None:
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.XBRL),
            timescope=TimeScope(year=2024, month=3, day=15),
        )

        mock_response = {
            "results": [
                {
                    "docID": "S100TEST1",
                    "docDescription": "有価証券報告書",
                    "docTypeCode": "120",
                    "secCode": "12345",
                    "submitDateTime": "2024-03-15 09:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "0",
                },
                {
                    "docID": "S100TEST2",
                    "docDescription": "四半期報告書",
                    "docTypeCode": "140",
                    "secCode": "67890",
                    "submitDateTime": "2024-03-15 10:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "0",
                    "csvFlag": "0",
                },
            ]
        }

        with patch.object(
            adapter.client, "get_document_list", return_value=mock_response
        ) as mock_get_list:
            documents = adapter.list_available_documents(criteria)

            assert len(documents) == 2
            assert documents[0].document_id.value == "EDINET_S100TEST1_XBRL"
            assert documents[0].filing_name == "有価証券報告書"
            assert documents[0].ticker.value == "12345"
            assert documents[0].disclosure_type.enum == DisclosureTypeEnum.ANNUAL_REPORT
            assert documents[0].filing_format.enum == FormatTypeEnum.XBRL

            assert documents[1].document_id.value == "EDINET_S100TEST2_XBRL"
            assert documents[1].filing_name == "四半期報告書"
            assert documents[1].ticker.value == "67890"
            assert (
                documents[1].disclosure_type.enum == DisclosureTypeEnum.QUARTERLY_REPORT
            )

            mock_get_list.assert_called_once()

    def test_list_available_documents_filters_by_format_type(
        self, adapter: EdinetAdapter
    ) -> None:
        """指定されたフォーマットタイプに対応していない書類を除外する"""
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.CSV),
            timescope=TimeScope(year=2024, month=3, day=15),
        )

        mock_response = {
            "results": [
                {
                    "docID": "S100TEST1",
                    "docDescription": "有価証券報告書",
                    "docTypeCode": "120",
                    "secCode": "12345",
                    "submitDateTime": "2024-03-15 09:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "0",  # CSVに非対応
                },
                {
                    "docID": "S100TEST2",
                    "docDescription": "四半期報告書",
                    "docTypeCode": "140",
                    "secCode": "67890",
                    "submitDateTime": "2024-03-15 10:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "1",  # CSVに対応
                },
            ]
        }

        with patch.object(adapter.client, "get_document_list", return_value=mock_response):
            documents = adapter.list_available_documents(criteria)

            # CSV対応の書類のみが返される
            assert len(documents) == 1
            assert documents[0].document_id.value == "EDINET_S100TEST2_CSV"
            assert documents[0].filing_format.enum == FormatTypeEnum.CSV

    def test_list_available_documents_filters_unknown_disclosure_type(
        self, adapter: EdinetAdapter
    ) -> None:
        """未知の開示書類種別を除外する"""
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.XBRL),
            timescope=TimeScope(year=2024, month=3, day=15),
        )

        mock_response = {
            "results": [
                {
                    "docID": "S100TEST1",
                    "docDescription": "有価証券報告書",
                    "docTypeCode": "120",
                    "secCode": "12345",
                    "submitDateTime": "2024-03-15 09:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "0",
                },
                {
                    "docID": "S100TEST2",
                    "docDescription": "未知の書類",
                    "docTypeCode": "999",  # 未知の書類コード
                    "secCode": "67890",
                    "submitDateTime": "2024-03-15 10:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "0",
                    "csvFlag": "0",
                },
            ]
        }

        with patch.object(adapter.client, "get_document_list", return_value=mock_response):
            documents = adapter.list_available_documents(criteria)

            # 既知の書類のみが返される
            assert len(documents) == 1
            assert documents[0].document_id.value == "EDINET_S100TEST1_XBRL"

    def test_list_available_documents_with_multiple_days(
        self, adapter: EdinetAdapter
    ) -> None:
        """複数日のデータを処理できる"""
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.XBRL),
            timescope=TimeScope(year=2024, month=3),
        )

        mock_response_day1: dict[str, list[dict[str, str]]] = {
            "results": [
                {
                    "docID": "S100TEST1",
                    "docDescription": "有価証券報告書",
                    "docTypeCode": "120",
                    "secCode": "12345",
                    "submitDateTime": "2024-03-01 09:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "0",
                }
            ]
        }

        mock_response_day2: dict[str, list[dict[str, str]]] = {
            "results": [
                {
                    "docID": "S100TEST2",
                    "docDescription": "四半期報告書",
                    "docTypeCode": "140",
                    "secCode": "67890",
                    "submitDateTime": "2024-03-02 10:00",
                    "xbrlFlag": "1",
                    "pdfFlag": "0",
                    "csvFlag": "0",
                }
            ]
        }

        # 2024年3月は31日まであるので、31回呼ばれる
        # テストでは最初の2日分だけモックする
        with patch.object(adapter.client, "get_document_list") as mock_get_list:
            # 最初の2日間は異なるレスポンスを返し、残りの日は空のレスポンスを返す
            empty_response: dict[str, list[Any]] = {"results": []}
            mock_get_list.side_effect = (
                [mock_response_day1, mock_response_day2] + [empty_response] * 29
            )

            documents = adapter.list_available_documents(criteria)

            # 31回呼ばれる（3月の日数分）
            assert mock_get_list.call_count == 31
            # 最初の2日分のドキュメントが取得される
            assert len(documents) == 2

    def test_list_available_documents_with_empty_response(
        self, adapter: EdinetAdapter
    ) -> None:
        """空のレスポンスを処理できる"""
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.XBRL),
            timescope=TimeScope(year=2024, month=3, day=15),
        )

        mock_response: dict[str, list[Any]] = {"results": []}

        with patch.object(adapter.client, "get_document_list", return_value=mock_response):
            documents = adapter.list_available_documents(criteria)

            assert len(documents) == 0

    def test_list_available_documents_with_invalid_data(
        self, adapter: EdinetAdapter
    ) -> None:
        """無効なデータを除外する"""
        criteria = EdinetDocumentSearchCriteria(
            format_type=FormatType(enum=FormatTypeEnum.XBRL),
            timescope=TimeScope(year=2024, month=3, day=15),
        )

        mock_response = {
            "results": [
                {
                    "docID": "S100TEST1",
                    "docDescription": "有価証券報告書",
                    "docTypeCode": "120",
                    "secCode": "12345",
                    "submitDateTime": "invalid-date",  # 無効な日付
                    "xbrlFlag": "1",
                    "pdfFlag": "1",
                    "csvFlag": "0",
                }
            ]
        }

        with patch.object(adapter.client, "get_document_list", return_value=mock_response):
            documents = adapter.list_available_documents(criteria)

            # 無効なデータは除外される
            assert len(documents) == 0

    ########## download_document ##########
    def test_download_document_xbrl(self, adapter: EdinetAdapter) -> None:
        document_id = DocumentId(value="EDINET_S100TEST_XBRL")
        format_type = FormatType(enum=FormatTypeEnum.XBRL)
        expected_content = b"xbrl content"

        with patch.object(
            adapter.client, "get_document", return_value=expected_content
        ) as mock_get_doc:
            content = adapter.download_document(document_id, format_type)

            assert content == expected_content
            mock_get_doc.assert_called_once_with(docId="EDINET_S100TEST_XBRL", type=1)

    def test_download_document_pdf(self, adapter: EdinetAdapter) -> None:
        document_id = DocumentId(value="EDINET_S100TEST_PDF")
        format_type = FormatType(enum=FormatTypeEnum.PDF)
        expected_content = b"pdf content"

        with patch.object(
            adapter.client, "get_document", return_value=expected_content
        ) as mock_get_doc:
            content = adapter.download_document(document_id, format_type)

            assert content == expected_content
            mock_get_doc.assert_called_once_with(docId="EDINET_S100TEST_PDF", type=2)

    def test_download_document_csv(self, adapter: EdinetAdapter) -> None:
        document_id = DocumentId(value="EDINET_S100TEST_CSV")
        format_type = FormatType(enum=FormatTypeEnum.CSV)
        expected_content = b"csv content"

        with patch.object(
            adapter.client, "get_document", return_value=expected_content
        ) as mock_get_doc:
            content = adapter.download_document(document_id, format_type)

            assert content == expected_content
            mock_get_doc.assert_called_once_with(docId="EDINET_S100TEST_CSV", type=5)

    def test_download_document_unsupported_format(self, adapter: EdinetAdapter) -> None:
        document_id = DocumentId(value="EDINET_S100TEST_OTHER")
        format_type = FormatType(enum=FormatTypeEnum.OTHER)

        with pytest.raises(ValueError, match="Unsupported format type"):
            _ = adapter.download_document(document_id, format_type)

    ########## _generate_edinet_document_id ##########
    def test_generate_edinet_document_id(self) -> None:
        doc_id = "S100TEST"
        format_type = FormatType(enum=FormatTypeEnum.XBRL)

        document_id = EdinetAdapter._generate_edinet_document_id(doc_id, format_type)  # type: ignore[reportPrivateUsage]

        assert document_id.value == "EDINET_S100TEST_XBRL"

    def test_generate_edinet_document_id_with_different_formats(self) -> None:
        doc_id = "S100TEST"

        xbrl_id = EdinetAdapter._generate_edinet_document_id(  # type: ignore[reportPrivateUsage]
            doc_id, FormatType(enum=FormatTypeEnum.XBRL)
        )
        pdf_id = EdinetAdapter._generate_edinet_document_id(  # type: ignore[reportPrivateUsage]
            doc_id, FormatType(enum=FormatTypeEnum.PDF)
        )
        csv_id = EdinetAdapter._generate_edinet_document_id(  # type: ignore[reportPrivateUsage]
            doc_id, FormatType(enum=FormatTypeEnum.CSV)
        )

        assert xbrl_id.value == "EDINET_S100TEST_XBRL"
        assert pdf_id.value == "EDINET_S100TEST_PDF"
        assert csv_id.value == "EDINET_S100TEST_CSV"

    ########## _convert_to_document ##########
    def test_convert_to_document_success(
        self, adapter: EdinetAdapter, mock_edinet_document: dict[str, str]
    ) -> None:
        format_type = FormatType(enum=FormatTypeEnum.XBRL)
        document = adapter._convert_to_document(  # type: ignore[reportPrivateUsage,arg-type]
            mock_edinet_document, format_type  # type: ignore[arg-type]
        )

        assert document is not None
        assert document.document_id.value == "EDINET_S100TEST_XBRL"
        assert document.filing_name == "有価証券報告書"
        assert document.ticker.value == "12345"
        assert document.disclosure_type.enum == DisclosureTypeEnum.ANNUAL_REPORT
        assert document.disclosure_source.enum == DisclosureSourceEnum.EDINET
        assert document.disclosure_date.value == date(2024, 3, 15)
        assert document.filing_format.enum == FormatTypeEnum.XBRL

    def test_convert_to_document_returns_none_for_unsupported_format(
        self, adapter: EdinetAdapter, mock_edinet_document: dict[str, str]
    ) -> None:
        """書類が指定されたフォーマットに対応していない場合はNoneを返す"""
        # CSV非対応の書類
        format_type = FormatType(enum=FormatTypeEnum.CSV)
        document = adapter._convert_to_document(  # type: ignore[reportPrivateUsage,arg-type]
            mock_edinet_document, format_type  # type: ignore[arg-type]
        )

        assert document is None

    def test_convert_to_document_returns_none_for_unknown_disclosure_type(
        self, adapter: EdinetAdapter
    ) -> None:
        """未知の開示書類種別の場合はNoneを返す"""
        edinet_doc = {
            "docID": "S100TEST",
            "docDescription": "未知の書類",
            "docTypeCode": "999",  # 未知の書類コード
            "secCode": "12345",
            "submitDateTime": "2024-03-15 09:00",
            "xbrlFlag": "1",
            "pdfFlag": "1",
            "csvFlag": "0",
        }
        format_type = FormatType(enum=FormatTypeEnum.XBRL)

        document = adapter._convert_to_document(edinet_doc, format_type)  # type: ignore[reportPrivateUsage,arg-type]

        assert document is None

    def test_convert_to_document_handles_missing_fields(
        self, adapter: EdinetAdapter
    ) -> None:
        """オプションフィールドが欠落している場合でもドキュメントを生成できる"""
        edinet_doc = {
            "docID": "S100TEST",
            # "docDescription": None,  # 欠落
            # "secCode": None,  # 欠落
            "docTypeCode": "120",
            "submitDateTime": "2024-03-15 09:00",
            "xbrlFlag": "1",
            "pdfFlag": "1",
            "csvFlag": "0",
        }
        format_type = FormatType(enum=FormatTypeEnum.XBRL)

        document = adapter._convert_to_document(edinet_doc, format_type)  # type: ignore[reportPrivateUsage,arg-type]

        assert document is not None
        assert document.filing_name == ""
        assert document.ticker.value == ""

    def test_convert_to_document_handles_invalid_date(
        self, adapter: EdinetAdapter
    ) -> None:
        """無効な日付の場合はNoneを返す"""
        edinet_doc = {
            "docID": "S100TEST",
            "docDescription": "有価証券報告書",
            "docTypeCode": "120",
            "secCode": "12345",
            "submitDateTime": "invalid-date",
            "xbrlFlag": "1",
            "pdfFlag": "1",
            "csvFlag": "0",
        }
        format_type = FormatType(enum=FormatTypeEnum.XBRL)

        document = adapter._convert_to_document(edinet_doc, format_type)  # type: ignore[reportPrivateUsage,arg-type]

        assert document is None

    ########## convert_to_edinet_format_type ##########
    def test_convert_to_edinet_format_type_xbrl(self, adapter: EdinetAdapter) -> None:
        format_type = FormatType(enum=FormatTypeEnum.XBRL)
        edinet_type = adapter.convert_to_edinet_format_type(format_type)
        assert edinet_type == 1

    def test_convert_to_edinet_format_type_pdf(self, adapter: EdinetAdapter) -> None:
        format_type = FormatType(enum=FormatTypeEnum.PDF)
        edinet_type = adapter.convert_to_edinet_format_type(format_type)
        assert edinet_type == 2

    def test_convert_to_edinet_format_type_csv(self, adapter: EdinetAdapter) -> None:
        format_type = FormatType(enum=FormatTypeEnum.CSV)
        edinet_type = adapter.convert_to_edinet_format_type(format_type)
        assert edinet_type == 5

    def test_convert_to_edinet_format_type_other(self, adapter: EdinetAdapter) -> None:
        format_type = FormatType(enum=FormatTypeEnum.OTHER)
        edinet_type = adapter.convert_to_edinet_format_type(format_type)
        assert edinet_type is None

    ########## _map_disclosure_type ##########
    def test_map_disclosure_type_annual_report(self, adapter: EdinetAdapter) -> None:
        disclosure_type = adapter._map_disclosure_type("120")  # type: ignore[reportPrivateUsage]
        assert disclosure_type is not None
        assert disclosure_type.enum == DisclosureTypeEnum.ANNUAL_REPORT

    def test_map_disclosure_type_quarterly_report(self, adapter: EdinetAdapter) -> None:
        disclosure_type = adapter._map_disclosure_type("140")  # type: ignore[reportPrivateUsage]
        assert disclosure_type is not None
        assert disclosure_type.enum == DisclosureTypeEnum.QUARTERLY_REPORT

    def test_map_disclosure_type_amended_reports(self, adapter: EdinetAdapter) -> None:
        amended_annual = adapter._map_disclosure_type("130")  # type: ignore[reportPrivateUsage]
        assert amended_annual is not None
        assert amended_annual.enum == DisclosureTypeEnum.AMENDED_ANNUAL_REPORT

        amended_quarterly = adapter._map_disclosure_type("150")  # type: ignore[reportPrivateUsage]
        assert amended_quarterly is not None
        assert amended_quarterly.enum == DisclosureTypeEnum.AMENDED_QUARTERLY_REPORT

    def test_map_disclosure_type_all_supported_codes(self, adapter: EdinetAdapter) -> None:
        """すべてのサポートされているコードをテスト"""
        mappings = {
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

        for code, expected_enum in mappings.items():
            disclosure_type = adapter._map_disclosure_type(code)  # type: ignore[reportPrivateUsage]
            assert disclosure_type is not None
            assert disclosure_type.enum == expected_enum

    def test_map_disclosure_type_unknown_code(self, adapter: EdinetAdapter) -> None:
        disclosure_type = adapter._map_disclosure_type("999")  # type: ignore[reportPrivateUsage]
        assert disclosure_type is None

    def test_map_disclosure_type_none(self, adapter: EdinetAdapter) -> None:
        disclosure_type = adapter._map_disclosure_type(None)  # type: ignore[reportPrivateUsage]
        assert disclosure_type is None

    ########## _map_format_type ##########
    def test_map_format_type_xbrl_only(self, adapter: EdinetAdapter) -> None:
        format_types = adapter._map_format_type("1", "0", "0")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 1
        assert format_types[0].enum == FormatTypeEnum.XBRL

    def test_map_format_type_pdf_only(self, adapter: EdinetAdapter) -> None:
        format_types = adapter._map_format_type("0", "1", "0")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 1
        assert format_types[0].enum == FormatTypeEnum.PDF

    def test_map_format_type_csv_only(self, adapter: EdinetAdapter) -> None:
        format_types = adapter._map_format_type("0", "0", "1")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 1
        assert format_types[0].enum == FormatTypeEnum.CSV

    def test_map_format_type_multiple_formats(self, adapter: EdinetAdapter) -> None:
        format_types = adapter._map_format_type("1", "1", "1")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 3
        assert FormatType(enum=FormatTypeEnum.XBRL) in format_types
        assert FormatType(enum=FormatTypeEnum.PDF) in format_types
        assert FormatType(enum=FormatTypeEnum.CSV) in format_types

    def test_map_format_type_xbrl_and_pdf(self, adapter: EdinetAdapter) -> None:
        format_types = adapter._map_format_type("1", "1", "0")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 2
        assert FormatType(enum=FormatTypeEnum.XBRL) in format_types
        assert FormatType(enum=FormatTypeEnum.PDF) in format_types

    def test_map_format_type_none_available(self, adapter: EdinetAdapter) -> None:
        """すべてのフォーマットが利用不可の場合、OTHERを返す"""
        format_types = adapter._map_format_type("0", "0", "0")  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 1
        assert format_types[0].enum == FormatTypeEnum.OTHER

    def test_map_format_type_with_none_values(self, adapter: EdinetAdapter) -> None:
        """Noneの値が渡された場合、OTHERを返す"""
        format_types = adapter._map_format_type(None, None, None)  # type: ignore[reportPrivateUsage]
        assert len(format_types) == 1
        assert format_types[0].enum == FormatTypeEnum.OTHER


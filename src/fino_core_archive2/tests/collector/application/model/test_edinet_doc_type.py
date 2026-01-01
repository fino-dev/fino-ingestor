"""Tests for EdinetDocTypeDto model."""

import pytest
from fino_core.application.model.edinet_doc_type_dto import EdinetDocTypeDto
from fino_core.domain.edinet import EdinetDocType


class TestEdinetDocTypeDto:
    """EdinetDocTypeDtoモデルのテスト"""

    def test_create_with_single_int(self) -> None:
        """単一のintでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(doc_types=120)
        assert input_model.doc_types == [120]

    def test_create_with_single_edinet_doc_type(self) -> None:
        """単一のEdinetDocTypeでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(doc_types=EdinetDocType.ANNUAL_REPORT)
        assert input_model.doc_types == [120]

    def test_create_with_list_of_int(self) -> None:
        """intのリストでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(doc_types=[120, 130, 140])
        assert input_model.doc_types == [120, 130, 140]

    def test_create_with_list_of_edinet_doc_type(self) -> None:
        """EdinetDocTypeのリストでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(
            doc_types=[
                EdinetDocType.ANNUAL_REPORT,
                EdinetDocType.AMENDED_ANNUAL_REPORT,
                EdinetDocType.QUARTERLY_REPORT,
            ]
        )
        assert input_model.doc_types == [120, 130, 140]

    def test_create_with_mixed_list(self) -> None:
        """intとEdinetDocTypeの混合リストでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(doc_types=[120, EdinetDocType.AMENDED_ANNUAL_REPORT, 140])
        assert input_model.doc_types == [120, 130, 140]

    def test_create_with_empty_list(self) -> None:
        """空のリストでEdinetDocTypeDtoを生成"""
        input_model = EdinetDocTypeDto(doc_types=[])
        assert input_model.doc_types == []

    def test_create_with_invalid_type_raises_error(self) -> None:
        """無効な型でEdinetDocTypeDtoを生成しようとするとエラー"""
        with pytest.raises(ValueError, match="Invalid document type code"):
            EdinetDocTypeDto(doc_types="invalid")

    def test_create_with_list_containing_invalid_type_raises_error(self) -> None:
        """無効な型を含むリストでEdinetDocTypeDtoを生成しようとするとエラー"""
        with pytest.raises(ValueError, match="Invalid document type code"):
            EdinetDocTypeDto(doc_types=[120, "invalid", 140])

    def test_to_domain_with_single_doc_type(self) -> None:
        """to_domainメソッドで単一のドキュメントタイプを変換"""
        input_model = EdinetDocTypeDto(doc_types=120)
        domain_types = input_model.to_domain()
        assert domain_types == [EdinetDocType.ANNUAL_REPORT]

    def test_to_domain_with_multiple_doc_types(self) -> None:
        """to_domainメソッドで複数のドキュメントタイプを変換"""
        input_model = EdinetDocTypeDto(doc_types=[120, 130, 140])
        domain_types = input_model.to_domain()
        assert domain_types == [
            EdinetDocType.ANNUAL_REPORT,
            EdinetDocType.AMENDED_ANNUAL_REPORT,
            EdinetDocType.QUARTERLY_REPORT,
        ]

    def test_to_domain_with_empty_list(self) -> None:
        """to_domainメソッドで空のリストを変換"""
        input_model = EdinetDocTypeDto(doc_types=[])
        domain_types = input_model.to_domain()
        assert domain_types == []

    def test_to_domain_with_invalid_int_raises_error(self) -> None:
        """to_domainメソッドで無効なintを変換しようとするとエラー"""
        # Pydanticのバリデーションを通すために、まず有効な値で作成してから
        # 直接無効な値を設定する必要がある
        input_model = EdinetDocTypeDto(doc_types=[120])
        input_model.doc_types = [999]  # 無効な値
        with pytest.raises(ValueError):
            input_model.to_domain()

from typing import Any, cast

from fino_core.domain.edinet import EdinetDocType
from pydantic import BaseModel, field_validator


class EdinetDocTypeDto(BaseModel):
    """Input model for EDINET document type."""

    doc_types: list[int]

    @field_validator("doc_types", mode="before")
    @classmethod
    def normalize_doc_type(cls, value: Any) -> list[int]:
        def to_int(v: Any) -> int:
            if isinstance(v, EdinetDocType):
                return v.value
            if isinstance(v, int):
                return v
            raise ValueError(f"Invalid document type code: {v}")

        if isinstance(value, (int, EdinetDocType)):
            return [to_int(value)]

        if isinstance(value, list):
            return [to_int(v) for v in cast(list[Any], value)]

        raise ValueError(f"Invalid document type code: {value}")

    # 一応取っておくサンプル例 aflterの場合はinstance methodとして定義できて、selfを使える。というのも、初期化後に実行される処理だから。
    # https://it-for-pharma.com/python-classmethod%E3%81%A8staticmethod%E3%82%92%E4%BD%BF%E3%81%86%E6%84%8F%E5%91%B3%E3%82%92%E8%80%83%E3%81%88%E3%82%8B
    # https://docs.pydantic.dev/latest/concepts/validators/#json-schema-and-field-validators
    # @field_validator("doc_type", mode="after")
    # def validate_doc_type_after(self, value: int | EdinetDocType) -> EdinetDocType:
    #     return EdinetDocType(value)

    def to_domain(self) -> list[EdinetDocType]:
        return [EdinetDocType(v) for v in self.doc_types]

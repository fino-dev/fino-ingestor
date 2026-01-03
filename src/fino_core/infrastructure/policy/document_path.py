import zipfile
from dataclasses import dataclass

from fino_core.domain.entity.document import Document


# Finoのデータレイクストレージのパス構造に合わせたポリシー
# @see: .cursor/rules/project.mdc#Storage Rules
@dataclass(frozen=True, slots=True)
class DocumentPathPolicy:
    """文書のパスを生成するポリシー"""

    document: Document
    as_zip: bool

    @property
    def folder(self) -> str:
        return f"{self.document.market.value}/{self.document.ticker.value}/{self.document.disclosure_type.value}"  # noqa: E501

    @property
    def filename(self) -> str:
        zip_suffix = ".zip" if self.as_zip else ""
        return f"{self.document.document_id.value}_{self.document.disclosure_date.value.isoformat()}_{self.document.filing_format.value}{zip_suffix}"  # noqa: E501

    @staticmethod
    def generate_path(document: Document, is_zip: bool = False) -> str:
        zip_suffix = ".zip" if is_zip else ""
        return f"{document.market.value}/{document.ticker.value}/{document.disclosure_type.value}/{document.document_id.value}_{document.disclosure_date.value.isoformat()}_{document.filing_format.value}{zip_suffix}"  # noqa: E501

    @staticmethod
    def is_zip(path: str) -> bool:
        return zipfile.is_zipfile(path)

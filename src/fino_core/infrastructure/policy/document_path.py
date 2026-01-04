import zipfile
from dataclasses import dataclass
from pathlib import Path

from fino_core.domain.entity.document import Document


# Finoのデータレイクストレージのパス構造に合わせたポリシー
# @see: .cursor/rules/project.mdc#Storage Rules
@dataclass(frozen=True, slots=True)
class DocumentPathPolicy:
    """文書のパスを生成するポリシー"""

    @staticmethod
    def generate_path(document: Document, is_zip: bool = False) -> str:
        zip_suffix = ".zip" if is_zip else ""
        return f"{document.disclosure_source.value}/{document.ticker.value}/{document.disclosure_type.value}/{document.document_id.value}_{document.disclosure_date.value.isoformat()}_{document.filing_format.value}{zip_suffix}"  # noqa: E501

    @staticmethod
    def is_zip(file_path: Path) -> bool:
        return zipfile.is_zipfile(file_path)

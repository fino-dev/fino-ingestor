from dataclasses import dataclass
from datetime import date
from typing import Optional

from fino_core.collector.domain.repository.document_source import DocumentSourceCriteria
from fino_core.collector.domain.value import DocumentType


@dataclass(frozen=True)
class EdinetCriteria(DocumentSourceCriteria):
    """EDINET固有の文書取得条件

    EDINET APIの特性に基づいた条件を定義します。
    他のデータソース（TDnetなど）とは異なる条件構造を持ちます。
    """

    date: date
    """取得する日付（必須）"""

    doc_types: Optional[list[DocumentType]] = None
    """取得する文書タイプのフィルタ（オプション）

    Noneの場合はすべての文書タイプを取得します。
    """

    with_docs: bool = False
    """メタデータと一緒に文書本体も取得するかどうか

    EDINET APIのtypeパラメータに対応します。
    False: メタデータのみ（type=1）
    True: メタデータと文書本体（type=2）
    """

"""
Fino Ingestorの基底例外クラス
"""

from typing import Any


class FinoIngestorError(Exception):
    """
    Fino Ingestorシステム全体の基底例外クラス

    全てのカスタム例外はこのクラスを継承します。
    これにより、システムレベルで統一的なエラーハンドリングが可能になります。
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message

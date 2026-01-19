"""
開示ソース（EDINET、SEC EDGAR等）に関連する例外
"""

from typing import Any

from fino_ingestor.domain.exception.base import FinoIngestorError


class DisclosureSourceError(FinoIngestorError):
    """
    開示ソースに関連する例外の基底クラス

    EDINET、SEC EDGAR等の外部開示システムとの通信や
    データ取得時に発生するエラーを表現します。
    """

    pass


class DisclosureSourceConnectionError(DisclosureSourceError):
    """
    開示ソースへの接続エラー

    ネットワーク障害やタイムアウト等、
    開示ソースAPIへの接続自体が失敗した場合に発生します。
    """

    pass


class DisclosureSourceApiError(DisclosureSourceError):
    """
    開示ソースAPIからのエラーレスポンス

    APIが正常に応答したものの、エラーステータスや
    エラーメッセージを含むレスポンスを返した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if status_code is not None:
            details["status_code"] = status_code
        if api_error_code is not None:
            details["api_error_code"] = api_error_code

        super().__init__(message, details)
        self.status_code = status_code
        self.api_error_code = api_error_code


class DisclosureSourceInvalidResponseError(DisclosureSourceError):
    """
    開示ソースAPIからの不正なレスポンス

    APIからのレスポンスが期待される形式と異なる、
    または必須フィールドが欠損している場合に発生します。
    """

    def __init__(
        self,
        message: str,
        response_data: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if response_data is not None:
            details["response_data"] = response_data

        super().__init__(message, details)
        self.response_data = response_data


class DisclosureSourceRateLimitError(DisclosureSourceError):
    """
    開示ソースAPIのレート制限エラー

    APIの呼び出し回数制限に達した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if retry_after is not None:
            details["retry_after"] = retry_after

        super().__init__(message, details)
        self.retry_after = retry_after

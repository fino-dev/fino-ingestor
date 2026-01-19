from typing import Literal, Optional

from fino_ingestor.application.input.collect_document import CollectDocumentInput
from fino_ingestor.application.input.list_document import ListDocumentInput
from fino_ingestor.application.interactor.collect_document import CollectDocumentUseCase
from fino_ingestor.application.interactor.list_document import ListDocumentUseCase
from fino_ingestor.domain.entity.document import Document
from fino_ingestor.domain.exception.disclosure_source import (
    DisclosureSourceApiError,
    DisclosureSourceConnectionError,
    DisclosureSourceError,
    DisclosureSourceInvalidResponseError,
    DisclosureSourceRateLimitError,
    FinoIngestorError,
)
from fino_ingestor.domain.value.format_type import FormatType, FormatTypeEnum
from fino_ingestor.infrastructure.adapter.disclosure_source.edinet import (
    EdinetDocumentSearchCriteria,
)
from fino_ingestor.infrastructure.factory.disclosure_source import (
    create_disclosure_source,
)
from fino_ingestor.infrastructure.factory.storage import create_storage
from fino_ingestor.infrastructure.repository.document import DocumentRepositoryImpl
from fino_ingestor.interface.config.disclosure import EdinetConfig
from fino_ingestor.interface.config.storage import LocalStorageConfig, S3StorageConfig
from fino_ingestor.util.timescope import TimeScope


class DocumentCollector:
    def __init__(
        self,
        disclosure_config: EdinetConfig,
        storage_config: LocalStorageConfig | S3StorageConfig,
    ) -> None:
        storage = create_storage(storage_config)
        self._document_repository = DocumentRepositoryImpl(storage)
        self._disclosure_source = create_disclosure_source(disclosure_config)

    def list_document(
        self,
        timescope: TimeScope,
        format_type: Optional[FormatTypeEnum] = FormatTypeEnum.XBRL,
    ) -> dict[
        Literal["available_document_list", "stored_document_list"], list[Document]
    ]:
        """
        指定された期間の書類一覧を取得します

        Args:
            timescope: 取得対象期間
            format_type: 書類フォーマット形式（デフォルト: XBRL）

        Returns:
            取得可能な書類と保存済み書類のリスト

        Raises:
            ValueError: format_typeがNoneの場合
            DisclosureSourceConnectionError: 開示ソースへの接続に失敗した場合
            DisclosureSourceApiError: 開示ソースAPIがエラーを返した場合
            DisclosureSourceInvalidResponseError: APIレスポンスが不正な場合
            DisclosureSourceRateLimitError: APIのレート制限に達した場合
            FinoIngestorError: その他のシステムエラー
        """
        # validation
        if format_type is None:
            raise ValueError(
                "format_type must not None. please specify format_type or use default value (XBRL)"
            )

        try:
            usecase = ListDocumentUseCase(self._document_repository)

            criteria = EdinetDocumentSearchCriteria(
                format_type=FormatType(enum=format_type),
                timescope=timescope,
            )
            input = ListDocumentInput(
                disclosure_source=self._disclosure_source, criteria=criteria
            )

            output = usecase.execute(input)
            return {
                "available_document_list": output.available_document_list,
                "stored_document_list": output.stored_document_list,
            }
        except DisclosureSourceConnectionError as e:
            # 接続エラーの場合、詳細情報を含めて再度投げる
            raise DisclosureSourceConnectionError(
                message=f"開示ソースへの接続に失敗しました。ネットワーク接続を確認してください。\n詳細: {e.message}",
                details=e.details,
            ) from e
        except DisclosureSourceApiError as e:
            # APIエラーの場合、ユーザーフレンドリーなメッセージに変換
            if e.status_code == 400:
                raise DisclosureSourceApiError(
                    message=f"リクエストパラメータが不正です。timescope={timescope}を確認してください。\n詳細: {e.message}",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
            elif e.status_code == 401 or e.status_code == 403:
                raise DisclosureSourceApiError(
                    message="APIキーが無効です。設定を確認してください。",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
            else:
                raise DisclosureSourceApiError(
                    message=f"開示ソースAPIがエラーを返しました。\n詳細: {e.message}",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
        except DisclosureSourceInvalidResponseError as e:
            # 不正なレスポンスの場合
            raise DisclosureSourceInvalidResponseError(
                message=f"開示ソースAPIから不正なレスポンスを受信しました。APIの仕様が変更されている可能性があります。\n詳細: {e.message}",
                response_data=e.response_data,
                details=e.details,
            ) from e
        except DisclosureSourceRateLimitError as e:
            # レート制限エラーの場合
            retry_msg = (
                f"{e.retry_after}秒後に再試行してください。"
                if e.retry_after
                else "しばらくしてから再試行してください。"
            )
            raise DisclosureSourceRateLimitError(
                message=f"APIのレート制限に達しました。{retry_msg}\n詳細: {e.message}",
                retry_after=e.retry_after,
                details=e.details,
            ) from e
        except DisclosureSourceError as e:
            # その他の開示ソースエラー
            raise DisclosureSourceError(
                message=f"開示ソースとの通信中にエラーが発生しました。\n詳細: {e.message}",
                details=e.details,
            ) from e
        except FinoIngestorError:
            # システム全体のエラー
            raise
        except Exception as e:
            # 予期しないエラー
            raise FinoIngestorError(
                message=f"予期しないエラーが発生しました: {str(e)}",
                details={"error_type": type(e).__name__},
            ) from e

    def collect_document(
        self,
        timescope: TimeScope,
        format_type: Optional[FormatTypeEnum] = FormatTypeEnum.XBRL,
    ) -> dict[Literal["collected_document_list"], list[Document]]:
        """
        指定された期間の書類を収集してストレージに保存します

        Args:
            timescope: 収集対象期間
            format_type: 書類フォーマット形式（デフォルト: XBRL）

        Returns:
            収集した書類のリスト

        Raises:
            ValueError: format_typeがNoneの場合
            DisclosureSourceConnectionError: 開示ソースへの接続に失敗した場合
            DisclosureSourceApiError: 開示ソースAPIがエラーを返した場合
            DisclosureSourceInvalidResponseError: APIレスポンスが不正な場合
            DisclosureSourceRateLimitError: APIのレート制限に達した場合
            FinoIngestorError: その他のシステムエラー
        """
        # validation
        if format_type is None:
            raise ValueError(
                "format_type must not None. please specify format_type or use default value (XBRL)"
            )

        try:
            usecase = CollectDocumentUseCase(self._document_repository)

            criteria = EdinetDocumentSearchCriteria(
                format_type=FormatType(enum=format_type),
                timescope=timescope,
            )

            input = CollectDocumentInput(
                disclosure_source=self._disclosure_source, criteria=criteria
            )

            output = usecase.execute(input)

            return {"collected_document_list": output.collected_document_list}
        except DisclosureSourceConnectionError as e:
            # 接続エラーの場合、詳細情報を含めて再度投げる
            raise DisclosureSourceConnectionError(
                message=f"開示ソースへの接続に失敗しました。ネットワーク接続を確認してください。\n詳細: {e.message}",
                details=e.details,
            ) from e
        except DisclosureSourceApiError as e:
            # APIエラーの場合、ユーザーフレンドリーなメッセージに変換
            if e.status_code == 400:
                raise DisclosureSourceApiError(
                    message=f"リクエストパラメータが不正です。timescope={timescope}を確認してください。\n詳細: {e.message}",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
            elif e.status_code == 401 or e.status_code == 403:
                raise DisclosureSourceApiError(
                    message="APIキーが無効です。設定を確認してください。",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
            else:
                raise DisclosureSourceApiError(
                    message=f"開示ソースAPIがエラーを返しました。\n詳細: {e.message}",
                    status_code=e.status_code,
                    api_error_code=e.api_error_code,
                    details=e.details,
                ) from e
        except DisclosureSourceInvalidResponseError as e:
            # 不正なレスポンスの場合
            raise DisclosureSourceInvalidResponseError(
                message=f"開示ソースAPIから不正なレスポンスを受信しました。APIの仕様が変更されている可能性があります。\n詳細: {e.message}",
                response_data=e.response_data,
                details=e.details,
            ) from e
        except DisclosureSourceRateLimitError as e:
            # レート制限エラーの場合
            retry_msg = (
                f"{e.retry_after}秒後に再試行してください。"
                if e.retry_after
                else "しばらくしてから再試行してください。"
            )
            raise DisclosureSourceRateLimitError(
                message=f"APIのレート制限に達しました。{retry_msg}\n詳細: {e.message}",
                retry_after=e.retry_after,
                details=e.details,
            ) from e
        except DisclosureSourceError as e:
            # その他の開示ソースエラー
            raise DisclosureSourceError(
                message=f"開示ソースとの通信中にエラーが発生しました。\n詳細: {e.message}",
                details=e.details,
            ) from e
        except FinoIngestorError:
            # システム全体のエラー
            raise
        except Exception as e:
            # 予期しないエラー
            raise FinoIngestorError(
                message=f"予期しないエラーが発生しました: {str(e)}",
                details={"error_type": type(e).__name__},
            ) from e

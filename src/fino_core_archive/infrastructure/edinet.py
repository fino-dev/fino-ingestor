from datetime import date
from typing import Any, override

import requests
from fino_core.domain.edinet import (
    BadRequestError,
    Edinet,
    EdinetDocType,
    GetDocumentResponse,
    GetDocumentResponseWithDocs,
    InternalServerError,
    InvalidAPIKeyError,
    ResourceNotFoundError,
    ResponseNot200Error,
)


def create_edinet(api_key: str) -> Edinet:
    """Create an Edinet adapter instance."""
    return EdinetAdapter(api_key=api_key)


class EdinetAdapter(Edinet):
    # EDINET API Version (今のところ2しかないけど)
    api_version: int = 2
    base_url: str = "https://api.edinet-fsa.go.jp/api/v{self.api_version}/"
    api_key: str

    def __init__(self, api_key: str) -> None:
        super().__init__(api_key=api_key)
        self.api_key = api_key

    def __request(self, endpoint: str, params: dict[str, Any]) -> requests.Response:
        """内部で使うrequestsメソッド、getリクエストのみ。"""

        params["Subscription-Key"] = self.api_key

        res = requests.get(
            url=self.base_url + endpoint,
            params=params,
            timeout=(3.0, 7.0),  # timeout: (connect timeout, read timeout)
        )

        if res.status_code == 200:
            return res
        elif res.status_code == 400:
            raise BadRequestError(
                res.status_code, res.text
            )  # 例外のargはすべて右の通り: int(statuscode), str(text)
        elif res.status_code == 401:
            raise InvalidAPIKeyError(res.status_code, res.text)
        elif res.status_code == 404:
            raise ResourceNotFoundError(res.status_code, res.text)
        elif res.status_code == 500:
            raise InternalServerError(res.status_code, res.text)
        else:
            raise ResponseNot200Error(res.status_code, res.text)

    @override
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        params = {
            "date": date.strftime("%Y-%m-%d"),
            "type": (2 if withdocs else 1),
        }

        response = self.__request(endpoint="documents.json", params=params)
        return response.json()

    @override
    def get_document(self, doc_id: str, doc_type: EdinetDocType) -> bytes:
        response = self.__request(endpoint=f"documents/{doc_id}", params={"type": doc_type.value})

        return response.content

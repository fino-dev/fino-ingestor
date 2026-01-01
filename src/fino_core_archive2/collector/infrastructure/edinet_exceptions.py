"""EDINET API specific exceptions.

These exceptions are infrastructure concerns and should not appear in domain or application layers.
"""


class EdinetAPIError(Exception):
    """Base exception for EDINET API errors"""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"EDINET API error {status_code}: {message}")


class BadRequestError(EdinetAPIError):
    """400 Bad Request - Invalid request parameters"""

    pass


class InvalidAPIKeyError(EdinetAPIError):
    """401 Unauthorized - Invalid API key"""

    pass


class ResourceNotFoundError(EdinetAPIError):
    """404 Not Found - Resource not found"""

    pass


class InternalServerError(EdinetAPIError):
    """500 Internal Server Error - EDINET server error"""

    pass


class ResponseNot200Error(EdinetAPIError):
    """Unexpected HTTP status code (not 200)"""

    pass


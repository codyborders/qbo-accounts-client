"""Exception hierarchy for QuickBooks Online API errors."""

from __future__ import annotations

from typing import Any


class QBOError(Exception):
    """Base exception for all QBO API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        detail: str | None = None,
        error_code: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(message)


class AuthenticationError(QBOError):
    """Raised on 401 Unauthorized responses."""


class ForbiddenError(QBOError):
    """Raised on 403 Forbidden responses."""


class NotFoundError(QBOError):
    """Raised on 404 Not Found responses."""


class ValidationError(QBOError):
    """Raised on 400 Bad Request responses (QBO ValidationFault)."""


class RateLimitError(QBOError):
    """Raised on 429 Too Many Requests responses."""


class ServerError(QBOError):
    """Raised on 5xx server error responses."""


_STATUS_MAP: dict[int, type[QBOError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
}


def map_status_to_exception(status_code: int, body: dict[str, Any] | None = None) -> QBOError:
    """Parse a QBO error response and return the appropriate exception.

    QBO error format::

        {
            "Fault": {
                "Error": [{"Message": "...", "Detail": "...", "code": "..."}],
                "type": "ValidationFault"
            }
        }
    """
    message = f"HTTP {status_code}"
    detail = None
    error_code = None

    if body and "Fault" in body:
        fault = body["Fault"]
        errors = fault.get("Error", [])
        if isinstance(errors, dict):
            errors = [errors]
        if errors:
            first = errors[0]
            message = first.get("Message", message)
            detail = first.get("Detail")
            error_code = first.get("code")

    if status_code >= 500:
        exc_cls = ServerError
    else:
        exc_cls = _STATUS_MAP.get(status_code, QBOError)

    return exc_cls(
        message=message,
        status_code=status_code,
        detail=detail,
        error_code=error_code,
    )

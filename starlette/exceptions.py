import http
import typing
import warnings


class HTTPException(Exception):  # type: ignore[type-arg]  # noqa: E501
    def __init__(  # type: ignore[attr-defined]  # noqa: E501
        self, status_code: typing.Union[int, str] = "500 Internal Server Error", detail: typing.Any = ""
    ):
        self.status_code = status_code
        self.detail = detail


class UNAUTHORIZED(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "401 Unauthorized"


class FORBIDDEN(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "403 Forbidden"


class NOT_FOUND(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "404 Not Found"


class METHOD_NOT_ALLOWED(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "405 Method Not Allowed"


class REDIRECT_SEE_OTHER(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "303 See Other"


class UNPROCESSABLE_ENTITY(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "422 Unprocessable Entity"


class TOO_MANY_REQUESTS(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "429 Too Many Requests"


class CLIENT_CLOSED_REQUEST(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "499 Client Closed Request"


class SERVER_ERROR(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "500 Internal Server Error"


class SERVICE_UNAVAILABLE(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "503 Service Unavailable"


class NOT_IMPLEMENTED(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "501 Not Implemented"


class BAD_GATEWAY(HTTPException):  # type: ignore[type-arg]  # noqa: E501
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = "502 Bad Gateway"

__all__ = ("HTTPException", "WebSocketException")


class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class WebSocketException(Exception):
    def __init__(self, code: int, reason: str | None = None) -> None:
        self.code = code
        self.reason = reason or ""

    def __str__(self) -> str:
        return f"{self.code}: {self.reason}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(code={self.code!r}, reason={self.reason!r})"


__deprecated__ = "ExceptionMiddleware"


def __getattr__(name: str) -> typing.Any:  # pragma: no cover
    if name == __deprecated__:
        from starlette.middleware.exceptions import ExceptionMiddleware

        warnings.warn(
            f"{__deprecated__} is deprecated on `starlette.exceptions`. "
            f"Import it from `starlette.middleware.exceptions` instead.",
            category=DeprecationWarning,
            stacklevel=3,
        )
        return ExceptionMiddleware
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(__all__) + [__deprecated__])  # pragma: no cover

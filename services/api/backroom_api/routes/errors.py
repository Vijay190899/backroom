"""The API's error shape: `{"error": {"code": ..., "message": ...}}` (contracts/api.py)."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backroom_api.contracts.api import ApiError, ErrorResponse

_CODES = {400: "bad_request", 404: "not_found", 409: "conflict", 503: "unavailable"}


class ApiProblem(HTTPException):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(status_code=status, detail=message)
        self.code = code


def body(code: str, message: str) -> dict[str, object]:
    return ErrorResponse(error=ApiError(code=code, message=message)).model_dump()


def install(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        code = getattr(exc, "code", None) or _CODES.get(exc.status_code, "error")
        return JSONResponse(body(code, str(exc.detail)), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def invalid(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0] if exc.errors() else {}
        where = ".".join(str(p) for p in first.get("loc", ()))
        return JSONResponse(
            body("invalid_request", f"{where}: {first.get('msg', 'invalid')}"), status_code=422
        )

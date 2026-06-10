from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.exceptions.errors import AppError, ConflictError, NotFoundError, UnauthorizedError

_STATUS_BY_ERROR: list[tuple[type[AppError], int]] = [
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
    (UnauthorizedError, status.HTTP_401_UNAUTHORIZED),
]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        for error_type, status_code in _STATUS_BY_ERROR:
            if isinstance(exc, error_type):
                headers = (
                    {"WWW-Authenticate": "Bearer"}
                    if status_code == status.HTTP_401_UNAUTHORIZED
                    else None
                )
                return JSONResponse(
                    status_code=status_code, content={"detail": exc.message}, headers=headers
                )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
        )

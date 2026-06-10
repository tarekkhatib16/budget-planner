from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.exceptions.errors import AppError, ConflictError, NotFoundError

_STATUS_BY_ERROR: list[tuple[type[AppError], int]] = [
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        for error_type, status_code in _STATUS_BY_ERROR:
            if isinstance(exc, error_type):
                return JSONResponse(status_code=status_code, content={"detail": exc.message})
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
        )

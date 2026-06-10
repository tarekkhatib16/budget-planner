"""Application-level exceptions.

Services raise these instead of HTTPException so business logic stays
independent of FastAPI; handlers.py maps them to HTTP responses at the edge.
"""


class AppError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass

"""Resolves the Bearer token on a request to a User, or raises 401.

Any route (or service provider) that depends on CurrentUser is therefore
protected: unauthenticated requests never reach the handler.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.core.config import get_settings
from api.core.security import decode_access_token
from api.dependencies.database import DbSession
from api.exceptions.errors import UnauthorizedError
from api.models import User
from api.repositories.user_repository import UserRepository

# auto_error=False so a missing header raises our UnauthorizedError (handled
# uniformly by the exception handlers) instead of FastAPI's default 403.
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: DbSession,
) -> User:
    if credentials is None:
        raise UnauthorizedError("Not authenticated")
    user_id = decode_access_token(credentials.credentials, get_settings())
    if user_id is None:
        raise UnauthorizedError("Invalid or expired token")
    user = UserRepository(db).get(user_id)
    if user is None:
        raise UnauthorizedError("Account no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

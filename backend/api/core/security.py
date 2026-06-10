"""Password hashing and JWT creation/verification.

bcrypt embeds a per-password random salt in the hash, so equal passwords
produce different hashes and rainbow tables are useless. JWTs are signed
(HS256) with the app secret: the server can verify it issued a token
without storing sessions anywhere.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from api.core.config import Settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=settings.access_token_expire_days),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, settings: Settings) -> int | None:
    """The user id inside a valid token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None

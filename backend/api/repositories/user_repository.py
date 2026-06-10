from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.scalars(stmt).first()

    def add(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user

from api.core.config import Settings
from api.core.security import create_access_token, hash_password, verify_password
from api.exceptions.errors import ConflictError, UnauthorizedError
from api.models import User
from api.repositories.category_repository import CategoryRepository
from api.repositories.user_repository import UserRepository
from api.schemas.auth import LoginRequest, RegisterRequest
from api.shared.default_categories import create_default_categories


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        categories: CategoryRepository,
        settings: Settings,
    ) -> None:
        self._users = users
        self._categories = categories
        self._settings = settings

    def register(self, data: RegisterRequest) -> tuple[User, str]:
        email = data.email.lower()
        if self._users.find_by_email(email):
            raise ConflictError("An account with this email already exists")
        user = self._users.add(User(email=email, password_hash=hash_password(data.password)))
        # New accounts start with the spreadsheet's category layout instead of
        # an empty grid.
        create_default_categories(self._categories, user.id)
        return user, create_access_token(user.id, self._settings)

    def login(self, data: LoginRequest) -> tuple[User, str]:
        user = self._users.find_by_email(data.email.lower())
        # Same error whether the email or the password was wrong, so the
        # endpoint can't be used to probe which emails have accounts.
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")
        return user, create_access_token(user.id, self._settings)

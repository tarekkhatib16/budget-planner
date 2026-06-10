from fastapi import APIRouter, status

from api.dependencies.auth import CurrentUser
from api.dependencies.services import AuthServiceDep
from api.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, service: AuthServiceDep):
    user, token = service.register(payload)
    return AuthResponse(token=token, user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, service: AuthServiceDep):
    user, token = service.login(payload)
    return AuthResponse(token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user

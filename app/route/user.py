from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.database import AsyncSessionDep
from app.models.user import User, UserCreate, UserPublic
from app.models.token import Token
from app.security import (
    get_current_user,
    verify_password,
    get_password_hash,
    create_access_token,
)

router = APIRouter(prefix="/api")

@router.post("/register", response_model=Token)
async def register(
    session: AsyncSessionDep,
    user: UserCreate
):
    db_user = await User.get_by_name(session, user.name)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_obj = User(
        name=user.name,
        password=hashed_password,
    )
    user_obj = await User.add(session, user_obj)

    access_token = create_access_token(data={"sub": user_obj.name})
    return Token(access_token=access_token)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized", headers: dict | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers
        )

unauthorized = UnauthorizedException(
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.post("/login", response_model=Token)
async def login(
    session: AsyncSessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await User.get_by_name(session, form_data.username)
    if not user:
        raise unauthorized
    
    if not verify_password(form_data.password, user.password):
        raise unauthorized
    
    access_token = create_access_token(data={"sub": user.name})
    return Token(access_token=access_token)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@router.get("/profile")
async def profile(current_user: User = Depends(get_current_user)):
    return UserPublic(
        id=current_user.id,
        name=current_user.name,
        balance=f"{current_user.total_balance:.2f}"
    )

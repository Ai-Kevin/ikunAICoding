from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.models import User
from app.schemas.schemas import LoginRequest, LoginResponse, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.username == payload.username) | (User.email == payload.username)
        )
        .first()
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误",
        )
    token = create_access_token(subject=user.username)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户")
def me(current_user: User = Depends(get_current_user)):
    return current_user

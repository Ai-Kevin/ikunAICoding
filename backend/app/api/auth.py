import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.models import LoginRecord, User
from app.schemas.schemas import (
    LoginRecordListOut,
    LoginRecordOut,
    LoginRequest,
    LoginResponse,
    UserOut,
)
from app.utils.client_info import format_location, get_client_ip, parse_user_agent

router = APIRouter(prefix="/auth", tags=["认证"])

AVATAR_DIR = Path(__file__).resolve().parents[2] / "uploads" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_AVATAR_SIZE = 2 * 1024 * 1024


def _record_to_out(record: LoginRecord, current_session_id: str | None) -> LoginRecordOut:
    return LoginRecordOut(
        id=record.id,
        device=record.device,
        title=record.title,
        time=record.created_at,
        location=record.location,
        ip=record.ip,
        current=bool(current_session_id and record.session_id == current_session_id),
    )


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
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

    session_id = uuid.uuid4().hex
    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    device, title = parse_user_agent(user_agent)

    db.add(
        LoginRecord(
            user_id=user.id,
            session_id=session_id,
            device=device,
            title=title,
            ip=ip,
            location=format_location(ip),
            user_agent=user_agent[:512],
        )
    )
    db.commit()

    token = create_access_token(subject=user.username)
    return LoginResponse(
        token=token,
        user=UserOut.model_validate(user),
        session_id=session_id,
    )


@router.get("/me", response_model=UserOut, summary="获取当前用户")
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/login-records", response_model=LoginRecordListOut, summary="最近登录记录")
def login_records(
    limit: int = 10,
    offset: int = 0,
    session_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 50))
    offset = max(0, offset)

    query = (
        db.query(LoginRecord)
        .filter(LoginRecord.user_id == current_user.id)
        .order_by(LoginRecord.created_at.desc())
    )
    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return LoginRecordListOut(
        items=[_record_to_out(record, session_id) for record in records],
        total=total,
    )


@router.post("/avatar", response_model=UserOut, summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 JPG / PNG / WebP / GIF 格式的图片",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传文件为空",
        )
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件不能超过 2MB",
        )

    ext = ALLOWED_AVATAR_TYPES[content_type]
    filename = f"user_{current_user.id}{ext}"
    file_path = AVATAR_DIR / filename
    file_path.write_bytes(content)

    for old in AVATAR_DIR.glob(f"user_{current_user.id}.*"):
        if old.name != filename:
            old.unlink(missing_ok=True)

    avatar_url = f"{settings.API_V1_PREFIX}/static/avatars/{filename}"
    current_user.avatar = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit_logger import log_auth_event
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    def get_user_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(
        self,
        db: Session,
        user_id: UUID,
    ) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def _save_user(
        self,
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def register(
        self,
        db: Session,
        request: RegisterRequest,
    ) -> User:
        existing_user = self.get_user_by_email(
            db,
            request.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        role = (
            "admin"
            if settings.BOOTSTRAP_ADMIN_EMAIL
            and request.email == settings.BOOTSTRAP_ADMIN_EMAIL
            else "user"
        )

        user = User(
            email=request.email,
            name=request.name,
            hashed_password=hash_password(request.password),
            role=role,
        )

        saved_user = self._save_user(db, user)
        
        log_auth_event(
            action="register",
            user_id=str(saved_user.id),
            email=saved_user.email,
            role=saved_user.role,
        )

        return saved_user

    def login(
        self,
        db: Session,
        request: LoginRequest,
    ) -> TokenResponse:
        user = self.get_user_by_email(
            db,
            request.email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            request.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(user.id, user.role)
        
        log_auth_event(
            action="login",
            user_id=str(user.id),
            email=user.email,
        )
        
        return TokenResponse(
            access_token=token,
        )


auth_service = AuthService()

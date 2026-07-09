from datetime import datetime, timedelta, timezone
from uuid import UUID

from joserfc import jwt
from joserfc.jwk import OctKey
from joserfc.jwt import JWTClaimsRegistry
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

JWT_KEY = OctKey.import_key(settings.SECRET_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        password,
        hashed_password,
    )


def create_access_token(user_id: UUID, role: str = "user") -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    claims = {
        "sub": str(user_id),
        "role": role,
        "exp": int(expire.timestamp()),
    }

    header = {
        "alg": settings.JWT_ALGORITHM,
    }

    return jwt.encode(
        header=header,
        claims=claims,
        key=JWT_KEY,
    )


def verify_access_token(token: str) -> dict:
    token_obj = jwt.decode(
        token,
        JWT_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    registry = JWTClaimsRegistry(
        exp={"essential": True},
        sub={"essential": True},
    )

    registry.validate(token_obj.claims)

    return token_obj.claims

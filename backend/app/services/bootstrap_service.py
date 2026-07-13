from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


def bootstrap_admin(db: Session) -> None:
    email = settings.BOOTSTRAP_ADMIN_EMAIL.strip()

    if not email:
        return

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        print(f"[BOOTSTRAP] Admin email not found: {email}")
        return

    if user.role != "admin":
        user.role = "admin"
        db.commit()
        print(f"[BOOTSTRAP] Promoted {email} to admin.")

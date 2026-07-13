from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.user import User

logger = get_logger(__name__)

def bootstrap_admin(db: Session) -> None:
    email = settings.BOOTSTRAP_ADMIN_EMAIL.strip()

    if not email:
        return

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        logger.warning(f"[BOOTSTRAP] Admin email not found: {email}")
        return

    if user.role != "admin":
        user.role = "admin"
        db.commit()
        logger.info(f"[BOOTSTRAP] Promoted {email} to admin.")

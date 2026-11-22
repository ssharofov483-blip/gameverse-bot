import hmac
import hashlib
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


def verify_admin_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API Key talab qilinadi (Header: X-Admin-API-Key)"
        )
    if not hmac.compare_digest(api_key, settings.ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Noto'g'ri Admin API Key!"
        )
    return True


def is_telegram_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_TELEGRAM_IDS


def generate_idempotency_key(prefix: str = "tx") -> str:
    return f"{prefix}_{secrets.token_hex(16)}"

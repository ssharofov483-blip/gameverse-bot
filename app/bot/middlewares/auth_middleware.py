from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from app.core.database import async_session_factory
from app.repositories.user_repo import UserRepository


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        tg_user: TgUser = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            db_user, _ = await user_repo.get_or_create(
                telegram_id=tg_user.id,
                first_name=tg_user.first_name or "Hukmdor",
                username=tg_user.username,
                last_name=tg_user.last_name,
                language_code=tg_user.language_code or "uz"
            )
            await session.commit()

            if db_user.is_banned:
                # User is banned
                return None

            data["db_user"] = db_user

        return await handler(event, data)

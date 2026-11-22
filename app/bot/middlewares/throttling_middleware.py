import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from app.core.cache import cache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        last_req = await cache.get(key)
        now = time.time()

        if last_req:
            elapsed = now - float(last_req)
            if elapsed < self.rate_limit:
                if isinstance(event, CallbackQuery):
                    await event.answer("Juda tez harakat qildingiz! Biroz kuting.", show_alert=False)
                elif isinstance(event, Message):
                    await event.answer("Iltimos, buyruqlarni biroz sekinroq yuboring!")
                return None

        await cache.set(key, now, ex=2)
        return await handler(event, data)

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings
from app.core.database import init_db
from app.core.cache import cache
from app.api.admin_routes import admin_router

from app.bot.handlers.start import start_router
from app.bot.handlers.kingdom import kingdom_router
from app.bot.handlers.buildings import buildings_router
from app.bot.handlers.troops import troops_router
from app.bot.handlers.battle import battle_router
from app.bot.handlers.clan import clan_router
from app.bot.handlers.missions import missions_router
from app.bot.handlers.leaderboard import leaderboard_router
from app.bot.handlers.profile import profile_router

from app.bot.middlewares.auth_middleware import AuthMiddleware
from app.bot.middlewares.throttling_middleware import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gameverse")

dp = Dispatcher()

# Register Middlewares
dp.message.outer_middleware(AuthMiddleware())
dp.callback_query.outer_middleware(AuthMiddleware())
dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.4))

# Register Routers
dp.include_router(start_router)
dp.include_router(kingdom_router)
dp.include_router(buildings_router)
dp.include_router(troops_router)
dp.include_router(battle_router)
dp.include_router(clan_router)
dp.include_router(missions_router)
dp.include_router(leaderboard_router)
dp.include_router(profile_router)

bot_instance = None
bot_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_instance, bot_task
    logger.info("Initializing GAMEVERSE backend...")

    # 1. Database initialization
    await init_db()
    logger.info("Database schema initialized.")

    # 2. Cache connection
    await cache.connect()
    logger.info("Cache manager initialized.")

    # 3. Telegram Bot start (if token present)
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "your_bot_token_here":
        bot_instance = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info(f"Starting Telegram bot @{settings.BOT_USERNAME}...")
        bot_task = asyncio.create_task(dp.start_polling(bot_instance))
    else:
        logger.warning(
            "BOT_TOKEN is not set or empty. Bot polling is paused. "
            "Please configure BOT_TOKEN in .env to connect Telegram."
        )

    yield

    logger.info("Shutting down GAMEVERSE...")
    if bot_instance:
        await bot_instance.session.close()
    if bot_task:
        bot_task.cancel()
    await cache.close()


app = FastAPI(
    title="GAMEVERSE Admin API & Game Engine",
    version="1.0.0",
    description="Multiplayer Medieval Kingdom Strategy Game Backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "game": "GAMEVERSE",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "bot_configured": bool(settings.BOT_TOKEN and settings.BOT_TOKEN != "your_bot_token_here")
    }


async def run_bot_standalone():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_bot_token_here":
        logger.error("BOT_TOKEN is required in .env to run standalone bot!")
        return

    await init_db()
    await cache.connect()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    logger.info(f"GAMEVERSE Telegram Bot starting @{settings.BOT_USERNAME}...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await cache.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bot":
        asyncio.run(run_bot_standalone())
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)

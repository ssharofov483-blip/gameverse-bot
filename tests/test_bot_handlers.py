import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, User as TgUser, Chat
from app.bot.handlers.start import cmd_start
from app.bot.handlers.kingdom import view_kingdom
from app.bot.handlers.buildings import view_buildings
from app.bot.handlers.troops import view_troops
from app.bot.handlers.battle import view_battle_hub
from app.bot.handlers.clan import view_clan_hub
from app.bot.handlers.missions import view_missions
from app.bot.handlers.leaderboard import view_leaderboard
from app.bot.handlers.profile import view_profile, view_inventory
from app.core.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


def create_mock_message(user_id=12345, text="/start", first_name="Alisher"):
    msg = MagicMock(spec=Message)
    msg.from_user = MagicMock(spec=TgUser)
    msg.from_user.id = user_id
    msg.from_user.first_name = first_name
    msg.from_user.username = "alisher_dev"
    msg.from_user.last_name = None
    msg.from_user.language_code = "uz"
    msg.text = text
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = user_id
    msg.answer = AsyncMock()
    return msg


@pytest.mark.asyncio
async def test_cmd_start_handler(test_session):
    import time
    unique_id = int(time.time()) + 90000
    msg = create_mock_message(user_id=unique_id, text="/start")
    await cmd_start(msg)
    assert msg.answer.called
    call_args = msg.answer.call_args[0][0]
    assert "GAMEVERSE" in call_args
    assert "Xush kelibsiz" in call_args


@pytest.mark.asyncio
async def test_all_main_menu_handlers():
    msg = create_mock_message(user_id=88802, text="🏰 Mening qirolligim")

    # Start first to register user
    await cmd_start(msg)
    msg.answer.reset_mock()

    # Test Kingdom view
    await view_kingdom(msg)
    assert msg.answer.called
    assert "Resurslar ombori" in msg.answer.call_args[0][0]

    # Test Buildings view
    msg.answer.reset_mock()
    await view_buildings(msg)
    assert msg.answer.called
    assert "QIROLLIK BINOLARI" in msg.answer.call_args[0][0]

    # Test Troops view
    msg.answer.reset_mock()
    await view_troops(msg)
    assert msg.answer.called
    assert "QIROLLIK QO‘SHINI" in msg.answer.call_args[0][0]

    # Test Battle hub view
    msg.answer.reset_mock()
    await view_battle_hub(msg)
    assert msg.answer.called
    assert "JANG MAYDONI" in msg.answer.call_args[0][0]

    # Test Clan view
    msg.answer.reset_mock()
    await view_clan_hub(msg)
    assert msg.answer.called
    assert "KLAN" in msg.answer.call_args[0][0]

    # Test Missions view
    msg.answer.reset_mock()
    await view_missions(msg)
    assert msg.answer.called
    assert "KUNDALIK MISSIYALAR" in msg.answer.call_args[0][0]

    # Test Leaderboard view
    msg.answer.reset_mock()
    await view_leaderboard(msg)
    assert msg.answer.called
    assert "REYTINGI" in msg.answer.call_args[0][0]

    # Test Profile view
    msg.answer.reset_mock()
    await view_profile(msg)
    assert msg.answer.called
    assert "HUKMDOR PROFILI" in msg.answer.call_args[0][0]

    # Test Inventory view
    msg.answer.reset_mock()
    await view_inventory(msg)
    assert msg.answer.called
    assert "INVENTAR" in msg.answer.call_args[0][0]

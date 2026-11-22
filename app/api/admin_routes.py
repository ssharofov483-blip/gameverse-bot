from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_admin_key
from app.services.admin_service import AdminService
from app.repositories.battle_repo import BattleRepository

admin_router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])


@admin_router.get("/overview", dependencies=[Depends(verify_admin_key)])
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Tizimning umumiy statistikasi va o'yinchilar soni."""
    service = AdminService(db)
    return await service.get_overview()


@admin_router.get("/players", dependencies=[Depends(verify_admin_key)])
async def get_players(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Barcha ro'yxatdan o'tgan o'yinchilar ro'yxati."""
    service = AdminService(db)
    return await service.get_players(limit=limit, offset=offset)


@admin_router.post("/players/{user_id}/adjust-resources", dependencies=[Depends(verify_admin_key)])
async def adjust_resources(
    user_id: int,
    gold: int = Body(0),
    wood: int = Body(0),
    iron: int = Body(0),
    food: int = Body(0),
    reason: str = Body("Admin adjustment"),
    db: AsyncSession = Depends(get_db)
):
    """O'yinchining resurslarini boshqarish (qo'shish/ayirish)."""
    service = AdminService(db)
    try:
        return await service.adjust_player_resources(user_id, gold, wood, iron, food, reason)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@admin_router.get("/battles/recent", dependencies=[Depends(verify_admin_key)])
async def get_recent_battles(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """So'nggi janglar hisoboti."""
    repo = BattleRepository(db)
    battles = await repo.get_all(limit=limit)
    return battles

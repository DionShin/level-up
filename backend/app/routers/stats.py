from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.models import Stat
from app.schemas.schemas import StatResponse
from app.services.routine_service import calc_stat_score

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/", response_model=list[StatResponse])
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Stat).where(Stat.user_id == user_id))
    stats = result.scalars().all()
    response = []
    for stat in stats:
        score = await calc_stat_score(db, stat.id, user_id)
        response.append(StatResponse(id=stat.id, user_id=stat.user_id, name=stat.name, icon=stat.icon, color=stat.color, score=score))
    return response


@router.get("/{stat_id}", response_model=StatResponse)
async def get_stat(
    stat_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Stat).where(Stat.id == stat_id, Stat.user_id == user_id))
    stat = result.scalar_one_or_none()
    if not stat:
        raise HTTPException(status_code=404, detail="스탯을 찾을 수 없습니다.")
    score = await calc_stat_score(db, stat.id, user_id)
    return StatResponse(id=stat.id, user_id=stat.user_id, name=stat.name, icon=stat.icon, color=stat.color, score=score)

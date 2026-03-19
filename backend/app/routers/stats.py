from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.models import Stat
from app.schemas.schemas import StatCreate, StatResponse
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


@router.post("/", response_model=StatResponse, status_code=201)
async def create_stat(
    body: StatCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """새 스탯 추가 (최대 8개)."""
    result = await db.execute(select(Stat).where(Stat.user_id == user_id))
    existing = result.scalars().all()
    if len(existing) >= 8:
        raise HTTPException(status_code=400, detail="스탯은 최대 8개까지 추가할 수 있습니다.")
    stat = Stat(user_id=user_id, name=body.name, icon=body.icon, color=body.color)
    db.add(stat)
    await db.commit()
    await db.refresh(stat)
    return StatResponse(id=stat.id, user_id=stat.user_id, name=stat.name, icon=stat.icon, color=stat.color, score=0)


@router.delete("/{stat_id}", status_code=204)
async def delete_stat(
    stat_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """스탯 삭제 (최소 3개 유지)."""
    result = await db.execute(select(Stat).where(Stat.user_id == user_id))
    all_stats = result.scalars().all()
    if len(all_stats) <= 3:
        raise HTTPException(status_code=400, detail="스탯은 최소 3개 이상 유지해야 합니다.")
    stat = next((s for s in all_stats if s.id == stat_id), None)
    if not stat:
        raise HTTPException(status_code=404, detail="스탯을 찾을 수 없습니다.")
    await db.delete(stat)
    await db.commit()


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

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.models import GrowthHistory, Routine, Category
from app.schemas.schemas import HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/", response_model=list[HistoryResponse])
async def get_history(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """성장 히스토리 전체 조회 (최신순)."""
    result = await db.execute(
        select(GrowthHistory)
        .where(GrowthHistory.user_id == user_id)
        .order_by(GrowthHistory.created_at.desc())
    )
    events = result.scalars().all()

    response = []
    for event in events:
        routine_name = None
        stat_id = None

        # 루틴 이름과 stat_id를 조인 없이 개별 조회 (SQLite 호환)
        if event.routine_id:
            r_result = await db.execute(
                select(Routine, Category)
                .join(Category, Routine.category_id == Category.id)
                .where(Routine.id == event.routine_id)
            )
            row = r_result.first()
            if row:
                routine, category = row
                routine_name = routine.name
                stat_id = category.stat_id

        response.append(HistoryResponse(
            id=event.id,
            user_id=event.user_id,
            routine_id=event.routine_id,
            routine_name=routine_name,
            stat_id=stat_id,
            event_type=event.event_type,
            content=event.content,
            note=event.note,
            created_at=event.created_at,
        ))

    return response

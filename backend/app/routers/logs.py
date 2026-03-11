"""
루틴 O/X 체크 API.

파이썬 관점: upsert = INSERT OR UPDATE.
같은 날짜에 중복 로그를 방지하고 토글(O→X→O) 방식으로 동작.
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.models import Routine, RoutineLog, GrowthHistory
from app.schemas.schemas import LogToggleRequest, LogResponse
from app.services.routine_service import calc_streak, add_history_event

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/toggle", response_model=LogResponse)
async def toggle_log(body: LogToggleRequest, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """
    루틴 O/X 토글 (upsert 방식).
    이미 로그가 있으면 completed 값만 업데이트, 없으면 새로 생성.
    """
    result = await db.execute(
        select(RoutineLog).where(
            and_(
                RoutineLog.routine_id == body.routine_id,
                RoutineLog.user_id == user_id,
                RoutineLog.log_date == body.date,
            )
        )
    )
    log = result.scalar_one_or_none()

    if log:
        log.completed = body.completed
        if body.note:
            log.note = body.note
    else:
        log = RoutineLog(
            routine_id=body.routine_id,
            user_id=user_id,
            log_date=body.date,
            completed=body.completed,
            note=body.note,
        )
        db.add(log)

    await db.flush()

    # 21일 연속 달성 시 habit_formed 이벤트 자동 기록
    if body.completed:
        streak = await calc_streak(db, body.routine_id, user_id)
        if streak == 21:
            routine_result = await db.execute(select(Routine).where(Routine.id == body.routine_id))
            routine = routine_result.scalar_one_or_none()
            if routine:
                await add_history_event(
                    db,
                    user_id=user_id,
                    event_type="habit_formed",
                    content=f"습관 정착 성공! 21일 연속 달성 🏆",
                    routine_id=body.routine_id,
                )

    await db.commit()
    await db.refresh(log)
    return LogResponse(id=log.id, routine_id=log.routine_id, date=log.log_date, completed=log.completed, note=log.note)


@router.get("/{routine_id}", response_model=list[LogResponse])
async def get_logs(routine_id: str, days: int = 7, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """루틴의 최근 N일 로그 조회."""
    since = date.today() - timedelta(days=days - 1)
    result = await db.execute(
        select(RoutineLog).where(
            and_(
                RoutineLog.routine_id == routine_id,
                RoutineLog.user_id == user_id,
                RoutineLog.log_date >= since,
            )
        ).order_by(RoutineLog.log_date)
    )
    logs = result.scalars().all()
    return [LogResponse(id=l.id, routine_id=l.routine_id, date=l.log_date, completed=l.completed, note=l.note) for l in logs]

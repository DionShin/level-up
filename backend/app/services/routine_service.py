"""
비즈니스 로직 분리 레이어.

파이썬 관점: 라우터(views)에서 로직을 분리한 함수 모음.
DB 조작 + 계산 로직을 담당하며, 라우터는 단순히 이 함수를 호출만 함.
"""
from datetime import date, timedelta

from sqlalchemy import Integer, select, func, and_, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Routine, RoutineLog, GrowthHistory


async def calc_weekly_rate(db: AsyncSession, routine_id: str, user_id: str) -> float:
    """최근 7일 달성률 계산 (완료된 날 / 전체 기록된 날 * 100)."""
    seven_days_ago = date.today() - timedelta(days=6)

    result = await db.execute(
        select(
            func.count(RoutineLog.id).label("total"),
            func.sum(cast(RoutineLog.completed, Integer)).label("done"),
        ).where(
            and_(
                RoutineLog.routine_id == routine_id,
                RoutineLog.user_id == user_id,
                RoutineLog.log_date >= seven_days_ago,
            )
        )
    )
    row = result.one()
    total, done = row.total, row.done or 0
    if total == 0:
        return 0.0
    return round(done / total * 100, 1)


async def calc_streak(db: AsyncSession, routine_id: str, user_id: str) -> int:
    """오늘부터 역순으로 연속 달성일 계산."""
    result = await db.execute(
        select(RoutineLog.log_date, RoutineLog.completed)
        .where(
            and_(
                RoutineLog.routine_id == routine_id,
                RoutineLog.user_id == user_id,
                RoutineLog.completed == True,  # noqa: E712
            )
        )
        .order_by(RoutineLog.log_date.desc())
    )
    rows = result.fetchall()
    if not rows:
        return 0

    # 연속 날짜 체크: 오늘부터 하루씩 역산
    streak = 0
    expected = date.today()
    for row in rows:
        if row.log_date == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif row.log_date < expected:
            break   # 중간에 빠진 날 발견 → 종료
    return streak


async def calc_stat_score(db: AsyncSession, stat_id: str, user_id: str) -> float:
    """
    스탯 점수 = 해당 스탯 전체 루틴의 주간 달성률 평균.
    파이썬의 리스트 컴프리헨션 + 평균 계산과 동일한 로직.
    """
    from app.models.models import Category  # 순환 import 방지
    result = await db.execute(
        select(Routine).join(Category).where(
            and_(Category.stat_id == stat_id, Routine.user_id == user_id, Routine.is_active == True)  # noqa: E712
        )
    )
    routines = result.scalars().all()
    if not routines:
        return 0.0

    rates = [await calc_weekly_rate(db, r.id, user_id) for r in routines]
    return round(sum(rates) / len(rates), 1)


async def add_history_event(
    db: AsyncSession,
    user_id: str,
    event_type: str,
    content: str,
    routine_id: str | None = None,
    note: str | None = None,
) -> None:
    """성장 타임라인에 이벤트 기록."""
    event = GrowthHistory(
        user_id=user_id,
        routine_id=routine_id,
        event_type=event_type,
        content=content,
        note=note,
    )
    db.add(event)
    await db.flush()  # commit은 라우터에서 한 번에

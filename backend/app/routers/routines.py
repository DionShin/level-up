from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.models import Routine
from app.schemas.schemas import RoutineCreate, RoutineUpdate, RoutineResponse
from app.services.routine_service import calc_weekly_rate, calc_streak, add_history_event

router = APIRouter(prefix="/routines", tags=["routines"])


async def _build_response(db: AsyncSession, r: Routine, user_id: str) -> RoutineResponse:
    weekly_rate = await calc_weekly_rate(db, r.id, user_id)
    streak = await calc_streak(db, r.id, user_id)
    return RoutineResponse(
        id=r.id,
        category_id=r.category_id,
        user_id=r.user_id,
        name=r.name,
        description=r.description,
        frequency=r.frequency,
        days_of_week=r.days_of_week,
        notification_time=r.notification_time,
        is_active=r.is_active,
        is_forked=r.is_forked,
        original_author=r.original_author,
        weekly_rate=weekly_rate,
        streak=streak,
        created_at=r.created_at,
    )


@router.get("/by-category/{cat_id}", response_model=list[RoutineResponse])
async def get_routines_by_category(cat_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """카테고리에 속한 루틴 목록."""
    result = await db.execute(
        select(Routine).where(
            and_(Routine.category_id == cat_id, Routine.user_id == user_id, Routine.is_active == True)  # noqa: E712
        ).order_by(Routine.created_at)
    )
    routines = result.scalars().all()
    return [await _build_response(db, r, user_id) for r in routines]


@router.get("/today", response_model=list[RoutineResponse])
async def get_today_routines(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """오늘 해야 할 루틴 목록 (frequency 기반 필터링)."""
    from datetime import date
    today_weekday = date.today().weekday()  # 0=월 ~ 6=일 (Python 기준)
    # SQLite에서는 JSON 필드 내 검색이 어려우므로 전체 로드 후 Python에서 필터
    result = await db.execute(
        select(Routine).where(
            and_(Routine.user_id == user_id, Routine.is_active == True)  # noqa: E712
        )
    )
    all_routines = result.scalars().all()

    today_routines = []
    for r in all_routines:
        if r.frequency == "daily":
            today_routines.append(r)
        elif r.frequency == "alternate":
            # 생성일 기준 격일 계산
            delta = (date.today() - r.created_at.date()).days
            if delta % 2 == 0:
                today_routines.append(r)
        elif r.frequency == "weekdays" and r.days_of_week:
            # Python weekday: 0=월, SQLite에서는 0=일로 저장했으므로 변환 필요
            # 우리 데이터는 0=일 기준이므로 Python의 weekday()+1 % 7 = 0=일 기준
            day_sun_based = (today_weekday + 1) % 7  # Python Mon=0 → Sun=0 변환
            if day_sun_based in r.days_of_week:
                today_routines.append(r)

    return [await _build_response(db, r, user_id) for r in today_routines]


@router.post("/", response_model=RoutineResponse, status_code=201)
async def create_routine(body: RoutineCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """루틴 생성 + 히스토리 기록."""
    routine = Routine(
        category_id=body.category_id,
        user_id=user_id,
        name=body.name,
        description=body.description,
        frequency=body.frequency,
        days_of_week=body.days_of_week,
        notification_time=body.notification_time,
        is_forked=body.is_forked,
        original_routine_id=body.original_routine_id,
        original_author=body.original_author,
    )
    db.add(routine)
    await db.flush()  # ID 생성

    await add_history_event(
        db,
        user_id=user_id,
        event_type="routine_added",
        content=f"새 루틴 시작: '{body.name}'",
        routine_id=routine.id,
    )
    await db.commit()
    await db.refresh(routine)
    return await _build_response(db, routine, user_id)


@router.patch("/{routine_id}", response_model=RoutineResponse)
async def update_routine(routine_id: str, body: RoutineUpdate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """루틴 수정."""
    result = await db.execute(
        select(Routine).where(and_(Routine.id == routine_id, Routine.user_id == user_id))
    )
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="루틴을 찾을 수 없습니다.")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(routine, field, value)

    await db.commit()
    await db.refresh(routine)
    return await _build_response(db, routine, user_id)


@router.delete("/{routine_id}", status_code=204)
async def delete_routine(routine_id: str, note: str | None = None, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """루틴 삭제 + 히스토리 기록."""
    result = await db.execute(
        select(Routine).where(and_(Routine.id == routine_id, Routine.user_id == user_id))
    )
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="루틴을 찾을 수 없습니다.")

    await add_history_event(
        db,
        user_id=user_id,
        event_type="routine_deleted",
        content=f"루틴 삭제: '{routine.name}'",
        routine_id=routine.id,
        note=note,
    )
    await db.delete(routine)
    await db.commit()

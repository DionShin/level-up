from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, select, func, and_, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.models import Category, Routine, RoutineLog
from app.schemas.schemas import CategoryCreate, CategoryResponse
from app.services.routine_service import add_history_event

router = APIRouter(prefix="/categories", tags=["categories"])


async def _build_response(db: AsyncSession, cat: Category, user_id: str) -> CategoryResponse:
    """카테고리 응답 객체 조립 (루틴 수, 주간 달성률 계산 포함)."""
    from datetime import date, timedelta
    seven_days_ago = date.today() - timedelta(days=6)

    # 루틴 수
    r_count = await db.execute(
        select(func.count(Routine.id)).where(
            and_(Routine.category_id == cat.id, Routine.is_active == True)  # noqa: E712
        )
    )
    routine_count = r_count.scalar() or 0

    # 주간 달성률: 이 카테고리에 속한 모든 로그의 평균
    rate_result = await db.execute(
        select(
            func.count(RoutineLog.id).label("total"),
            func.sum(cast(RoutineLog.completed, Integer)).label("done"),
        )
        .join(Routine, RoutineLog.routine_id == Routine.id)
        .where(
            and_(
                Routine.category_id == cat.id,
                RoutineLog.user_id == user_id,
                RoutineLog.log_date >= seven_days_ago,
            )
        )
    )
    row = rate_result.one()
    total, done = row.total, row.done or 0
    weekly_rate = round(done / total * 100, 1) if total > 0 else 0.0

    return CategoryResponse(
        id=cat.id,
        stat_id=cat.stat_id,
        user_id=cat.user_id,
        name=cat.name,
        icon=cat.icon,
        description=cat.description,
        order_index=cat.order_index,
        routine_count=routine_count,
        weekly_rate=weekly_rate,
    )


@router.get("/by-stat/{stat_id}", response_model=list[CategoryResponse])
async def get_categories_by_stat(stat_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """특정 스탯의 카테고리 목록."""
    result = await db.execute(
        select(Category)
        .where(and_(Category.stat_id == stat_id, Category.user_id == user_id))
        .order_by(Category.order_index)
    )
    cats = result.scalars().all()
    return [await _build_response(db, c, user_id) for c in cats]


@router.get("/{cat_id}", response_model=CategoryResponse)
async def get_category(cat_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """카테고리 단건 조회."""
    result = await db.execute(
        select(Category).where(and_(Category.id == cat_id, Category.user_id == user_id))
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    return await _build_response(db, cat, user_id)


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """카테고리 생성."""
    # order_index: 같은 stat 내 최대값 + 1
    max_order = await db.execute(
        select(func.max(Category.order_index)).where(Category.stat_id == body.stat_id)
    )
    next_order = (max_order.scalar() or 0) + 1

    cat = Category(
        stat_id=body.stat_id,
        user_id=user_id,
        name=body.name,
        icon=body.icon,
        description=body.description,
        order_index=next_order,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return await _build_response(db, cat, user_id)


@router.delete("/{cat_id}", status_code=204)
async def delete_category(cat_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """카테고리 삭제 (하위 루틴 cascade 삭제)."""
    result = await db.execute(
        select(Category).where(and_(Category.id == cat_id, Category.user_id == user_id))
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    await db.delete(cat)
    await db.commit()

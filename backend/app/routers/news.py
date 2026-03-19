"""
경제/지식 패스 뉴스 API.
유저의 카테고리 이름을 키워드로 사용해 개인화된 뉴스를 반환.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.models import Category, Stat
from app.services.news_service import fetch_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=list[dict])
async def get_news(
    category: str | None = Query(default=None, description="economy | knowledge | all"),
    page_size: int = Query(default=10, le=20),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """개인화된 뉴스 반환 — 유저의 카테고리 이름을 검색 키워드로 사용."""
    user_keywords: list[str] = []
    try:
        result = await db.execute(
            select(Category.name).join(Stat, Category.stat_id == Stat.id)
            .where(Category.user_id == user_id)
        )
        user_keywords = [row[0] for row in result.fetchall()]
    except Exception:
        pass

    return await fetch_news(
        category=category,
        page_size=page_size,
        user_keywords=user_keywords if user_keywords else None,
    )

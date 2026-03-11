"""
경제/지식 패스 뉴스 API.

GET /news?category=economy&page_size=10
  category: economy | knowledge | all (기본: all)
  page_size: 최대 20 (기본: 10)
"""
from fastapi import APIRouter, Query
from app.services.news_service import fetch_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=list[dict])
async def get_news(
    category: str | None = Query(default=None, description="economy | knowledge | all"),
    page_size: int = Query(default=10, le=20),
):
    """경제·지식 뉴스 목록 반환."""
    return await fetch_news(category=category, page_size=page_size)

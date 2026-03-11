"""
뉴스 가져오기 서비스.

NewsAPI (https://newsapi.org) 또는 GNews API를 사용.
API 키가 없으면 샘플 데이터 반환 (로컬 개발용).

환경변수:
  NEWS_API_KEY=your_key  (newsapi.org 가입 후 무료 발급)
"""
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# 로컬 개발용 샘플 뉴스
SAMPLE_NEWS = [
    {
        "title": "2025 자기계발 트렌드: 마이크로 루틴의 부상",
        "description": "짧고 일관성 있는 마이크로 루틴이 장기적 성공의 핵심으로 주목받고 있다.",
        "url": "https://example.com/news/1",
        "source": "자기개발 매거진",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "category": "knowledge",
    },
    {
        "title": "복리 효과: 1% 개선이 1년 후 37배 차이를 만드는 법",
        "description": "매일 1%씩 나아지면 1년 후 약 37배 성장한다는 복리 원칙의 실천 방법.",
        "url": "https://example.com/news/2",
        "source": "경제 인사이트",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
        "category": "economy",
    },
    {
        "title": "운동과 인지 능력: 하루 30분이 뇌를 바꾼다",
        "description": "최신 연구에 따르면 규칙적인 유산소 운동이 집중력과 기억력을 30% 향상시킨다.",
        "url": "https://example.com/news/3",
        "source": "헬스 사이언스",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
        "category": "knowledge",
    },
    {
        "title": "2030 세대 재테크: ETF 장기투자 vs 적금, 어떤 게 유리할까",
        "description": "장기 관점에서 ETF 분산투자와 전통적인 적금 상품을 비교 분석한다.",
        "url": "https://example.com/news/4",
        "source": "머니 가이드",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
        "category": "economy",
    },
    {
        "title": "수면 루틴이 성공을 결정한다: 최적 수면 시간대 분석",
        "description": "상위 1% 성공인들의 수면 패턴을 분석해 최적의 취침/기상 루틴을 제안한다.",
        "url": "https://example.com/news/5",
        "source": "라이프스타일 리서치",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
        "category": "knowledge",
    },
]


async def fetch_news(category: str | None = None, page_size: int = 10) -> list[dict]:
    """
    뉴스 목록 반환.
    NEWS_API_KEY가 설정되면 실제 NewsAPI 호출, 없으면 샘플 데이터 반환.
    """
    from app.core.config import settings
    api_key = getattr(settings, "news_api_key", "")

    if api_key and not api_key.startswith("YOUR_"):
        return await _fetch_from_newsapi(api_key, category, page_size)

    # 샘플 데이터 (API 키 없을 때)
    items = SAMPLE_NEWS
    if category and category != "all":
        items = [n for n in items if n["category"] == category]
    return items[:page_size]


async def _fetch_from_newsapi(api_key: str, category: str | None, page_size: int) -> list[dict]:
    """NewsAPI에서 한국 경제/지식 뉴스 가져오기."""
    try:
        import httpx
        # category 매핑: economy→business, knowledge→science
        q_map = {"economy": "경제 재테크", "knowledge": "자기계발 독서"}
        q = q_map.get(category or "economy", "자기계발 경제")

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": q,
                    "language": "ko",
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "apiKey": api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return [
            {
                "title": a["title"],
                "description": a.get("description", ""),
                "url": a["url"],
                "source": a["source"]["name"],
                "published_at": a["publishedAt"],
                "category": category or "economy",
            }
            for a in data.get("articles", [])
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]
    except Exception as e:
        logger.error("NewsAPI 호출 실패: %s — 샘플 데이터 반환", e)
        return SAMPLE_NEWS[:page_size]

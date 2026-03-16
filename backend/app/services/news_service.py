"""
뉴스 가져오기 서비스.

네이버 검색 API (뉴스/블로그) + YouTube Data API v3 사용.
API 키가 없으면 샘플 데이터 반환 (로컬 개발용 폴백).

환경변수:
  NAVER_CLIENT_ID=...      (https://developers.naver.com — 무료)
  NAVER_CLIENT_SECRET=...
  YOUTUBE_API_KEY=...      (https://console.cloud.google.com — 무료 10,000 units/day)
"""
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# 로컬 개발용 샘플 뉴스 (API 키 미설정 시 폴백)
SAMPLE_NEWS = [
    {
        "title": "2025 자기계발 트렌드: 마이크로 루틴의 부상",
        "description": "짧고 일관성 있는 마이크로 루틴이 장기적 성공의 핵심으로 주목받고 있다.",
        "url": "https://example.com/news/1",
        "source": "자기계발 매거진",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "category": "knowledge",
        "thumbnail": None,
    },
    {
        "title": "복리 효과: 1% 개선이 1년 후 37배 차이를 만드는 법",
        "description": "매일 1%씩 나아지면 1년 후 약 37배 성장한다는 복리 원칙의 실천 방법.",
        "url": "https://example.com/news/2",
        "source": "경제 인사이트",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
        "category": "economy",
        "thumbnail": None,
    },
    {
        "title": "운동과 인지 능력: 하루 30분이 뇌를 바꾼다",
        "description": "최신 연구에 따르면 규칙적인 유산소 운동이 집중력과 기억력을 30% 향상시킨다.",
        "url": "https://example.com/news/3",
        "source": "헬스 사이언스",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
        "category": "knowledge",
        "thumbnail": None,
    },
    {
        "title": "2030 세대 재테크: ETF 장기투자 vs 적금, 어떤 게 유리할까",
        "description": "장기 관점에서 ETF 분산투자와 전통적인 적금 상품을 비교 분석한다.",
        "url": "https://example.com/news/4",
        "source": "머니 가이드",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
        "category": "economy",
        "thumbnail": None,
    },
    {
        "title": "수면 루틴이 성공을 결정한다: 최적 수면 시간대 분석",
        "description": "상위 1% 성공인들의 수면 패턴을 분석해 최적의 취침/기상 루틴을 제안한다.",
        "url": "https://example.com/news/5",
        "source": "라이프스타일 리서치",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
        "category": "knowledge",
        "thumbnail": None,
    },
    {
        "title": "자기계발 쇼츠: 하루 5분 집중력 훈련법",
        "description": "짧은 시간 안에 집중력을 키우는 실전 방법을 소개합니다.",
        "url": "https://www.youtube.com/shorts/example1",
        "source": "YouTube",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
        "category": "shorts",
        "thumbnail": None,
    },
]


async def fetch_news(category: str | None = None, page_size: int = 10) -> list[dict]:
    """
    뉴스 목록 반환.

    category:
      - "economy"   → 네이버 뉴스 (재테크 경제) + YouTube (재테크 쇼츠)
      - "knowledge" → 네이버 블로그 (자기계발) + YouTube (자기계발 쇼츠)
      - "shorts"    → YouTube만 (자기계발 운동 쇼츠)
      - None / "all"→ 세 가지 mix
    """
    from app.core.config import settings

    naver_id = getattr(settings, "naver_client_id", "")
    naver_secret = getattr(settings, "naver_client_secret", "")
    youtube_key = getattr(settings, "youtube_api_key", "")

    has_naver = naver_id and not naver_id.startswith("YOUR_")
    has_youtube = youtube_key and not youtube_key.startswith("YOUR_")

    # API 키가 전혀 없으면 샘플 데이터 폴백
    if not has_naver and not has_youtube:
        items = SAMPLE_NEWS
        if category and category != "all":
            items = [n for n in items if n["category"] == category]
        return items[:page_size]

    results: list[dict] = []

    if category == "economy":
        if has_naver:
            results += await _fetch_naver_news(naver_id, naver_secret, "재테크 경제", "economy", page_size)
        if has_youtube:
            results += await _fetch_youtube(youtube_key, "재테크 쇼츠", "economy", max(2, page_size // 3))

    elif category == "knowledge":
        if has_naver:
            results += await _fetch_naver_blog(naver_id, naver_secret, "자기계발", "knowledge", page_size)
        if has_youtube:
            results += await _fetch_youtube(youtube_key, "자기계발 쇼츠", "knowledge", max(2, page_size // 3))

    elif category == "shorts":
        if has_youtube:
            results += await _fetch_youtube(youtube_key, "자기계발 운동 쇼츠", "shorts", page_size)
        else:
            # YouTube 키 없으면 샘플 shorts 반환
            return [n for n in SAMPLE_NEWS if n["category"] == "shorts"][:page_size]

    else:
        # all / None: 세 소스 mix
        per = max(2, page_size // 3)
        if has_naver:
            results += await _fetch_naver_news(naver_id, naver_secret, "재테크 경제", "economy", per)
            results += await _fetch_naver_blog(naver_id, naver_secret, "자기계발", "knowledge", per)
        if has_youtube:
            results += await _fetch_youtube(youtube_key, "자기계발 운동 쇼츠", "shorts", per)

    return results[:page_size] if results else SAMPLE_NEWS[:page_size]


# ─── 네이버 뉴스 ──────────────────────────────────────────────────────────────

async def _fetch_naver_news(
    client_id: str,
    client_secret: str,
    query: str,
    category: str,
    display: int,
) -> list[dict]:
    """네이버 뉴스 검색 API 호출."""
    try:
        import httpx

        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://openapi.naver.com/v1/search/news.json",
                headers=headers,
                params={"query": query, "display": display, "sort": "date"},
            )
            resp.raise_for_status()
            data = resp.json()

        items = []
        for item in data.get("items", []):
            title = _strip_html(item.get("title", ""))
            description = _strip_html(item.get("description", ""))
            pub_date = _parse_naver_date(item.get("pubDate", ""))
            items.append({
                "title": title,
                "description": description,
                "url": item.get("originallink") or item.get("link", ""),
                "source": "네이버뉴스",
                "published_at": pub_date,
                "category": category,
                "thumbnail": None,
            })
        return items

    except Exception as e:
        logger.warning("네이버 뉴스 API 호출 실패 (query=%s): %s", query, e)
        return []


# ─── 네이버 블로그 ────────────────────────────────────────────────────────────

async def _fetch_naver_blog(
    client_id: str,
    client_secret: str,
    query: str,
    category: str,
    display: int,
) -> list[dict]:
    """네이버 블로그 검색 API 호출."""
    try:
        import httpx

        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://openapi.naver.com/v1/search/blog.json",
                headers=headers,
                params={"query": query, "display": display, "sort": "date"},
            )
            resp.raise_for_status()
            data = resp.json()

        items = []
        for item in data.get("items", []):
            title = _strip_html(item.get("title", ""))
            description = _strip_html(item.get("description", ""))
            pub_date = _parse_naver_date(item.get("postdate", ""))
            items.append({
                "title": title,
                "description": description,
                "url": item.get("link", ""),
                "source": "네이버블로그",
                "published_at": pub_date,
                "category": category,
                "thumbnail": None,
            })
        return items

    except Exception as e:
        logger.warning("네이버 블로그 API 호출 실패 (query=%s): %s", query, e)
        return []


# ─── YouTube ─────────────────────────────────────────────────────────────────

async def _fetch_youtube(
    api_key: str,
    query: str,
    category: str,
    max_results: int,
) -> list[dict]:
    """YouTube Data API v3 — Shorts 검색."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "videoDuration": "short",
                    "maxResults": max_results,
                    "key": api_key,
                    "relevanceLanguage": "ko",
                    "regionCode": "KR",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        items = []
        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            snippet = item.get("snippet", {})
            thumbnail = (
                snippet.get("thumbnails", {}).get("medium", {}).get("url")
                or snippet.get("thumbnails", {}).get("default", {}).get("url")
            )
            pub = snippet.get("publishedAt", datetime.now(timezone.utc).isoformat())
            items.append({
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "url": f"https://www.youtube.com/shorts/{video_id}",
                "source": "YouTube",
                "published_at": pub,
                "category": category,
                "thumbnail": thumbnail,
            })
        return items

    except Exception as e:
        logger.warning("YouTube API 호출 실패 (query=%s): %s", query, e)
        return []


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    """네이버 API 응답에 포함된 <b> 등 HTML 태그 제거."""
    import re
    return re.sub(r"<[^>]+>", "", text).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').strip()


def _parse_naver_date(date_str: str) -> str:
    """
    네이버 날짜 포맷 → ISO 8601.
    뉴스: 'Mon, 16 Mar 2026 10:00:00 +0900'
    블로그: '20260316'
    """
    if not date_str:
        return datetime.now(timezone.utc).isoformat()

    # 블로그: YYYYMMDD
    if len(date_str) == 8 and date_str.isdigit():
        try:
            dt = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            pass

    # 뉴스: RFC 2822
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).isoformat()
    except Exception:
        pass

    return datetime.now(timezone.utc).isoformat()

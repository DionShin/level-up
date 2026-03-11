"""
SQLAlchemy 비동기 DB 엔진 및 세션 설정.

파이썬 관점에서: engine = DB 커넥션 풀, AsyncSession = 파이썬의 with문과 같은 컨텍스트 매니저로 쓰는 DB 트랜잭션 객체.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _make_db_url(url: str) -> str:
    """
    Supabase/Railway PostgreSQL URL을 asyncpg 드라이버 URL로 변환.
    postgresql:// → postgresql+asyncpg://
    postgres://   → postgresql+asyncpg://  (Railway 등이 제공하는 형식)
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_db_url = _make_db_url(settings.DATABASE_URL)

# SQLite는 check_same_thread=False 필요
connect_args = {"check_same_thread": False} if "sqlite" in _db_url else {}

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args=connect_args,
)

# 세션 팩토리 (파이썬의 클래스 팩토리 패턴과 동일)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # commit 후에도 객체 속성 유지
)


# SQLAlchemy 모델의 Base 클래스
class Base(DeclarativeBase):
    pass


# FastAPI 의존성 주입용 DB 세션 제너레이터
# 파이썬의 제너레이터(yield)를 이용한 컨텍스트 매니저 패턴
async def get_db() -> AsyncSession:  # type: ignore[return]
    async with AsyncSessionLocal() as session:
        yield session

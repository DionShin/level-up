"""
Alembic 환경 설정.
비동기 SQLAlchemy 엔진을 사용하여 마이그레이션 실행.

사용법:
  alembic revision --autogenerate -m "설명"   # 새 마이그레이션 자동 생성
  alembic upgrade head                        # 최신 버전으로 마이그레이션
  alembic downgrade -1                        # 한 단계 롤백
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config 객체 (alembic.ini 설정 접근)
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 우리 앱의 모델 Base import — autogenerate가 테이블 변경을 감지
from app.core.database import Base
import app.models.models  # noqa: F401 — 모든 모델을 Base에 등록

target_metadata = Base.metadata

# DATABASE_URL을 settings에서 읽어 alembic에 주입
from app.core.config import settings
from app.core.database import _make_db_url

db_url = _make_db_url(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """오프라인 모드: 실제 DB 없이 SQL 스크립트만 생성."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진으로 온라인 마이그레이션."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""
APScheduler 기반 푸시 알림 스케줄러.

스케줄:
  - 매일 07:30 → "오늘의 루틴" 알림 (오늘 루틴이 있는 유저에게)
  - 매일 22:00 → "미완료 루틴" 리마인더

main.py lifespan에서 시작/종료 처리.
"""
import json
import logging
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def _send_daily_reminders(event_time: str, title: str, body: str, url: str = "/"):
    """DB에서 구독자 조회 후 푸시 전송."""
    from app.core.database import AsyncSessionLocal
    from app.models.models import PushSubscription
    from app.services.push_service import send_push
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PushSubscription))
        subs = result.scalars().all()

    sent = 0
    for sub in subs:
        info = {"endpoint": sub.endpoint, "keys": json.loads(sub.keys)}
        if send_push(info, title, body, url):
            sent += 1

    logger.info("[%s] 푸시 전송 완료: %d/%d", event_time, sent, len(subs))


async def _send_morning_news_push():
    """오전 07:30 — 뉴스 헤드라인 + 루틴 알림 통합 푸시."""
    from app.services.news_service import fetch_news

    # 뉴스 헤드라인 가져오기
    try:
        news_list = await fetch_news(category="economy", page_size=1)
        headline = news_list[0]["title"] if news_list else "오늘의 경제 뉴스를 확인하세요."
    except Exception:
        headline = "오늘의 루틴을 시작해 보세요!"

    body = f"[오늘의 인사이트] {headline}"
    await _send_daily_reminders("07:30", "Level-Up 모닝 브리핑", body, "/news")


def start_scheduler():
    """스케줄러 시작 (lifespan에서 호출)."""
    # 매일 07:30 — 모닝 브리핑 (뉴스 헤드라인 + 루틴)
    scheduler.add_job(
        _send_morning_news_push,
        CronTrigger(hour=7, minute=30),
        id="morning_reminder",
        replace_existing=True,
    )

    # 매일 22:00 — 저녁 리마인더
    scheduler.add_job(
        _send_daily_reminders,
        CronTrigger(hour=22, minute=0),
        args=["22:00", "루틴 체크", "오늘 루틴을 완료했나요? 마지막으로 확인해 보세요.", "/"],
        id="evening_reminder",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("스케줄러 시작 — 아침(07:30) + 저녁(22:00) 알림 등록")


def stop_scheduler():
    """스케줄러 종료 (lifespan 종료 시 호출)."""
    if scheduler.running:
        scheduler.shutdown()

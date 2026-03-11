"""
DB 초기 데이터 삽입 스크립트.

실행: python seed.py
파이썬 관점: Django의 management command loaddata와 동일한 역할.
프론트엔드 mock-data.ts의 데이터를 실제 DB에 그대로 이식.
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.core.database import engine, Base, AsyncSessionLocal
from app.models.models import Stat, Category, Routine, RoutineLog, GrowthHistory, CommunityRoutine

USER_ID = "user_001"

# ─── 시드 데이터 (프론트 mock-data.ts와 동일) ─────────────────────
STATS_DATA = [
    {"id": "appearance", "name": "외모", "icon": "✨", "color": "#60a5fa"},
    {"id": "manner",     "name": "매너", "icon": "🤝", "color": "#a78bfa"},
    {"id": "fitness",    "name": "체력", "icon": "💪", "color": "#34d399"},
    {"id": "intellect",  "name": "지성", "icon": "🧠", "color": "#fbbf24"},
    {"id": "asset",      "name": "자산", "icon": "💰", "color": "#f87171"},
]

CATEGORIES_DATA = [
    {"id": "skincare", "stat_id": "appearance", "name": "피부관리", "icon": "🧴", "order_index": 0},
    {"id": "body",     "stat_id": "appearance", "name": "체형관리", "icon": "🏋️", "order_index": 1},
    {"id": "fashion",  "stat_id": "appearance", "name": "패션",    "icon": "👔", "order_index": 2},
    {"id": "speech",   "stat_id": "manner",     "name": "언어습관", "icon": "💬", "order_index": 0},
    {"id": "posture",  "stat_id": "manner",     "name": "자세교정", "icon": "🧍", "order_index": 1},
    {"id": "workout",  "stat_id": "fitness",    "name": "근력운동", "icon": "🏋️", "order_index": 0},
    {"id": "cardio",   "stat_id": "fitness",    "name": "유산소",   "icon": "🏃", "order_index": 1},
    {"id": "sleep",    "stat_id": "fitness",    "name": "수면관리", "icon": "😴", "order_index": 2},
    {"id": "reading",  "stat_id": "intellect",  "name": "독서",     "icon": "📚", "order_index": 0},
    {"id": "english",  "stat_id": "intellect",  "name": "영어",     "icon": "🇺🇸", "order_index": 1},
    {"id": "news",     "stat_id": "intellect",  "name": "시사경제", "icon": "📰", "order_index": 2},
    {"id": "invest",   "stat_id": "asset",      "name": "투자공부", "icon": "📈", "order_index": 0},
    {"id": "savings",  "stat_id": "asset",      "name": "절약습관", "icon": "💳", "order_index": 1},
]

ROUTINES_DATA = [
    {"id": "r1",  "category_id": "skincare", "name": "레티놀 바르기",   "frequency": "daily",    "notification_time": "22:30", "is_forked": False},
    {"id": "r2",  "category_id": "skincare", "name": "선크림 바르기",   "frequency": "daily",    "notification_time": "08:00", "is_forked": False},
    {"id": "r3",  "category_id": "skincare", "name": "보습 루틴",       "frequency": "daily",    "notification_time": "23:00", "is_forked": True,  "original_author": "철민_루틴러"},
    {"id": "r4",  "category_id": "body",     "name": "벌크업 식단",     "frequency": "daily",    "notification_time": "12:00", "is_forked": False},
    {"id": "r5",  "category_id": "body",     "name": "체중 측정",       "frequency": "daily",    "notification_time": "07:00", "is_forked": False},
    {"id": "r6",  "category_id": "workout",  "name": "상체 루틴",       "frequency": "weekdays", "notification_time": "19:00", "is_forked": False, "days_of_week": [1, 3, 5]},
    {"id": "r7",  "category_id": "workout",  "name": "하체 루틴",       "frequency": "weekdays", "notification_time": "19:00", "is_forked": False, "days_of_week": [2, 4]},
    {"id": "r8",  "category_id": "workout",  "name": "코어 운동",       "frequency": "daily",    "notification_time": "07:30", "is_forked": True,  "original_author": "헬스왕_준"},
    {"id": "r9",  "category_id": "cardio",   "name": "30분 조깅",       "frequency": "weekdays", "notification_time": "06:30", "is_forked": False, "days_of_week": [1, 3, 5]},
    {"id": "r10", "category_id": "cardio",   "name": "계단 이용",       "frequency": "daily",    "notification_time": "09:00", "is_forked": False},
    {"id": "r11", "category_id": "reading",  "name": "30분 독서",       "frequency": "daily",    "notification_time": "22:00", "is_forked": False},
    {"id": "r12", "category_id": "invest",   "name": "경제뉴스 읽기",   "frequency": "daily",    "notification_time": "07:30", "is_forked": False},
    {"id": "r13", "category_id": "invest",   "name": "포트폴리오 점검", "frequency": "weekdays", "notification_time": "10:00", "is_forked": False, "days_of_week": [0]},
]

def get_date(days_ago: int) -> date:
    return date.today() - timedelta(days=days_ago)

LOGS_DATA = [
    # r1 레티놀 (85% 달성률 목표)
    *[{"routine_id": "r1", "date": get_date(i), "completed": i not in [2, 5]} for i in range(7)],
    # r2 선크림 (90%)
    *[{"routine_id": "r2", "date": get_date(i), "completed": i not in [4]} for i in range(7)],
    # r11 독서 (85%)
    *[{"routine_id": "r11", "date": get_date(i), "completed": i not in [3]} for i in range(7)],
    # r6 상체 (격일)
    {"routine_id": "r6", "date": get_date(0), "completed": False},
    {"routine_id": "r6", "date": get_date(2), "completed": True},
    {"routine_id": "r6", "date": get_date(4), "completed": True},
    {"routine_id": "r6", "date": get_date(6), "completed": False},
    # r12 경제뉴스 (42%)
    *[{"routine_id": "r12", "date": get_date(i), "completed": i in [1, 3, 6]} for i in range(7)],
]

HISTORY_DATA = [
    {"event_type": "habit_formed",    "content": "습관 정착 성공! 21일 연속 달성 🏆", "routine_id": "r2"},
    {"event_type": "forked",          "content": "헬스왕_준의 루틴을 내 플랜에 추가", "routine_id": "r8"},
    {"event_type": "streak_broken",   "content": "연속 달성 중단", "routine_id": "r9", "note": "날씨 핑계 그만. 실내 대체 운동 준비하기"},
    {"event_type": "routine_added",   "content": "새 루틴 시작", "routine_id": "r1"},
    {"event_type": "routine_added",   "content": "새 루틴 시작 - 목표: 연간 24권", "routine_id": "r11"},
    {"event_type": "streak_broken",   "content": "연속 달성 중단", "routine_id": "r12", "note": "주말 연속으로 빠짐. 알림 시간 조정 필요"},
    {"event_type": "routine_added",   "content": "주간 투자 점검 루틴 추가", "routine_id": "r13"},
]

COMMUNITY_DATA = [
    {"id": "c1", "author_user_id": "u_cheolmin", "author_name": "철민_루틴러", "author_level": 28, "stat_id": "appearance", "category_name": "피부관리", "routine_name": "10단계 피부관리 루틴", "description": "피부과 의사 추천 순서로 정리한 완벽한 스킨케어 루틴. 3개월 만에 피부톤 확 달라짐", "frequency": "daily", "notification_time": "22:00", "tags": ["피부", "스킨케어", "비기너OK"], "fork_count": 342, "like_count": 891},
    {"id": "c2", "author_user_id": "u_jun",     "author_name": "헬스왕_준",  "author_level": 45, "stat_id": "fitness",    "category_name": "근력운동", "routine_name": "3분할 입문 루틴",      "description": "헬스 6년차가 만든 초보자 맞춤 3분할. 과학적 볼륨으로 최단기 증량 가능",    "frequency": "weekdays", "days_of_week": [1,3,5,2,4], "notification_time": "19:00", "tags": ["헬스", "근성장", "3분할"], "fork_count": 1204, "like_count": 2103},
    {"id": "c3", "author_user_id": "u_book",    "author_name": "독서매니아", "author_level": 33, "stat_id": "intellect",  "category_name": "독서",     "routine_name": "연간 50권 독서법",     "description": "취침 전 30분 + 점심 20분 루틴으로 연간 50권 달성. 책 선정 기준도 공유",    "frequency": "daily", "notification_time": "22:00", "tags": ["독서", "자기계발", "루틴화"], "fork_count": 567, "like_count": 1203},
    {"id": "c4", "author_user_id": "u_invest",  "author_name": "재테크_민수","author_level": 19, "stat_id": "asset",      "category_name": "투자공부", "routine_name": "직장인 아침 경제루틴",  "description": "기상 후 30분: 뉴스 → 포트폴리오 → 메모. 1년째 지속 중인 루틴",          "frequency": "daily", "notification_time": "07:00", "tags": ["경제", "투자", "아침루틴"], "fork_count": 289, "like_count": 445},
    {"id": "c5", "author_user_id": "u_posture", "author_name": "자세요정",   "author_level": 22, "stat_id": "manner",     "category_name": "자세교정", "routine_name": "거북목 교정 루틴",     "description": "물리치료사에게 배운 거북목/라운드숄더 교정 스트레칭 10분 루틴",            "frequency": "daily", "notification_time": "12:00", "tags": ["자세", "거북목", "직장인"], "fork_count": 731, "like_count": 1567},
]


async def seed():
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 이미 데이터 있으면 스킵 (멱등성 보장)
        existing = await db.execute(select(Stat).limit(1))
        if existing.scalar_one_or_none():
            print("[OK] 이미 시드 데이터가 존재합니다. 스킵.")
            return

        print("[SEED] 시드 데이터 삽입 중...")

        for s in STATS_DATA:
            db.add(Stat(user_id=USER_ID, **s))

        for c in CATEGORIES_DATA:
            db.add(Category(user_id=USER_ID, **c))

        for r in ROUTINES_DATA:
            db.add(Routine(user_id=USER_ID, **r))

        await db.flush()

        for l in LOGS_DATA:
            db.add(RoutineLog(user_id=USER_ID, log_date=l["date"], routine_id=l["routine_id"], completed=l["completed"]))

        for h in HISTORY_DATA:
            db.add(GrowthHistory(user_id=USER_ID, **h))

        for cr in COMMUNITY_DATA:
            db.add(CommunityRoutine(**cr))

        await db.commit()
        print("[DONE] 시드 완료!")


if __name__ == "__main__":
    asyncio.run(seed())

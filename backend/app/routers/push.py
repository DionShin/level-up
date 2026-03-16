"""
Web Push 구독 관리 및 수동 테스트 전송 API.

엔드포인트:
  POST /push/subscribe    — 구독 정보 저장
  POST /push/unsubscribe  — 구독 해제
  GET  /push/vapid-key    — 프론트에서 구독 시 필요한 VAPID 공개키 반환
  POST /push/test         — 테스트 푸시 즉시 전송 (개발용)
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.config import settings
from app.core.database import get_db
from app.models.models import PushSubscription
from app.services.push_service import send_push

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/push", tags=["push"])


class SubscribeBody(BaseModel):
    endpoint: str
    keys: dict  # {"p256dh": "...", "auth": "..."}
    expirationTime: float | None = None


class UnsubscribeBody(BaseModel):
    endpoint: str


@router.get("/vapid-key")
async def get_vapid_public_key():
    """프론트에서 pushManager.subscribe() 할 때 필요한 VAPID 공개키."""
    key = getattr(settings, "vapid_public_key", "")
    if not key or key.startswith("YOUR_"):
        raise HTTPException(status_code=503, detail="VAPID 키가 설정되지 않았습니다.")
    return {"vapidPublicKey": key}


@router.post("/subscribe")
async def subscribe(
    body: SubscribeBody,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """브라우저 구독 정보 저장 (중복 방지: endpoint 기준 upsert)."""
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
    )
    sub = result.scalar_one_or_none()

    if sub:
        sub.user_id = user_id
        sub.keys = json.dumps(body.keys)
    else:
        sub = PushSubscription(
            user_id=user_id,
            endpoint=body.endpoint,
            keys=json.dumps(body.keys),
        )
        db.add(sub)

    await db.commit()
    return {"message": "구독 완료"}


@router.post("/unsubscribe")
async def unsubscribe(
    body: UnsubscribeBody,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """구독 해제."""
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.endpoint == body.endpoint,
            PushSubscription.user_id == user_id,
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.commit()
    return {"message": "구독 해제 완료"}


@router.post("/test")
async def send_test_push(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """내 구독 목록에 테스트 푸시 전송 (개발/디버깅용)."""
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    subs = result.scalars().all()

    if not subs:
        raise HTTPException(status_code=404, detail="등록된 구독이 없습니다.")

    sent = 0
    for sub in subs:
        subscription_info = {"endpoint": sub.endpoint, "keys": json.loads(sub.keys)}
        ok = send_push(subscription_info, "Axis 테스트", "푸시 알림이 정상 작동합니다!", "/")
        if ok:
            sent += 1

    return {"sent": sent, "total": len(subs)}

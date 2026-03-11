"""
Web Push 전송 서비스 (pywebpush 기반).

VAPID 키 생성 방법 (최초 1회):
  pip install pywebpush
  python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); v.save_key('vapid_private.pem'); print(v.public_key.public_bytes_raw().hex())"

또는 간단히:
  python -m py_vapid --gen  (vapid_private.pem, vapid_public.pem 생성)
"""
import json
import logging
from pywebpush import webpush, WebPushException
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_push(subscription_info: dict, title: str, body: str, url: str = "/") -> bool:
    """
    단일 구독자에게 Web Push 전송.
    subscription_info: {"endpoint": "...", "keys": {"p256dh": "...", "auth": "..."}}
    """
    vapid_private = getattr(settings, "vapid_private_key", None)
    vapid_email = getattr(settings, "vapid_email", "mailto:admin@levelup.app")

    if not vapid_private or vapid_private.startswith("YOUR_"):
        logger.warning("VAPID 키 미설정 — 푸시 전송 스킵")
        return False

    data = json.dumps({"title": title, "body": body, "url": url})
    try:
        webpush(
            subscription_info=subscription_info,
            data=data,
            vapid_private_key=vapid_private,
            vapid_claims={"sub": vapid_email},
        )
        return True
    except WebPushException as e:
        logger.error("WebPush 전송 실패: %s", e)
        return False

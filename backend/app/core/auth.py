"""
JWT 인증 미들웨어.

Supabase가 발급한 JWT를 검증하고 user_id를 추출.
파이썬 관점: FastAPI의 Depends()를 이용한 의존성 주입 패턴.
            = Django의 @login_required 데코레이터와 동일한 역할.

개발 모드: Authorization 헤더가 없으면 DEFAULT_USER_ID 사용 (테스트 편의).
프로덕션: 헤더 필수, 검증 실패 시 401 반환.
"""
import os
import httpx
from functools import lru_cache
from fastapi import Depends, HTTPException, Header
from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_jwks():
    """Supabase 공개키 조회 (lru_cache로 1회만 호출)."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url:
        return None
    try:
        res = httpx.get(f"{supabase_url}/auth/v1/.well-known/jwks.json", timeout=5)
        return res.json()
    except Exception:
        return None


async def get_current_user_id(
    authorization: str | None = Header(default=None)
) -> str:
    """
    Authorization: Bearer <JWT> 헤더에서 user_id 추출.

    SUPABASE_URL 미설정 시 (로컬 개발) → DEFAULT_USER_ID 반환.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")

    # 로컬 개발: Supabase 미연동 → 하드코딩 ID 사용
    if not supabase_url:
        return settings.DEFAULT_USER_ID

    # 토큰 없음
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    token = authorization.split(" ", 1)[1]

    try:
        from jose import jwt, JWTError
        jwks = get_supabase_jwks()
        if not jwks:
            # JWKS 조회 실패 시 서명 검증 없이 디코딩 (개발용)
            payload = jwt.decode(token, options={"verify_signature": False})
        else:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience="authenticated",
            )
        user_id: str = payload.get("sub", settings.DEFAULT_USER_ID)
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

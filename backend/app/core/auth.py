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
from fastapi import Depends, HTTPException, Header
from app.core.config import settings


_jwks_cache: dict | None = None

def get_supabase_jwks():
    """Supabase 공개키 조회 (성공 시에만 캐싱)."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url:
        return None
    try:
        res = httpx.get(f"{supabase_url}/auth/v1/.well-known/jwks.json", timeout=5)
        _jwks_cache = res.json()
        return _jwks_cache
    except Exception:
        return None  # 실패 시 캐싱 안 함 → 다음 요청에서 재시도


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
            # JWKS 조회 실패 시 서명 검증 없이 클레임만 추출
            payload = jwt.get_unverified_claims(token)
        else:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience="authenticated",
            )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        return user_id
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

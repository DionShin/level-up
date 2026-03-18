# Axis 앱 — Claude 작업 가이드

## 프로젝트
- **앱 이름**: Axis (구 Level-Up) — 한국 2030 남성 자기관리 플랫폼
- **프론트엔드**: https://axis0843.vercel.app (Vercel, Next.js 14)
- **백엔드**: Railway (FastAPI + PostgreSQL)
- **인증**: Supabase (https://hjgkolkwsxmijhmeethp.supabase.co)

## 기술 스택
- Frontend: Next.js 14 App Router + TypeScript + TanStack Query + Tailwind CSS
- Backend: FastAPI + async SQLAlchemy 2.0 + asyncpg
- Auth: Supabase Auth
- Push: Web Push API + VAPID + APScheduler
- News: 네이버 Search API + YouTube Data API v3

## 배포 설정
- Railway: Root Directory = `backend`, PYTHONPATH=/app
- Railway 환경변수: DATABASE_URL, SUPABASE_URL, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, YOUTUBE_API_KEY, VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY
- Vercel 환경변수: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_URL
- alembic 실행 안 함 — FastAPI lifespan의 create_all 사용

## 완료된 기능
- 이메일+비밀번호 회원가입/로그인 (Supabase)
- 4단계 온보딩: 키워드 선택 → 카테고리/루틴 자동생성 → SNS → 알림
- 오각형 레이더 차트 (외모/매너/체력/지성/자산)
- 루틴 관리 (CRUD, 일별 체크, 스트릭)
- 오늘의 인사이트 (네이버 뉴스/블로그 + YouTube 쇼츠 실시간)
- 커뮤니티 (공유/검색/포크/좋아요)
- 프로필 (닉네임 편집, 스탯 요약, 알림 토글, 로그아웃)
- 푸시 알림 (07:30 브리핑, 22:00 리마인더)
- user_id 개인화 (유저별 데이터 분리)

## 남은 작업
1. 루틴 기반 인사이트 (내 루틴 키워드로 뉴스/유튜브 검색)
2. n각형 커스터마이징 (스탯 추가/삭제, 3~8각형 동적 변형)
3. Google/GitHub OAuth (Supabase Provider 설정 필요)
4. 앱 아이콘 (public/icons/icon-192.png, icon-512.png)

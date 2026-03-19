import { NextResponse } from 'next/server';

// 네이버 OAuth 시작 — 네이버 로그인 페이지로 리디렉트
export async function GET() {
  const clientId = process.env.NAVER_LOGIN_CLIENT_ID;
  if (!clientId) {
    return NextResponse.json({ error: 'NAVER_LOGIN_CLIENT_ID 환경변수 미설정' }, { status: 500 });
  }

  const state = Math.random().toString(36).substring(2);
  const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/naver/callback`;

  const naverAuthUrl = new URL('https://nid.naver.com/oauth2.0/authorize');
  naverAuthUrl.searchParams.set('response_type', 'code');
  naverAuthUrl.searchParams.set('client_id', clientId);
  naverAuthUrl.searchParams.set('redirect_uri', redirectUri);
  naverAuthUrl.searchParams.set('state', state);

  return NextResponse.redirect(naverAuthUrl.toString());
}

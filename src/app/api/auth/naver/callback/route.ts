import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// 네이버 OAuth 콜백 — 코드 교환 → 유저 정보 → Supabase 로그인 처리
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');

  if (!code) {
    return NextResponse.redirect(`${origin}/login?error=naver_auth_failed`);
  }

  const clientId = process.env.NAVER_LOGIN_CLIENT_ID!;
  const clientSecret = process.env.NAVER_LOGIN_CLIENT_SECRET!;
  const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/naver/callback`;

  try {
    // 1. 네이버 액세스 토큰 발급
    const tokenRes = await fetch('https://nid.naver.com/oauth2.0/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: clientId,
        client_secret: clientSecret,
        code,
        redirect_uri: redirectUri,
      }),
    });
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;
    if (!accessToken) throw new Error('네이버 토큰 발급 실패');

    // 2. 네이버 유저 정보 조회
    const profileRes = await fetch('https://openapi.naver.com/v1/nid/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const profileData = await profileRes.json();
    const naverUser = profileData.response;
    const email = naverUser?.email;
    const name = naverUser?.name || naverUser?.nickname || '네이버유저';

    if (!email) throw new Error('네이버 이메일 정보 없음');

    // 3. Supabase Admin으로 유저 생성 또는 조회
    const supabaseAdmin = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!,
    );

    // 이미 가입된 유저인지 확인 후 없으면 생성
    const { data: existingUsers } = await supabaseAdmin.auth.admin.listUsers();
    const existing = existingUsers?.users?.find(u => u.email === email);

    if (!existing) {
      await supabaseAdmin.auth.admin.createUser({
        email,
        email_confirm: true,
        user_metadata: { full_name: name, provider: 'naver' },
      });
    }

    // 4. 매직링크 생성 → 리디렉트 (자동 로그인)
    const { data: linkData, error: linkError } = await supabaseAdmin.auth.admin.generateLink({
      type: 'magiclink',
      email,
      options: { redirectTo: `${origin}/auth/callback` },
    });

    if (linkError || !linkData?.properties?.action_link) {
      throw new Error('로그인 링크 생성 실패');
    }

    return NextResponse.redirect(linkData.properties.action_link);

  } catch (err) {
    console.error('네이버 로그인 오류:', err);
    return NextResponse.redirect(`${origin}/login?error=naver_auth_failed`);
  }
}

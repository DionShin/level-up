/**
 * Supabase 클라이언트 싱글톤 (lazy 초기화).
 * 환경변수 미설정 시 (로컬 개발, 빌드 타임) 안전하게 null 반환.
 */
import { createBrowserClient } from '@supabase/ssr';
import type { SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';

// URL이 유효할 때만 클라이언트 생성 (빌드 타임 오류 방지)
function isValidUrl(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}

let _supabase: SupabaseClient | null = null;

function getSupabaseClient(): SupabaseClient | null {
  if (!isValidUrl(supabaseUrl) || !supabaseAnonKey) return null;
  if (!_supabase) {
    _supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);
  }
  return _supabase;
}

// 하위 호환 export (auth-context.tsx 등에서 사용)
export const supabase = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    const client = getSupabaseClient();
    if (!client) {
      // Supabase 미설정 — 더미 응답 반환
      if (prop === 'auth') {
        return {
          getSession: async () => ({ data: { session: null }, error: null }),
          onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
          signOut: async () => {},
          signInWithOAuth: async () => ({ data: null, error: new Error('Supabase 미설정') }),
          signInWithOtp: async () => ({ data: null, error: new Error('Supabase 미설정') }),
          signInWithPassword: async () => ({ data: null, error: new Error('Supabase 미설정') }),
          signUp: async () => ({ data: null, error: new Error('Supabase 미설정') }),
        };
      }
      return undefined;
    }
    return (client as unknown as Record<string | symbol, unknown>)[prop];
  },
});

// JWT 토큰 반환 (API 요청 헤더용)
export async function getAccessToken(): Promise<string | null> {
  const client = getSupabaseClient();
  if (!client) return null;
  const { data } = await client.auth.getSession();
  return data.session?.access_token ?? null;
}

/**
 * Web Push 구독 관리 유틸리티.
 * Service Worker 등록 → 푸시 구독 → 서버에 구독 정보 전송.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';

/** VAPID 공개키를 URL-safe Base64 → ArrayBuffer로 변환 (Web Push 규격) */
function urlBase64ToUint8Array(base64String: string): ArrayBuffer {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const output = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) {
    output[i] = rawData.charCodeAt(i);
  }
  return output.buffer as ArrayBuffer;
}

/** Service Worker 등록 + 푸시 구독 요청 */
export async function subscribePush(vapidPublicKey: string): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('이 브라우저는 푸시 알림을 지원하지 않습니다.');
    return false;
  }

  try {
    const reg = await navigator.serviceWorker.register('/sw.js');
    await navigator.serviceWorker.ready;

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return false;

    const subscription = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });

    // 서버에 구독 정보 저장
    const { getAccessToken } = await import('./supabase');
    const token = await getAccessToken();
    await fetch(`${API_URL}/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(subscription.toJSON()),
    });

    return true;
  } catch (err) {
    console.error('푸시 구독 실패:', err);
    return false;
  }
}

/** 푸시 구독 해제 */
export async function unsubscribePush(): Promise<void> {
  if (!('serviceWorker' in navigator)) return;

  const reg = await navigator.serviceWorker.getRegistration('/sw.js');
  if (!reg) return;

  const sub = await reg.pushManager.getSubscription();
  if (!sub) return;

  const endpoint = sub.endpoint;
  await sub.unsubscribe();

  const { getAccessToken } = await import('./supabase');
  const token = await getAccessToken();
  await fetch(`${API_URL}/push/unsubscribe`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ endpoint }),
  });
}

/** 현재 구독 상태 확인 */
export async function isPushSubscribed(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) return false;
  const reg = await navigator.serviceWorker.getRegistration('/sw.js');
  if (!reg) return false;
  const sub = await reg.pushManager.getSubscription();
  return !!sub;
}

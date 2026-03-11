/**
 * Service Worker - Level-Up 푸시 알림 처리.
 * 브라우저 백그라운드에서 실행되며 push 이벤트를 수신해 알림을 표시.
 */

// 푸시 이벤트: 서버에서 Web Push 메시지가 오면 실행
self.addEventListener('push', (event) => {
  let data = { title: 'Level-Up', body: '오늘의 루틴을 확인하세요!', url: '/' };

  if (event.data) {
    try {
      data = event.data.json();
    } catch {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    data: { url: data.url || '/' },
    vibrate: [200, 100, 200],
    requireInteraction: false,
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// 알림 클릭: 해당 URL로 이동
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});

// 설치 및 활성화 (캐시는 최소화)
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => event.waitUntil(clients.claim()));

import type { Metadata, Viewport } from 'next';
import './globals.css';
import BottomNav from '@/components/BottomNav';
import Providers from './providers';

export const metadata: Metadata = {
  title: 'Axis',
  description: '2030 남성을 위한 자기관리 앱',
  manifest: '/manifest.json',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0a0a0c',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <Providers>
          <div className="page-wrapper">{children}</div>
          <BottomNav />
        </Providers>
      </body>
    </html>
  );
}

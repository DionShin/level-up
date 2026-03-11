import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Tailwind 클래스 병합 유틸 (shadcn/ui 패턴)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 요일 배열 → 한글 라벨
export const DAY_LABELS = ['일', '월', '화', '수', '목', '금', '토'];

export function formatFrequency(frequency: string, daysOfWeek?: number[]): string {
  if (frequency === 'daily') return '매일';
  if (frequency === 'alternate') return '격일';
  if (frequency === 'weekdays' && daysOfWeek) {
    return daysOfWeek.map(d => DAY_LABELS[d]).join('/') + '요일';
  }
  return frequency;
}

// 날짜를 'MM.DD' 형식으로
export function formatDate(isoString: string): string {
  const d = new Date(isoString);
  return `${d.getMonth() + 1}.${String(d.getDate()).padStart(2, '0')}`;
}

// 상대 시간 ('3일 전', '방금 전')
export function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return '오늘';
  if (days === 1) return '어제';
  if (days < 7) return `${days}일 전`;
  if (days < 30) return `${Math.floor(days / 7)}주 전`;
  return `${Math.floor(days / 30)}개월 전`;
}

// 달성률에 따른 색상
export function rateColor(rate: number): string {
  if (rate >= 80) return '#34d399'; // 초록
  if (rate >= 50) return '#fbbf24'; // 노랑
  return '#f87171';                 // 빨강
}

// 이번 주 날짜 배열 (일~토)
export function getWeekDates(): string[] {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0=일
  const monday = new Date(today);
  monday.setDate(today.getDate() - dayOfWeek);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d.toISOString().split('T')[0];
  });
}

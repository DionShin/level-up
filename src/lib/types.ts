// ─── L1: 5대 스탯 (Root Stats) ────────────────────────────────────
export interface Stat {
  id: string;
  name: string;
  icon: string;
  color: string;      // 차트/UI에서 사용할 고유 색상
  score: number;      // 0~100, 하위 루틴 달성률로 계산
}

// ─── L2: 카테고리 (Categories) ────────────────────────────────────
export interface Category {
  id: string;
  statId: string;
  name: string;
  icon: string;
  description?: string;
  routineCount: number;
  weeklyRate: number; // 0~100%
}

// ─── L3: 루틴 (Routines) ──────────────────────────────────────────
export type Frequency = 'daily' | 'alternate' | 'weekdays';

export interface Routine {
  id: string;
  categoryId: string;
  statId: string;
  name: string;
  description?: string;
  frequency: Frequency;
  daysOfWeek?: number[];   // [1,3,5] = 월,수,금 (weekdays일 때)
  notificationTime?: string; // '22:00'
  weeklyRate: number;        // 주간 달성률 %
  isForked: boolean;
  originalAuthor?: string;
  streak: number;            // 연속 달성일
}

// ─── 루틴 일별 로그 ───────────────────────────────────────────────
export interface RoutineLog {
  routineId: string;
  date: string; // 'YYYY-MM-DD'
  completed: boolean;
}

// ─── 성장 히스토리 타임라인 ───────────────────────────────────────
export type HistoryEventType =
  | 'routine_added'
  | 'routine_deleted'
  | 'habit_formed'   // 21일 연속 달성
  | 'forked'
  | 'quit'
  | 'streak_broken';

export interface GrowthHistory {
  id: string;
  userId: string;
  routineId?: string;
  routineName?: string;
  statId?: string;
  eventType: HistoryEventType;
  content: string;
  note?: string;
  createdAt: string; // ISO string
}

// ─── 커뮤니티 공유 루틴 ──────────────────────────────────────────
export interface CommunityRoutine {
  id: string;
  routineId: string;
  authorName: string;
  authorLevel: number;
  statId: string;
  categoryName: string;
  routineName: string;
  description: string;
  frequency: Frequency;
  daysOfWeek?: number[];
  notificationTime?: string;
  forkCount: number;
  likeCount: number;
  tags: string[];
  createdAt: string;
}

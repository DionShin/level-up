import type { Stat, Category, Routine, RoutineLog, GrowthHistory, CommunityRoutine } from './types';

// ─── L1: 5대 스탯 ─────────────────────────────────────────────────
export const STATS: Stat[] = [
  { id: 'appearance', name: '외모', icon: '✨', color: '#60a5fa', score: 72 },
  { id: 'manner',     name: '매너', icon: '🤝', color: '#a78bfa', score: 85 },
  { id: 'fitness',    name: '체력', icon: '💪', color: '#34d399', score: 60 },
  { id: 'intellect',  name: '지성', icon: '🧠', color: '#fbbf24', score: 78 },
  { id: 'asset',      name: '자산', icon: '💰', color: '#f87171', score: 45 },
];

// ─── L2: 카테고리 ─────────────────────────────────────────────────
export const CATEGORIES: Category[] = [
  // 외모
  { id: 'skincare',  statId: 'appearance', name: '피부관리',  icon: '🧴', routineCount: 3, weeklyRate: 80 },
  { id: 'body',      statId: 'appearance', name: '체형관리',  icon: '🏋️', routineCount: 2, weeklyRate: 65 },
  { id: 'fashion',   statId: 'appearance', name: '패션',      icon: '👔', routineCount: 1, weeklyRate: 90 },
  // 매너
  { id: 'speech',    statId: 'manner',     name: '언어습관',  icon: '💬', routineCount: 2, weeklyRate: 88 },
  { id: 'posture',   statId: 'manner',     name: '자세교정',  icon: '🧍', routineCount: 1, weeklyRate: 75 },
  // 체력
  { id: 'workout',   statId: 'fitness',    name: '근력운동',  icon: '🏋️', routineCount: 3, weeklyRate: 57 },
  { id: 'cardio',    statId: 'fitness',    name: '유산소',    icon: '🏃', routineCount: 2, weeklyRate: 50 },
  { id: 'sleep',     statId: 'fitness',    name: '수면관리',  icon: '😴', routineCount: 2, weeklyRate: 70 },
  // 지성
  { id: 'reading',   statId: 'intellect',  name: '독서',      icon: '📚', routineCount: 1, weeklyRate: 85 },
  { id: 'english',   statId: 'intellect',  name: '영어',      icon: '🇺🇸', routineCount: 2, weeklyRate: 72 },
  { id: 'news',      statId: 'intellect',  name: '시사경제',  icon: '📰', routineCount: 1, weeklyRate: 90 },
  // 자산
  { id: 'invest',    statId: 'asset',      name: '투자공부',  icon: '📈', routineCount: 2, weeklyRate: 40 },
  { id: 'savings',   statId: 'asset',      name: '절약습관',  icon: '💳', routineCount: 1, weeklyRate: 55 },
];

// ─── L3: 루틴 ─────────────────────────────────────────────────────
export const ROUTINES: Routine[] = [
  // 피부관리
  { id: 'r1', categoryId: 'skincare', statId: 'appearance', name: '레티놀 바르기',    description: '취침 전 레티놀 0.1% 도포',    frequency: 'daily',    notificationTime: '22:30', weeklyRate: 85, isForked: false, streak: 12 },
  { id: 'r2', categoryId: 'skincare', statId: 'appearance', name: '선크림 바르기',    description: '외출 전 SPF50+ 도포',          frequency: 'daily',    notificationTime: '08:00', weeklyRate: 90, isForked: false, streak: 25 },
  { id: 'r3', categoryId: 'skincare', statId: 'appearance', name: '보습 루틴',        description: '세안 후 토너 → 에센스 → 크림', frequency: 'daily',    notificationTime: '23:00', weeklyRate: 70, isForked: true, originalAuthor: '철민_루틴러', streak: 7 },
  // 체형관리
  { id: 'r4', categoryId: 'body',     statId: 'appearance', name: '벌크업 식단',      description: '단백질 체중×2g 섭취',          frequency: 'daily',    notificationTime: '12:00', weeklyRate: 65, isForked: false, streak: 5 },
  { id: 'r5', categoryId: 'body',     statId: 'appearance', name: '체중 측정',        description: '기상 직후 공복 체중 기록',      frequency: 'daily',    notificationTime: '07:00', weeklyRate: 80, isForked: false, streak: 18 },
  // 근력운동
  { id: 'r6', categoryId: 'workout',  statId: 'fitness',    name: '상체 루틴',        description: '벤치/숄더/삼두 복합운동',      frequency: 'weekdays', daysOfWeek: [1, 3, 5], notificationTime: '19:00', weeklyRate: 60, isForked: false, streak: 3 },
  { id: 'r7', categoryId: 'workout',  statId: 'fitness',    name: '하체 루틴',        description: '스쿼트/데드리프트/런지',        frequency: 'weekdays', daysOfWeek: [2, 4],    notificationTime: '19:00', weeklyRate: 55, isForked: false, streak: 2 },
  { id: 'r8', categoryId: 'workout',  statId: 'fitness',    name: '코어 운동',        description: '플랭크 3분 + 복근 루틴',       frequency: 'daily',    notificationTime: '07:30', weeklyRate: 45, isForked: true, originalAuthor: '헬스왕_준', streak: 1 },
  // 유산소
  { id: 'r9',  categoryId: 'cardio',  statId: 'fitness',    name: '30분 조깅',        description: '유산소 존2 구간 유지',          frequency: 'weekdays', daysOfWeek: [1, 3, 5], notificationTime: '06:30', weeklyRate: 50, isForked: false, streak: 0 },
  { id: 'r10', categoryId: 'cardio',  statId: 'fitness',    name: '계단 이용',        description: '출퇴근 시 엘리베이터 금지',     frequency: 'daily',    notificationTime: '09:00', weeklyRate: 75, isForked: false, streak: 10 },
  // 독서
  { id: 'r11', categoryId: 'reading', statId: 'intellect',  name: '30분 독서',        description: '잠들기 전 종이책 독서',         frequency: 'daily',    notificationTime: '22:00', weeklyRate: 85, isForked: false, streak: 14 },
  // 투자공부
  { id: 'r12', categoryId: 'invest',  statId: 'asset',      name: '경제뉴스 읽기',    description: '아침 경제 브리핑 10분',         frequency: 'daily',    notificationTime: '07:30', weeklyRate: 42, isForked: false, streak: 2 },
  { id: 'r13', categoryId: 'invest',  statId: 'asset',      name: '포트폴리오 점검',  description: '주간 수익률 및 리밸런싱 확인',  frequency: 'weekdays', daysOfWeek: [0],        notificationTime: '10:00', weeklyRate: 80, isForked: false, streak: 8 },
];

// ─── 이번 주 O/X 로그 (오늘=목요일 기준) ──────────────────────────
// 요일: 0=일 1=월 2=화 3=수 4=목 5=금 6=토
const today = new Date();
const getDate = (daysAgo: number) => {
  const d = new Date(today);
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().split('T')[0];
};

export const ROUTINE_LOGS: RoutineLog[] = [
  // 레티놀 바르기 (r1) - 최근 7일
  { routineId: 'r1', date: getDate(0), completed: true  },
  { routineId: 'r1', date: getDate(1), completed: true  },
  { routineId: 'r1', date: getDate(2), completed: false },
  { routineId: 'r1', date: getDate(3), completed: true  },
  { routineId: 'r1', date: getDate(4), completed: true  },
  { routineId: 'r1', date: getDate(5), completed: false },
  { routineId: 'r1', date: getDate(6), completed: true  },
  // 선크림 바르기 (r2)
  { routineId: 'r2', date: getDate(0), completed: true  },
  { routineId: 'r2', date: getDate(1), completed: true  },
  { routineId: 'r2', date: getDate(2), completed: true  },
  { routineId: 'r2', date: getDate(3), completed: true  },
  { routineId: 'r2', date: getDate(4), completed: false },
  { routineId: 'r2', date: getDate(5), completed: true  },
  { routineId: 'r2', date: getDate(6), completed: true  },
  // 상체 루틴 (r6)
  { routineId: 'r6', date: getDate(0), completed: false },
  { routineId: 'r6', date: getDate(2), completed: true  },
  { routineId: 'r6', date: getDate(4), completed: true  },
  { routineId: 'r6', date: getDate(6), completed: false },
  // 30분 독서 (r11)
  { routineId: 'r11', date: getDate(0), completed: true  },
  { routineId: 'r11', date: getDate(1), completed: true  },
  { routineId: 'r11', date: getDate(2), completed: true  },
  { routineId: 'r11', date: getDate(3), completed: false },
  { routineId: 'r11', date: getDate(4), completed: true  },
  { routineId: 'r11', date: getDate(5), completed: true  },
  { routineId: 'r11', date: getDate(6), completed: true  },
];

// ─── 성장 히스토리 타임라인 ───────────────────────────────────────
export const GROWTH_HISTORY: GrowthHistory[] = [
  { id: 'h1', userId: 'me', routineId: 'r2', routineName: '선크림 바르기', statId: 'appearance',  eventType: 'habit_formed',    content: '습관 정착 성공! 21일 연속 달성',               createdAt: '2026-02-18T09:00:00Z' },
  { id: 'h2', userId: 'me', routineId: 'r8', routineName: '코어 운동',     statId: 'fitness',     eventType: 'forked',          content: '헬스왕_준의 루틴을 내 플랜에 추가',           createdAt: '2026-02-25T14:30:00Z' },
  { id: 'h3', userId: 'me', routineId: 'r9', routineName: '30분 조깅',     statId: 'fitness',     eventType: 'streak_broken',   content: '연속 달성 중단 (비 때문에 포기)', note: '날씨 핑계 그만. 실내 대체 운동 준비하기', createdAt: '2026-03-01T22:00:00Z' },
  { id: 'h4', userId: 'me', routineId: 'r1', routineName: '레티놀 바르기', statId: 'appearance',  eventType: 'routine_added',   content: '새 루틴 시작',                                 createdAt: '2026-03-05T11:00:00Z' },
  { id: 'h5', userId: 'me', routineId: 'r11',routineName: '30분 독서',     statId: 'intellect',   eventType: 'routine_added',   content: '새 루틴 시작 - 목표: 연간 24권',              createdAt: '2026-03-06T20:00:00Z' },
  { id: 'h6', userId: 'me', routineId: 'r12',routineName: '경제뉴스 읽기', statId: 'asset',       eventType: 'streak_broken',   content: '연속 달성 중단', note: '주말 연속으로 빠짐. 알림 시간 조정 필요',        createdAt: '2026-03-08T22:00:00Z' },
  { id: 'h7', userId: 'me', routineId: 'r13',routineName: '포트폴리오 점검',statId: 'asset',      eventType: 'routine_added',   content: '주간 투자 점검 루틴 추가',                     createdAt: '2026-03-10T09:00:00Z' },
];

// ─── 커뮤니티 공유 루틴 ──────────────────────────────────────────
export const COMMUNITY_ROUTINES: CommunityRoutine[] = [
  { id: 'c1', routineId: 'cr1', authorName: '철민_루틴러', authorLevel: 28, statId: 'appearance', categoryName: '피부관리', routineName: '10단계 피부관리 루틴', description: '피부과 의사 추천 순서로 정리한 완벽한 스킨케어 루틴. 3개월 만에 피부톤 확 달라짐', frequency: 'daily', notificationTime: '22:00', forkCount: 342, likeCount: 891, tags: ['피부', '스킨케어', '비기너OK'], createdAt: '2026-01-15T00:00:00Z' },
  { id: 'c2', routineId: 'cr2', authorName: '헬스왕_준',  authorLevel: 45, statId: 'fitness',    categoryName: '근력운동', routineName: '3분할 입문 루틴',      description: '헬스 6년차가 만든 초보자 맞춤 3분할. 과학적 볼륨으로 최단기 증량 가능', frequency: 'weekdays', daysOfWeek: [1,3,5,2,4], notificationTime: '19:00', forkCount: 1204, likeCount: 2103, tags: ['헬스', '근성장', '3분할'], createdAt: '2026-01-20T00:00:00Z' },
  { id: 'c3', routineId: 'cr3', authorName: '독서매니아', authorLevel: 33, statId: 'intellect',  categoryName: '독서',     routineName: '연간 50권 독서법',     description: '취침 전 30분 + 점심 20분 루틴으로 연간 50권 달성. 책 선정 기준도 공유', frequency: 'daily', notificationTime: '22:00', forkCount: 567, likeCount: 1203, tags: ['독서', '자기계발', '루틴화'], createdAt: '2026-02-01T00:00:00Z' },
  { id: 'c4', routineId: 'cr4', authorName: '재테크_민수', authorLevel: 19, statId: 'asset',      categoryName: '투자공부', routineName: '직장인 아침 경제루틴',  description: '기상 후 30분: 뉴스 → 포트폴리오 → 메모. 1년째 지속 중인 루틴', frequency: 'daily', notificationTime: '07:00', forkCount: 289, likeCount: 445, tags: ['경제', '투자', '아침루틴'], createdAt: '2026-02-10T00:00:00Z' },
  { id: 'c5', routineId: 'cr5', authorName: '자세요정',   authorLevel: 22, statId: 'manner',     categoryName: '자세교정', routineName: '거북목 교정 루틴',     description: '물리치료사에게 배운 거북목/라운드숄더 교정 스트레칭 10분 루틴', frequency: 'daily', notificationTime: '12:00', forkCount: 731, likeCount: 1567, tags: ['자세', '거북목', '직장인'], createdAt: '2026-02-20T00:00:00Z' },
];

// ─── 헬퍼: ID로 조회 ──────────────────────────────────────────────
export const getStatById = (id: string) => STATS.find(s => s.id === id);
export const getCategoriesByStatId = (statId: string) => CATEGORIES.filter(c => c.statId === statId);
export const getRoutinesByCategoryId = (catId: string) => ROUTINES.filter(r => r.categoryId === catId);
export const getLogsByRoutineId = (routineId: string) => ROUTINE_LOGS.filter(l => l.routineId === routineId);
export const getCategoryById = (id: string) => CATEGORIES.find(c => c.id === id);
export const getRoutineById = (id: string) => ROUTINES.find(r => r.id === id);

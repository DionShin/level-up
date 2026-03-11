'use client';

import { Bell, ChevronRight, Flame, TrendingUp, BookOpen, ExternalLink } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import StatRadarChart from '@/components/StatRadarChart';
import { statsAPI, routinesAPI, newsAPI, type StatResponse, type RoutineResponse } from '@/lib/api';

// API 응답을 StatRadarChart가 기대하는 형태로 변환
function toChartStat(s: StatResponse) {
  return { id: s.id, name: s.name, icon: s.icon, color: s.color, score: s.score };
}

export default function Dashboard() {
  const { data: stats = [], isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: statsAPI.getAll,
  });

  const { data: todayRoutines = [] } = useQuery({
    queryKey: ['routines', 'today'],
    queryFn: routinesAPI.getToday,
  });

  const { data: news = [] } = useQuery({
    queryKey: ['news'],
    queryFn: () => newsAPI.getAll(undefined, 3),
    staleTime: 10 * 60 * 1000, // 10분 캐시 (뉴스는 자주 안 바뀜)
  });

  const avgScore = stats.length
    ? Math.round(stats.reduce((s, r) => s + r.score, 0) / stats.length)
    : 0;
  const level = Math.floor(avgScore / 5) + 1;
  const xpCurrent = (avgScore % 5) * 20;

  const upcomingRoutine = todayRoutines.find(r => r.notification_time) ?? todayRoutines[0];
  const streakRoutines = todayRoutines.filter(r => r.streak > 3).slice(0, 2);

  if (statsLoading) {
    return (
      <main className="min-h-screen bg-[#0a0a0c] flex items-center justify-center">
        <div className="text-gray-600 text-sm animate-pulse">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white px-5 pt-8">

      {/* 상단: 레벨 & XP 바 */}
      <section className="mb-8">
        <div className="flex justify-between items-end mb-2">
          <div>
            <p className="text-[10px] text-gray-600 mb-0.5 tracking-widest uppercase">Your Level</p>
            <h2 className="text-2xl font-black italic text-blue-400">Lv.{level}</h2>
          </div>
          <span className="text-xs text-gray-600">{xpCurrent} / 100 XP</span>
        </div>
        <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-600 to-cyan-400 transition-all duration-700"
            style={{ width: `${xpCurrent}%` }}
          />
        </div>
      </section>

      {/* 중앙: 오각형 레이더 차트 */}
      <section className="mb-5">
        <p className="text-[10px] text-gray-600 text-center mb-3 tracking-wider">꼭짓점을 탭해서 스탯 관리</p>
        <div
          className="w-full aspect-square rounded-[2rem] flex items-center justify-center"
          style={{
            background: 'linear-gradient(145deg, #0f1117, #0a0a0c)',
            border: '1px solid rgba(255,255,255,0.05)',
          }}
        >
          <StatRadarChart stats={stats.map(toChartStat)} />
        </div>
      </section>

      {/* 스탯 미니 진행바 */}
      <section className="mb-7 grid grid-cols-5 gap-2">
        {stats.map(stat => (
          <div key={stat.id} className="flex flex-col items-center gap-1.5">
            <span className="text-sm">{stat.icon}</span>
            <div className="w-full h-0.5 rounded-full bg-gray-800 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{ width: `${stat.score}%`, background: stat.color }}
              />
            </div>
            <span className="text-[10px] font-bold" style={{ color: stat.color }}>
              {Math.round(stat.score)}
            </span>
          </div>
        ))}
      </section>

      {/* 오늘의 루틴 */}
      <section className="space-y-3 pb-6">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">오늘의 루틴</h3>
          <span className="text-xs text-blue-400">{todayRoutines.length}개 예정</span>
        </div>

        {/* 다음 알림 */}
        {upcomingRoutine && (
          <div
            className="rounded-2xl p-4 flex gap-3 items-start"
            style={{ background: '#0f1117', border: '1px solid rgba(59,130,246,0.2)' }}
          >
            <div className="rounded-xl p-2 mt-0.5 shrink-0" style={{ background: 'rgba(59,130,246,0.1)' }}>
              <Bell size={15} className="text-blue-400" />
            </div>
            <div>
              <p className="text-[11px] text-gray-500 mb-0.5">오늘 {upcomingRoutine.notification_time}</p>
              <p className="text-sm font-semibold">
                <span className="text-blue-400">'{upcomingRoutine.name}'</span> 루틴 예정
              </p>
            </div>
          </div>
        )}

        {/* 스트릭 루틴들 */}
        {streakRoutines.map(routine => (
          <div
            key={routine.id}
            className="rounded-2xl p-4 flex items-center gap-3"
            style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.05)' }}
          >
            <div className="rounded-xl p-2 shrink-0" style={{ background: 'rgba(251,191,36,0.1)' }}>
              <Flame size={15} className="text-yellow-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">{routine.name}</p>
              <p className="text-[11px] text-gray-500">{routine.streak}일 연속 달성 중</p>
            </div>
            <ChevronRight size={15} className="text-gray-700 shrink-0" />
          </div>
        ))}

        {todayRoutines.length === 0 && (
          <p className="text-center text-gray-600 text-sm py-6">오늘 예정된 루틴이 없습니다</p>
        )}
      </section>

      {/* 경제/지식 패스 — 뉴스 카드 */}
      {news.length > 0 && (
        <section className="pb-24">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-300">오늘의 인사이트</h3>
            <span className="text-xs text-gray-600">자동 큐레이션</span>
          </div>
          <div className="space-y-2.5">
            {news.map((article, i) => (
              <a
                key={i}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-3 p-4 rounded-2xl transition-all active:scale-[0.98] block"
                style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.05)' }}
              >
                {/* 카테고리 아이콘 */}
                <div
                  className="rounded-xl p-2 mt-0.5 shrink-0"
                  style={{
                    background: article.category === 'economy'
                      ? 'rgba(34,197,94,0.1)' : 'rgba(168,85,247,0.1)',
                  }}
                >
                  {article.category === 'economy'
                    ? <TrendingUp size={14} className="text-green-400" />
                    : <BookOpen size={14} className="text-purple-400" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 mb-0.5">{article.source}</p>
                  <p className="text-sm font-medium leading-snug line-clamp-2">{article.title}</p>
                </div>
                <ExternalLink size={13} className="text-gray-700 shrink-0 mt-1" />
              </a>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

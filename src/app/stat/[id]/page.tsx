'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ChevronLeft, Plus, ChevronRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { statsAPI, categoriesAPI } from '@/lib/api';
import { rateColor } from '@/lib/utils';
import AddCategorySheet from '@/components/AddCategorySheet';

export default function StatDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [sheetOpen, setSheetOpen] = useState(false);

  const { data: stat, isLoading: statLoading } = useQuery({
    queryKey: ['stat', id],
    queryFn: () => statsAPI.getOne(id),
  });

  const { data: categories = [], isLoading: catLoading } = useQuery({
    queryKey: ['categories', id],
    queryFn: () => categoriesAPI.getByStat(id),
  });

  if (statLoading || catLoading) {
    return (
      <main className="min-h-screen bg-[#0a0a0c] flex items-center justify-center">
        <div className="text-gray-600 text-sm animate-pulse">Loading...</div>
      </main>
    );
  }

  if (!stat) {
    return (
      <main className="min-h-screen bg-[#0a0a0c] text-white flex items-center justify-center">
        <p className="text-gray-500">스탯을 찾을 수 없습니다.</p>
      </main>
    );
  }

  const totalRoutines = categories.reduce((s, c) => s + c.routine_count, 0);

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white px-5 pt-6">

      {/* 헤더 */}
      <header className="flex items-center gap-3 mb-8">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-xl"
          style={{ background: 'rgba(255,255,255,0.05)' }}
        >
          <ChevronLeft size={18} />
        </button>
        <div className="flex items-center gap-2">
          <span className="text-2xl">{stat.icon}</span>
          <h1 className="text-xl font-black">{stat.name}</h1>
        </div>
        <div
          className="ml-auto px-3 py-1 rounded-full text-sm font-bold"
          style={{ background: stat.color + '22', color: stat.color }}
        >
          {Math.round(stat.score)}점
        </div>
      </header>

      {/* 스탯 전체 진행도 */}
      <section className="mb-8 rounded-2xl p-5" style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm text-gray-400">전체 달성률</span>
          <span className="text-lg font-black" style={{ color: stat.color }}>{Math.round(stat.score)}%</span>
        </div>
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${stat.score}%`, background: `linear-gradient(to right, ${stat.color}88, ${stat.color})` }}
          />
        </div>
        <p className="text-xs text-gray-600 mt-2">총 {totalRoutines}개 루틴 운영 중</p>
      </section>

      {/* 카테고리 목록 (L2) */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-300">카테고리</h2>
          <button
            onClick={() => setSheetOpen(true)}
            className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-xl font-semibold"
            style={{ background: stat.color + '22', color: stat.color }}
          >
            <Plus size={13} />
            카테고리 추가
          </button>
        </div>

        <div className="space-y-3">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => router.push(`/stat/${id}/category/${cat.id}`)}
              className="w-full rounded-2xl p-4 flex items-center gap-4 text-left transition-all active:scale-[0.98]"
              style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.05)' }}
            >
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center text-xl shrink-0"
                style={{ background: stat.color + '18' }}
              >
                {cat.icon}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-sm">{cat.name}</span>
                  <span className="text-xs font-bold" style={{ color: rateColor(cat.weekly_rate) }}>
                    {cat.weekly_rate}%
                  </span>
                </div>
                <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${cat.weekly_rate}%`, background: rateColor(cat.weekly_rate) }}
                  />
                </div>
                <p className="text-[11px] text-gray-600 mt-1">{cat.routine_count}개 루틴</p>
              </div>

              <ChevronRight size={15} className="text-gray-700 shrink-0" />
            </button>
          ))}
        </div>
      </section>

      <AddCategorySheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        statId={id}
        statColor={stat.color}
      />
    </main>
  );
}

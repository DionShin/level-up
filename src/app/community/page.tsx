'use client';

import { useState } from 'react';
import { GitFork, Heart, Search } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { communityAPI, statsAPI, type CommunityRoutineResponse } from '@/lib/api';
import { formatFrequency } from '@/lib/utils';
import ForkModal from '@/components/ForkModal';

const ALL_TAGS = ['전체', '피부', '헬스', '독서', '경제', '자세', '루틴화'];

export default function CommunityPage() {
  const qc = useQueryClient();
  const [selectedTag, setSelectedTag] = useState('전체');
  const [forkTarget, setForkTarget] = useState<CommunityRoutineResponse | null>(null);
  const [likedIds, setLikedIds] = useState<Set<string>>(new Set());
  const [forkedIds, setForkedIds] = useState<Set<string>>(new Set());

  const { data: routines = [], isLoading } = useQuery({
    queryKey: ['community', selectedTag],
    queryFn: () => communityAPI.getAll(selectedTag),
  });

  const { data: stats = [] } = useQuery({
    queryKey: ['stats'],
    queryFn: statsAPI.getAll,
  });

  const likeMutation = useMutation({
    mutationFn: (id: string) => communityAPI.like(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['community'] }),
  });

  const handleLike = (id: string) => {
    if (likedIds.has(id)) return; // 한 번만 가능
    setLikedIds(prev => new Set(prev).add(id));
    likeMutation.mutate(id);
  };

  const getStat = (statId: string) => stats.find(s => s.id === statId);

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white px-5 pt-8">

      {/* 헤더 */}
      <header className="mb-6">
        <h1 className="text-xl font-black mb-1">커뮤니티 루틴</h1>
        <p className="text-xs text-gray-500">다른 유저의 루틴을 내 플랜으로 복제하세요</p>
      </header>

      {/* 검색바 (추후 기능) */}
      <div
        className="flex items-center gap-2 px-4 py-3 rounded-2xl mb-4"
        style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.06)' }}
      >
        <Search size={15} className="text-gray-600" />
        <span className="text-sm text-gray-600">루틴 검색...</span>
      </div>

      {/* 태그 필터 */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
        {ALL_TAGS.map(tag => (
          <button
            key={tag}
            onClick={() => setSelectedTag(tag)}
            className="shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-all"
            style={{
              background: selectedTag === tag ? '#3b82f6' : 'rgba(255,255,255,0.05)',
              color: selectedTag === tag ? '#fff' : '#6b7280',
            }}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* 로딩 */}
      {isLoading && (
        <div className="flex flex-col gap-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-48 rounded-2xl animate-pulse" style={{ background: '#0f1117' }} />
          ))}
        </div>
      )}

      {/* 루틴 카드 목록 */}
      <div className="space-y-4">
        {routines.map(routine => {
          const stat = getStat(routine.stat_id);
          const isForked = forkedIds.has(routine.id);
          const isLiked = likedIds.has(routine.id);

          return (
            <div
              key={routine.id}
              className="rounded-2xl p-5"
              style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.06)' }}
            >
              {/* 저자 + 스탯 뱃지 */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                    style={{ background: (stat?.color ?? '#3b82f6') + '22', color: stat?.color ?? '#3b82f6' }}
                  >
                    {routine.author_name[0]}
                  </div>
                  <div>
                    <p className="text-xs font-semibold">{routine.author_name}</p>
                    <p className="text-[10px] text-gray-600">Lv.{routine.author_level}</p>
                  </div>
                </div>
                <div
                  className="px-2 py-1 rounded-full text-[10px] font-semibold"
                  style={{ background: (stat?.color ?? '#3b82f6') + '18', color: stat?.color ?? '#3b82f6' }}
                >
                  {stat?.icon} {routine.category_name}
                </div>
              </div>

              {/* 루틴 정보 */}
              <h3 className="font-black text-base mb-1">{routine.routine_name}</h3>
              <p className="text-xs text-gray-500 mb-3 leading-relaxed">{routine.description}</p>

              {/* 메타 */}
              <div className="flex gap-2 mb-4 flex-wrap">
                <span
                  className="text-[11px] px-2.5 py-1 rounded-lg font-medium"
                  style={{ background: 'rgba(255,255,255,0.05)', color: '#9ca3af' }}
                >
                  {formatFrequency(routine.frequency, routine.days_of_week)}
                </span>
                {routine.notification_time && (
                  <span
                    className="text-[11px] px-2.5 py-1 rounded-lg font-medium"
                    style={{ background: 'rgba(255,255,255,0.05)', color: '#9ca3af' }}
                  >
                    🔔 {routine.notification_time}
                  </span>
                )}
              </div>

              {/* 태그 */}
              <div className="flex gap-1.5 mb-4 flex-wrap">
                {routine.tags.map(tag => (
                  <span
                    key={tag}
                    className="text-[10px] px-2 py-0.5 rounded-full"
                    style={{ background: 'rgba(255,255,255,0.04)', color: '#6b7280' }}
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* 포크 / 좋아요 */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    if (!isForked) setForkTarget(routine);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-95"
                  style={{
                    background: isForked ? (stat?.color ?? '#3b82f6') + '33' : 'rgba(255,255,255,0.05)',
                    color: isForked ? (stat?.color ?? '#3b82f6') : '#6b7280',
                    border: `1px solid ${isForked ? (stat?.color ?? '#3b82f6') + '44' : 'transparent'}`,
                  }}
                >
                  <GitFork size={14} />
                  {isForked ? '추가됨' : '내 플랜에 추가'}
                </button>

                <button
                  onClick={() => handleLike(routine.id)}
                  className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl transition-all active:scale-95"
                  style={{ background: 'rgba(255,255,255,0.05)' }}
                >
                  <Heart
                    size={14}
                    className={isLiked ? 'text-red-400 fill-red-400' : 'text-gray-600'}
                  />
                  <span className="text-xs text-gray-500">
                    {routine.like_count + (isLiked ? 1 : 0)}
                  </span>
                </button>

                <div className="flex items-center gap-1 px-2">
                  <GitFork size={12} className="text-gray-700" />
                  <span className="text-xs text-gray-600">
                    {routine.fork_count + (isForked ? 1 : 0)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 포킹 모달 */}
      <ForkModal
        routine={forkTarget}
        onClose={() => {
          // 포킹 성공 시 해당 루틴을 forkedIds에 추가
          if (forkTarget) setForkedIds(prev => new Set(prev).add(forkTarget.id));
          setForkTarget(null);
        }}
      />
    </main>
  );
}
